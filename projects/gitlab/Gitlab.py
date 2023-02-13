import sys
import re
import gitlab


class Gitlab:
    '''
    Access a GitLab instance via a personal access token and a URL.
    '''

    def __init__(self, pat, url="https://gitlab.com"):
        '''
        Initialize a GitLab instance.

        @param pat The Personal Access Token of the GitLab account to be accessed.
        @param url The URL of the GitLab instance to access.
        '''
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
        '''
        Return the groups accessible by this Gitlab object.
        '''
        return self.groups

    def fetch_groups_by_id(self, group_ids: list) -> list:
        '''
        Read GitLab groups by Group ID.

        @param group_ids a list of the groups to fetch by ID
        @returns a list of the groups that were fetched
        '''
        # select leading and trailing whitespace for trimming
        pattern = re.compile(r"^\s+|\s+$")

        # Read by id
        groups = []
        for x, id in enumerate(group_ids):
            # Skip empty list elements
            if (id < 1):
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

            groups.append(group)

        return groups

    def fetch_all_available_groups(self) -> list:
        '''
        Fetch all available groups accessible by this Gitlab instance. Call on init. Updates self.groups attribute.

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
        Adds a group to self.groups. Replace the group if it already exists.

        @param group the gitlab.Gitlab.group object
        '''

        # remove the existing group if it exists.
        for g in self.groups:
            if group['group_id'] == g['group_id']:
                sys.stdout.write(f"Duplicate group <id: {group['group_id']}> found. Replacing...")
                self.groups.remove(g)
                
        # add all group members
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

    def create_group(self, name, members=[]):
        '''
        Create a GitLab group 

        @returns The created group.
        '''

        self.gl.groups.create({'name': name, })
    
    def remove_group(self, group_id):
        '''
        Destroy a group by ID

        @param group_id the ID of the group to remove.
        '''

    def add_group_members(self, group, members):
        '''
        Add members to a group.

        @param group The group ID
        @param members The members to add
        '''
    
    def remove_group_members(self, group, members):
        '''
        Remove members from a group

        @param group The group ID
        @param members A list of members to remove. Members that can't be found will be skipped.
        '''