# GLADSync Utility

The **G**it**L**ab **A**ctive **D**irectory **Sync** Utility syncs GitLab groups with Active Directory groups. It is designed to be run on a schedule through `crontab` or a similar utility.

### Contents
- [Usage](#usage)
- [Methodology](#methodology)

## Usage
To setup this program, first install the necessary packages:
```bash
$ pip install -r requirements.txt
```

Then, create a `config.py` file in the same directory as [`gladsync.py`](./gladsync.py). It should contain configuration information in this format:
```py
# The URL of the GitLab instance to access
gl_url = 'https://gitlab.com'

# The personal access token used to access the GitLab instance
gl_pat = 'glpat-1234567890'

# The URL of the AD instance to access
ad_url = 'https://path.to.ad'

# The username and password to use when accessing AD
ad_user = 'foo'
ad_pass = 'bar'
```

### Schedule Run
Now, setup a `cron` job to run at an interval you designate:
```bash
$ crontab -e
```

```bash
# Edit this file to introduce tasks to be run by cron.
...
# m h  dom mon dow   command
* 4 * * * /usr/local/bin/python3 /home/foo/gladsync.py
```

In this example, the script will run every 4 hours. Change the path to your Python install and the script in the crontab editor as necessary.

### Command Line Options



## Methodology

### API Access

#### python-gitlab
The [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html) package is a wrapper around the [GitLab API](https://docs.gitlab.com/ee/api/rest/), which is used in this program to access and modify GitLab groups.

#### Active Directory API
The [Active Directory API](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0) is accessed directly using the [`requests`](https://pypi.org/project/requests/) library, and responses are parsed using the [`json`](https://docs.python.org/3/library/json.html) library.