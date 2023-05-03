# GLADSync Utility

**GLADSync** is the **G**it**L**ab **A**ctive **D**irectory **Sync** Utility. It modifies GitLab groups to match an Active Directory instance. GLADSync can either be run standalone or by a scheduling tool such as `crontab`. In scenarios where GitLab groups need to be regularly updated to match AD, GLADSync can be used to automate this process.

### Contents

- [Usage](#usage)
- [Methodology](#methodology)

---

## Usage

If all dependencies are installed, GLADSync can be run with the command:

```
$ python3 gladsync [OPTIONS]
```

See [the available command line options below](#command-line-options).

If requirements need to be installed, follow the steps below:

### First-time Setup

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

# The base distinguished name to be used for LDAP searches.
ldap_base: 'OU=Project Groups,OU=Groups,DC=ad,DC=iti,DC=lab'

# A semicolon (;) separated list distinguished names of the groups to sync.
ldap_sync_groups: 'OU=Project Groups,OU=Groups,DC=ad,DC=iti,DC=lab,CN=foo;OU=Project Groups,OU=Groups,DC=ad,DC=iti,DC=lab,CN=bar'

# The access level to give to each person added to a GitLab group
# Must be one of: [GUEST, REPORTER, DEVELOPER, MAINTAINER, OWNER]
access_level: "developer"

# The log file to write to. If no path is given, print to standard out.
log_file: "./logs/gladsync-YYYMMDD.log"
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

```bash
*                     -config.file      PATH  The config file to use. [default: None] [required]
--test                -T                      Test mode. Print expected changes but make no modifications. [default: True]
--verbose             -v                      Verbose. Print extra information while running.
--create_groups       -c                      Create GitLab groups that are found in AD but not GitLab.
--no-print            -p                      Print logs to standard out. [default: True]
--help                                        Show this message and exit.
```

The `-config.file` option is required. Provide it the path to a config file as described above.

## Methodology

Below are the main libraries/packages/APIs used. For more specific information about the implementation, see the [GLADSync Reference](./gladsync/README.md).

### CLI

The [Typer](https://typer.tiangolo.com/) library allows for easy CLI implementation based Python's built-in type hints. You can see how it is used in [`./gladsync/main.py`](./gladsync/main.py).

### API Access

#### python-gitlab

The [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) package is a wrapper around the [GitLab API](https://docs.gitlab.com/ee/api/rest/), which is used in this program to access and modify GitLab groups. It can be used to get and post information about your GitLab instance's groups, users, projects, and other GitLab elements. In this case, it is used to read and modify groups to match AD.

#### ldap3

The [`ldap3`](https://ldap3.readthedocs.io/en/latest/index.html) package allows for LDAP communication, used here to access Active Directory groups and members. While it can be used to get and post information from an LDAP service, it only used here to read data.
