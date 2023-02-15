# Gitlab.py

The `Gitlab` class contains methods for accessing and updating GitLab groups by interfacing with the GitLab API using the [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) package.

## Attributes
### `self.gl`
The `gitlab.Gitlab` [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) instance initialized by this object.

### `self.groups`
The list of groups that are accessible to this GitLab instance.

Groups are stored in the following format:
```py
self.groups = 
[
    {
        'group_name': 'group1',
        'group_id': 12345678, 
        'object': <Group id:12345678 name:group1>,
        'members': [
            {'username': 'user1', 'user_id': 12345678},
            {'username': 'user2', 'user_id': 23456789}
        ]
    },
    {
        'group_name': 'group2', 
        ...
    }
]
```
- `group_name`: the name of this group
- `group_id`: this group's unique ID, assigned by GitLab
- `object`: the `gitlab.Gitlab.Group` object that represents this group
- `members`: a list of dicts, each representing a unique user
    - `username`: this user's username
    - `user_id`: this user's unique ID, assigned by GitLab

Since execution time and storage capacity aren't (realistically) limiting factors, this format for the `groups` list allows for easy access to name, ID, and members in a human-readable format while still retaining the `object` that can be used to access further information or perform operations on the group.

## Reference
### `Gitlab(pat, url="https://gitlab.com")`
Initialize a Gitlab instance.

Parameters:
- `pat` - the Personal Access Token of the GitLab account to be accessed.
- `url` - the URL of the GitLab instance to be accessed. Defaults to https://gitlab.com.

### `.get_gl()`
Return the `gitlab.Gitlab` instance that represents the connection to GitLab.

Return: [`self.gl`](#selfgl) (`gitlab.Gitlab`)

### `.get_groups()`
Return the list of accessible groups stored in the [`self.groups`](#selfgroups) attribute.

Return: [`self.groups`](#selfgroups) (`list`)

### `.sync_groups()`
Fetch all available groups accessible by this `Gitlab` instance and update this object's [`self.groups`](#selfgroups) attribute with the retrieved groups.

This method is called on `__init__` to populate [`self.groups`](#selfgroups) with the available remote groups.

### `.create_group(name, path, members=[])`
Create a remote GitLab group. Top-level groups are not currently allowed by the GitLab API, so a path to a parent group is required.

Parameters:
- `name` - The name of the group.
- `path` - The path to the parent group.
- `members` - A list of the members to add to the group upon creation. Defaults to none.

Return: A `gitlab.Gitlab.Group` object representing the created group.

### `.remove_group(group_id=None, group_name=None)`
Remove a GitLab group by name or id. Either `group_id` or `group_name` must be provided. If both are provided, attempt to remove by `group_id` first, then by `group_name`.

Parameters:
- `group_id` - The ID of the group to be removed.
- `group_name` - The name of the group to be removed.

### `.add_group_members(group_id, group_name, members)`
Add members to a group 