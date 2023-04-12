import json
import logging
import sys

import gitlab
import ldap
import requests
from config import Config


class GladSync:
    def __init__(self, config: Config, test: bool, delete: bool, skip_ad: bool):
        """
        The GitLab Active Directory Sync utility.
        Contains all program logic, called by main() in ./main.py.

        Args:
            config  (Config) : a config.Config object containing parsed config data.
            test    (bool)   : Enable/disable test/print-only mode.
            delete  (bool)   : Enable/disable group/member deletion.
        """
        # root logger should already be setup from config.
        self.log = logging.getLogger()
        self.log.info('Gladsync started')

        # gitlab auth may not be provided in test mode, so set blank defaults
        gl = None
        gl_groups = None
        parent_group = None

        # create the Gitlab object
        try:
            gl = gitlab.Gitlab(url=str(config.gl_url),
                               private_token=str(config.gl_pat))
            self.log.debug(f"GitLab instance accessed: {config.gl_url}")
        except Exception as e:
            if test:
                self.log.warning(
                    f"(test) GitLab instance cannot be accessed.")
                self.log.debug(e)
            else:
                self.log.error(
                    f"GitLab instance cannot be accessed. Given: \n\tgl_url: {config.gl_url}\n\tgl_pat: {config.gl_pat}")
                sys.exit()

        # fetch all groups
        try:
            gl_groups = gl.groups.list()
            self.log.debug(f"Groups fetched: {len(gl_groups)}")
        except Exception as e:
            if test:
                self.log.warning(
                    f"(test) Cannot fetch groups. GitLab Authentication Error.")
                self.log.debug(e)
            else:
                self.log.error(
                    f"Cannot fetch groups. GitLab Authentication Error.")
                self.log.debug(e)
                sys.exit()

        # fetch parent group
        try:
            # GitLab API only allows for edits in subgroups, so a parent group needs to be given
            parent_group = gl.groups.get(id=config.gl_root)
            self.log.debug(f"Root group fetched: {parent_group.name} ({parent_group.id})")
        except Exception as e:
            if test:
                self.log.warning(
                    f"(test) Root group could not be fetched.")
                self.log.debug(e)
            else:
                self.log.error(
                    f"Root group {config.gl_root} could not be fetched.")
                self.log.debug(e)
                sys.exit()

        if not skip_ad:
            # Create AD session and fetch groups
            try:
                s = requests.Session()
                s.auth = (config.ad_user, config.ad_pass)
                self.log.debug(f"AD Session started: {config.ad_url}")
            except Exception as e:
                self.log.error(f"AD Session could not be started.")
                self.log.debug(e)
                sys.exit()

            try:
                ad_groups_response = s.get(config.ad_url + '/api/groups')
                ad_groups = json.loads(ad_groups_response.text)['value']
                self.log.debug(f"AD groups fetched: {len(ad_groups)}")
            except Exception as e:
                self.log.error(f"AD groups could not be fetched.")
                self.log.debug(e)
                sys.exit()

            self.session = s
            self.ad_groups = ad_groups

        # gl, gl_groups, parent_group will be None if in test AND gl auth not provided in config/not working.
        self.gl = gl
        self.gl_groups = gl_groups
        self.parent_group = parent_group

        # inherited options
        self.test = test
        self.delete = delete

        if skip_ad:
            self.test_print()
        else:
            # start the main program loop
            self.sync_groups()

        self.log.info('Gladsync complete!')

    def sync_groups(self):
        """
        Create, update, or delete GitLab groups to match AD. This is the app's main program loop.
        """
        # check that all ad_groups are in gl
        for ad_group in self.ad_groups:
            # compare to gl groups
            ad_group_name = ad_group['displayName'].lower()

            # search for a match
            # skip finding a match if GitLab was never accessed
            if self.gl:
                match_found = False
                for gl_group in self.gl_groups:
                    if gl_group.name.lower() == ad_group_name:
                        # sync members if names match
                        self.sync_members(ad_group, gl_group)
                        match_found = True
                        break

                # create a new group if no match is found
                if not match_found:
                    self.create_group(ad_group)
            elif self.test:
                # this _should_ only execute in test mode, even without the `elif`,
                # since failing to start self.gl should exit the program. elif there just for safety.

                # since we're in test, run self.create_group() to print info about groups that would be created.
                for group in self.ad_groups:
                    self.create_group(group)
            else:
                # this should never execute, so throw an error and exit if we get here.
                self.log.error(
                    f"Hmm... not sure how this happened. Could not sync_groups().\nself.gl: <{self.gl}>, self.test: <{self.test}>")
                sys.exit()

        # Now, groups that are not in AD can be removed from GitLab.
        ad_group_names = [g['displayName'].lower() for g in self.ad_groups]
        if self.gl:
            for gl_group in self.gl_groups:
                if gl_group.name.lower() not in ad_group_names:
                    if self.test:
                        self.log.info(
                            f"(test) Group would be removed: <{gl_group.name}, {gl_group.id}>")
                    else:
                        if self.delete:
                            gl_group.remove()
                        else:
                            self.log.info(
                                f"(delete) Group would be removed: <{gl_group.name}, {gl_group.id}>")
        elif self.test:
            # same as the above block, this should only execute when in test and gl could not be accessed.
            self.log.info(
                f"(test) No self.gl instance found. Could not remove groups.")
        else:
            # again, this should never execute
            self.log.error(
                f"Hmm... not sure how this happened. Could not remove groups.\nself.gl: <{self.gl}>, self.test: <{self.test}>")
            sys.exit()

    def sync_members(self, ad_group, gl_group):
        """
        Sync the members between an AD and GL group.
        Read AD group members. Add and remove members from the gl_group to match.
        If in test mode, instead print members that would be added or removed.

        Args:
            ad_group : a JSON object representing the AD group.
            gl_group : a gitlab.Gitlab.Group object.
        """
        # get group members
        try:
            ad_members_response = self.session.get(
                self.config.ad_url + '/api/groups/' + ad_group['id'] + '/members')
        except Exception as e:
            self.log.warning(
                f"AD group <{ad_group['displayName']}, {ad_group['id']}> members could not be fetched.")
            self.log.debug(e)
            return

        # load member data from json
        try:
            ad_members = json.loads(ad_members_response.text)['value']
        except Exception as e:
            self.log.warning(
                f"AD group <{ad_group['displayName']}, {ad_group['id']}> members could not be loaded from json.")
            self.log.debug(e)
            self.log.debug(f"\tJSON: {ad_members_response.text}")

        # remove gl_group_members that are not in ad_group
        ad_member_names = [m['displayName'].lower() for m in ad_members]
        gl_group_members = gl_group.members.list()
        for gl_member in gl_group_members:
            # check display names against each other (not username)
            if gl_member.name.lower() not in ad_member_names:
                # gl_group_members is the local list
                gl_group_members.remove(gl_member)
                if self.test:
                    self.log.info(
                        f"(test) GitLab group <{gl_group.name}, {gl_group.id}> member <{gl_member.name}, {gl_member.id}> would be deleted.")
                else:
                    if self.delete:
                        gl_member.delete()
                    else:
                        self.log.info(
                            f"(delete) GitLab group <{gl_group.name}, {gl_group.id}> member <{gl_member.name}, {gl_member.id}> would be deleted.")

        # add members that are in the ad_group but not gitlab
        gl_member_names = [m.name.lower() for m in gl_group_members]
        gl_all_members = self.parent_group.members_all.list(get_all=True)
        for ad_member in ad_members:
            # for each member, check if they are in the gl group already
            ad_name = ad_member['displayName'].lower()
            if ad_name not in gl_member_names:
                # add user to group if they already have an account that exists in one of the subgroups
                match_found = False
                for gl_mem in gl_all_members:
                    if ad_name == gl_mem.name.lower():
                        # if a match is found, add the member to the gitlab group
                        create_member = {
                            'user_id': gl_mem.user_id,
                            'access_level': self.config.access_level
                        }
                        if self.test:
                            self.log.info(
                                f"(test) Member {create_member} would be added to GitLab group <{gl_group.name}, {gl_group.id}>.")
                        else:
                            try:
                                gl_group.members.create(create_member)
                            except Exception as e:
                                self.log.warning(
                                    f"Member {create_member} could not be added to GitLab group <{gl_group.name}, {gl_group.id}>.")
                                self.log.debug(e)
                            match_found = True
                            break

                # if no match is found, send invite email based on the info in AD.
                if not match_found:
                    if self.test:
                        self.log.info(
                            f"(test) Invite email would be sent for member <{ad_member['displayName']}, {ad_member['id']}, {ad_member['mail']}> to group <{gl_group.name}, {gl_group.id}>.")
                    else:
                        try:
                            gl_group.invitations.update(
                                ad_member['mail'],
                                {'access_level': self.config.access_level}
                            )
                        except Exception as e:
                            self.log.warning(
                                f"Invite email could not be sent for member <{ad_member['displayName']}, {ad_member['id']}, {ad_member['mail']}> to group <{gl_group.name}, {gl_group.id}>.")
                            self.log.debug(e)

    def create_group(self, ad_group):
        """
        Create a GitLab group with the members from the given ad_group. Top-level groups cannot be created (as a restriction of the GitLab API), so the parent_group is used.

        @param ad_group the AD group to copy to GitLab
        """
        parent_group = self.parent_group.id if self.parent_group else "<No gl_root Group>"

        gl_group = {
            'name': ad_group['displayName'],
            'path': ad_group['displayName'],
            'parent_group': parent_group
        }

        if self.test:
            self.log.info(f"(test) Would create group: {gl_group}")
        else:
            try:
                gl_group = self.gl.groups.create(gl_group)
            except Exception as e:
                self.log.error(
                    f"GitLab group {gl_group} could not be created.")
                self.log.debug(e)
                sys.exit()

        # use sync_members to add correct group members
        self.sync_members(ad_group, gl_group)

    def test_print(self):
        """
        TODO REMOVE THIS, only called when skip_ad is true
        check gitlab for all groups and members. Print all.
        """
        groups = self.gl_groups
        gr = []
        for g in groups:
            gr.append(f"<Group {g.id} '{g.name}', parent: {g.parent_id}>")
        members = self.parent_group.members_all.list(get_all=True)
        self.log.info(
            f"\nParent: {self.parent_group}\n\nGroups: {gr}\n\nMembers: {members}")
        sys.exit()
