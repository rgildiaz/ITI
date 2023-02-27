import sys
import gitlab
import requests
import json
import typer
from pathlib import Path
from config import Config

# TODO test/print only mode

# The CLI app
app = typer.Typer(
    # Disable local vars showing in error messages
    pretty_exceptions_show_locals=False
)

# this is the CLI's entry point
@app.command()
def main(
    config_path: Path = typer.Option(
        ...,    # make this required by passing no default value
        "-config.file",
        help="The config file to use."
    ),
    test: bool = typer.Option(
        True,   # On by default
        "--test",
        "-T",
        help="Test mode. Print expected changes but make no modifications."
    ),
    verbose: bool = typer.Option(
        True,   # TODO turn this off, on for testing
        "--verbose",
        "-v",
        help="Verbose. Print extra information while running."
    )
    # TODO override options
    # gl_url: str = typer.Option(
    #     None,
    #     help="Override the config file's gitlab URL"
    # )
):
    '''
    Sync AD groups to GitLab!\n
    Fetches groups from AD and creates/modifies GitLab groups to match.\n
    A .yaml config file must be provided with the -config.file option. See `./gladsync/example_config.yaml`.
    '''
    config = Config(config_path, test, verbose)
    # all program logic is contained in the GladSync object
    GladSync(config, test, verbose)


class GladSync:
    def __init__(self, config : Config, test: bool, verbose: bool):
        '''
        The GitLab Active Directory Sync utility. 
        Contains all program logic, called by main() in CLI.

        Args:
            config (Config) : a config.Config object containing parsed config data
            test (bool) : Enable/disable test/print-only mode.
            verbose (bool) : Enable/disable verbose logging.
        '''
        try:
            gl = gitlab.Gitlab(config.gl_url, config.gl_pat)
        except Exception as e:
            sys.exit(f"\nGitLab instance cannot be accessed. Given: \n\tgl_url: {config.gl_url}\n\tgl_pat: {config.gl_pat}")
            
        gl_groups = gl.groups.list()
        # GitLab API only allows for edits in sub-groups, so a parent group needs to be given
        # set first group as parent for now
        parent_group = gl_groups[0]
        # remove the parent group from this list to prevent accidental removal
        gl_groups = gl_groups.remove(parent_group)

        # a session is required for AD API
        s = requests.Session()
        s.auth = (config.ad_user, config.ad_pass)

        ad_groups_response = s.get(config.ad_url + '/api/groups')
        ad_groups = json.loads(ad_groups_response.text)['value']

        self.gl = gl
        self.gl_groups = gl_groups
        self.parent_group = parent_group
        self.session = s
        self.ad_groups = ad_groups
        self.test = test

        # start the main program loop
        self.sync_groups()
    
    def sync_groups(self):
        # check that all ad_groups are in gl
        for ad_group in self.ad_groups:
            # compare to gl groups
            ad_group_name = ad_group['displayName'].lower()

            match_found = False
            for gl_group in self.gl_groups:
                if gl_group.name.lower() == ad_group_name:
                    # check members if names match
                    sync_members(s, ad_group, gl_group)
                    match_found = True
                    break

            # create a new group if no match is found
            if not match_found:
                create_group(ad_group)

        # # remove groups that are in gl but not ad
        # ad_group_names = [g['displayName'].lower() for g in ad_groups]
        # for gl_group in gl_groups:
        #     if gl_group.name.lower() not in ad_group_names:
        #         gl_group.remove()

def sync_members(s, ad_group, gl_group, parent_group, config : Config, test : bool):
    '''
    Sync the members between an AD and GL group. 
    Read AD group members. Add and remove members from the gl_group to match.

    Args:
        ad_group : a JSON object representing the AD group.
        gl_group : a gitlab.Gitlab.Group object.
        config (Config) : a config.Config object containing parsed config data.
        test (bool) : Enable/disable test (print only) mode.
    '''
    ad_members_response = s.get(
        config.ad_url + '/api/groups/' + ad_group['id'] + '/members')
    ad_members = json.loads(ad_members_response.text)['value']
    # get member names list for use later
    ad_member_names = [m['displayName'].lower() for m in ad_members]

    gl_members = gl_group.members.list()

    # remove gl_members that are not in ad_group
    for gl_member in gl_members:
        # check display names against each other (not username)
        if gl_member.name.lower() not in ad_member_names:
            gl_member.delete()
            gl_members.remove(gl_member)    # gl_members is the local list

    # add members that are in the ad_group but not gitlab
    gl_member_names = [m.name.lower() for m in gl_members]
    gl_all_members = parent_group.members_all.list(get_all=True)
    for ad_member in ad_members:
        ad_name = ad_member['displayName'].lower()
        if ad_name not in gl_member_names:
            # add user to group if they already have an account that exists in one of the subgroups
            match_found = False
            for gl_mem in gl_all_members:
                if ad_name == gl_mem.name.lower():
                    gl_group.members.create({
                        'user_id': gl_mem.user_id,
                        'access_level': config.access_level
                    })
                    match_found = True
                    break

            # if no match is found, send invite email based on the info in AD.
            if not match_found:
                gl_group.invitations.update(
                    ad_member['mail'],
                    {'access_level': ACCESS_LEVEL}
                )


def create_group(ad_group):
    '''
    Create a GitLab group with the members from the given ad_group. Top-level groups cannot be created (as a restriction of the GitLab API), so the parent_group is used.

    @param ad_group the AD group to copy to GitLab
    '''
    gl_group = gl.groups.create({
        'name': ad_group['displayName'],
        'path': ad_group['displayName'],
        'parent_group': parent_group.id
    })

    # use sync_members to add correct group members
    sync_members(ad_group, gl_group)


if __name__ == "__main__":
    app()
