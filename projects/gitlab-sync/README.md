# GLADSync Utility

The **G**it**L**ab **A**ctive **D**irectory **Sync** Utility syncs GitLab groups with Active Directory groups. It can either be run standalone or by a scheduling tool such as `crontab`.

### Contents

- [Usage](#usage)
- [Methodology](#methodology)

## Usage

First, install the necessary packages:

```bash
$ pip install -r requirements.txt
```

GLADSync requires some configuration information in order to work. Create a `.yaml` config file in the same format as [`./gladsync/example_config.yaml`](./gladsync/example_config.yaml):

```yaml
# The URL of the GitLab instance to access
gl_url: "gitlab.com"

# The personal access token to use when accessing gitlab
gl_pat: "glpat-1234567890"

# The ID of the gitlab group to create newly-synced groups within
# The GitLab API disallows the creation of top-level groups
gl_root: "64497189"

# The URL to your Active Directory instance
ad_url: "path.to.ad"

# The username and password to use when accessing Active Directory
ad_user: "foo"
ad_pass: "bar"

# The access level to give to each person added to a GitLab group
# Must be one of: [GUEST, REPORTER, DEVELOPER, MAINTAINER, OWNER]
# Defaults to DEVELOPER
access_level: "developer"

# The log file to write to. If no path is given, print to standard out.
log_file: './logs/gladsync-YYYMMDD.log'
```

Now, GLADSync can be run standalone:

```bash
$ python3 gladsync -config.file config.yaml
```

### Schedule Run

Alternatively, a `cron` job can be setup to run at a regular interval:

```bash
$ crontab -e
```

```bash
# Edit this file to introduce tasks to be run by cron.
...
# m h  dom mon dow   command
* 4 * * * /usr/local/bin/python3 /home/gladsync -config.file /home/config.yaml
```

In this example, the script will run every 4 hours. Change the given paths as necessary.

### Command Line Options

The `-config.file` option is required. Provide it the path to a config file as described above.

```
-config.file                PATH    The config file to use. [default: None] [required]
--test        -T                    Test mode. Print expected changes but make no modifications. [default: True]
--verbose     -v                    Verbose. Print extra information while running. [default: True]
--delete      --no-delete           Delete GitLab groups and members as necessary. Otherwise, print expected changes but make no modifications. [default: delete]
--help                              Show this message and exit.
```

## Methodology

Below are the main libraries/packages/APIs used. For more specific information about the implementation, see the [GLADSync Reference](./gladsync/README.md).

### CLI

The [Typer](https://typer.tiangolo.com/) library allows for easy CLI implementation based Python's built-in type hints. You can see how it is used in [`./gladsync/main.py`](./gladsync/main.py).

### API Access

#### python-gitlab

The [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) package is a wrapper around the [GitLab API](https://docs.gitlab.com/ee/api/rest/), which is used in this program to access and modify GitLab groups.

#### Active Directory API

The [Active Directory API](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0) is accessed directly using the [`requests`](https://pypi.org/project/requests/) library, and responses are parsed using the [`json`](https://docs.python.org/3/library/json.html) library.
