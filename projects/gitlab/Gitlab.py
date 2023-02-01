import sys
import re
import gitlab


class Gitlab:
    '''
    Access a GitLab instance.

    @param pat The Personal Access Token of the GitLab account to be accessed.
    @param url The URL of the GitLab instance to access.
    '''

    def __init__(self, pat, url="https://gitlab.com"):
        self.gl = gitlab.Gitlab(url, private_token=pat)
        self.groups = []
        # fetch all available groups on startup. mutates self.groups
        self.fetch_all_available_groups()

    def get_gl(self):
        '''
        Return the python-gitlab API object.
        '''
        return self.gl

    def get_groups(self):
        return self.groups

    def fetch_groups_by_id(self, group_ids: list) -> list:
        '''
        Read GitLab groups by Group ID.
        TODO read by group name

        @param group_ids a list of the groups to fetch by ID
        @returns a list of the groups that were fetched
        '''
        # select leading and trailing whitespace for trimming
        pattern = re.compile(r"^\s+|\s+$")

        # Read by id
        groups = []
        for x, id in enumerate(group_ids):
            # Skip empty list elements
            if (id < 1) or ():
                sys.stdout.write(
                    f"Invalid Group ID <{id}> found at index {x}. Skipping..."
                )
                continue

            # Catch invalid IDs
            try:
                group = self.gl.groups.get(id)
            except Exception as e:
                sys.stdout.write(
                    f"Invalid Group ID <{id}> found at index {x}. Skipping...",
                    e
                )
                continue

            self.create_group_entry(group)

        self.groups = groups
        return groups

    def fetch_all_available_groups(self) -> list:
        '''
        Fetch all available groups that this Gitlab instance can access.

        @returns a list of all groups
        '''
        groups_list = []

        try:
            groups_list = self.gl.groups.list()
        except Exception as e:
            sys.stdout.write(f"Could not fetch groups:", e)

        for group in groups_list:
            self.create_group_entry(group)

        return groups_list

    def create_group_entry(self, group) -> None:
        '''
        Adds a group to self.groups

        @param group the gitlab.Gitlab.group object
        '''
        members = []
        for member in group.members.list():
            members.append({
                'username': member.username,
                'user_id': member.id,
            })

        self.groups.append({
            'group_name': group.name,
            'group_id': group.id,
            'members': members,
        })
