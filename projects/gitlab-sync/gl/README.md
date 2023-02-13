# Gitlab.py

The `Gitlab` class contains methods for accessing and updating GitLab groups by interfacing with the GitLab API through the [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) package.

## Attributes
### `self.gl`
The `gitlab.Gitlab` [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) instance initialized by this object.

### `self.groups`
The list of groups that are accessible to this GitLab instance.

Groups are stored in the following format:
```py
self.groups = [
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

## Methods
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

Return: `self.groups` (`list`)