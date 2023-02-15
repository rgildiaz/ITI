import sys
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
        self.sync_groups()

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

    # remove this?
    def fetch_groups_by_id(self, group_ids: list) -> list:
        '''
        NOT NEEDED
        Read GitLab groups by Group ID.

        @param group_ids a list of the groups to fetch by ID
        @returns a list of the groups that were fetched
        '''
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

    def sync_groups(self) -> list:
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
            self._create_group_entry(group)

        return groups_list

    def _create_group_entry(self, group) -> None:
        '''
        Adds a group to self.groups. Replace the group if it already exists.

        @param group the gitlab.Gitlab.group object
        '''

        # remove the existing group if it exists.
        for g in self.groups:
            if group.id == g['group_id']:
                sys.stdout.write(
                    f"Duplicate group <id: {group.id}> found. Replacing...")
                self.groups.remove(g)

        # add all group members
        members = []
        for member in group.members.list():
            members.append({
                'username': member.username,
                'user_id': member.id
            })

        self.groups.append({
            'group_name': group.name,
            'group_id': group.id,
            'object': group,
            'members': members,
        })

    def create_group(self, name: str, path: str, parent_id: int, members: list = []):
        '''
        Create a GitLab group.
        Members list should be formatted 
        Top-level groups are not currently allowed by the GitLab API, so a path to a parent group is required.

        @param name The group name
        @param path The path to the group
        @param parent_id The parent group's ID
        @param members <optional> The members to include in the group

        @returns The created group.
        '''

        group = {'name': name, 'path': path, 'parent_id': parent_id}

        return self.gl.groups.create(group)

    def remove_group(self, group_obj=None, group_id=None, group_name=None):
        '''
        Destroy a group by object, ID, or name. Either a `group_obj`, `group_id`, or a `group_name` must be provided. If all are provided, attempt them in order.

        @param group_id the ID of the group to remove.
        @param group_name the name of the group to remove.
        '''
        if group_obj:
            print(f"group_obj found: <{group_obj.id}>. Removing...")
            group_obj.delete()
        elif group_id:
            self.gl.groups.delete(group_id)
        elif group_name:
            for g in self.groups:
                if g['name'].strip() == group_name.strip():
                    self.gl.groups.delete(g['group_id'])
        else:
            sys.out.write(
                f"Group not found. Provided: \ngroup_obj: <{group_obj.id}> \ngroup_id: <{group_id}> \n group_name: <{group_name}>")

    def add_group_members(self, members: list, group_id: int = None, group_name: str = None):
        '''
        Add members to a group.

        @param group_id The group ID
        @param group_name The group name
        @param members A list of members to add
        '''

        # validate requested members

        group = None

        if group_id:
            for g in self.groups:
                if g['group_id'] == group_id:
                    group = g
                    break
        elif group_name:
            for g in self.groups:
                if g['name'].strip() == group_name.strip():
                    group = g
                    break
        else:
            # error
            pass

        for m in members:
            group['object'].create({'user_id': m['user_id']})

    def remove_group_members(self, members, group_id=None, group_name=None):
        '''
        Remove members from a group.

        @param group The group ID
        @param members A list of members to remove. Members that can't be found will be skipped.
        '''
