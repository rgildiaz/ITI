# GLADSync Reference

This document will walk through my thinking about the design of some of the program components, intended to make future maintenance and changes easier. For a more general overview of the program and how to use it, refer to [the `README` in the parent folder](../README.md).

The GLADSync package is split into three major components:

- [`main.py`](#mainpy) is the main entry-point for the CLI.
- [`gladsync.py`](#gladsyncpy) contains the actual program logic.
- [`config.py`](#configpy) is a helper for parsing config files.

It additionally contains some "helper" files:

- [`example_config.yaml`](#app-configuration), which is a starter config file.
- [this `README`](./README.md)!

## [`main.py`](./main.py)

`main.py` initializes the [Typer](#typer) app and provides it an entry-point through the [`main()`](#main) function.

### `main(config_path, test, verbose, std_out)`

Define the app's command line options and create a [`Config`](#config) and [`GladSync`](#gladsync) object.

Typer works with built-in type hints. By setting the default value of this functions parameters to `typer.Option()` objects, default values, required options, and help text can be set. The `@app.command()` decorator is required for `main()` to be recognized as a CLI command.

Args:

- `config_path` (`str`) - the path to a .yaml config file to use. This is a **required** CLI option.
- `test` (`bool`) - whether or not to use "test" mode. In test mode, log changes that would be made, but make no actual modifications. Default: `True`
- `verbose` (`bool`) - whether or not to use verbose logging. Default: `False`
- `std_out` (`bool`) - whether or not to print logs to std_out. Default: `True`

Typer also (helpfully) auto-generates text for the `--help` CLI option, based on the `help=` arguments within the `typer.Option()` definitions, as well as the docstring within the body of `main()`.

The flow of the program can also be more easily seen in `main()`, as it first collects these arguments, then creates a [`config.Config()`](#config) to parse the config file, and finally runs [`gladsync.Gladsync()`](#gladsync) to complete the program logic.

## [`gladsync.py`](./gladsync.py)

`gladsync.py` contains the main functionality and program logic of the app. Using data given by the app's [configuration](#configpy), [`GladSync`](#gladsync) calls the [GitLab](#python-gitlab) and [Active Directory](../README.md#ldap3) APIs. It fetches available groups from the specified Active Directory instance, and then ([optionally](#mainconfig_path-test-verbose)) modifies the given GitLab instance to match.

### `GladSync`

When created, the GladSync object fetches the root logger, which should have been setup by [`config.py`](#configpy). It also attempts to connect to GitLab and AD. GladSync should log any connections that can't be established, but should only exit on fatal errors.

In general, GladSync follows this flow:

- Establish a connection to GitLab and AD using the provided config information
- For each AD group, look for a GitLab group with the same name.
  - If a group is found, check that all members in the AD group are present in GitLab. Add any members necessary.
  - If a group is not found, create one and populate it with the necessary members.

A `GladSync` object is created by [`main.py`](#mainconfig_path-test-verbose-delete).

While the same functionality could be achieved with a simpler script format, I chose this object-oriented approach since it allows for easier development and maintenance down the road.

## [`config.py`](./config.py)

### `Config`

the `Config` class parses the `.yaml` config file that is given by the `-config.file` command line option. It is called by [`GladSync`](#gladsync) on startup. I chose to use this pattern in part because of [Grafana Loki's configuration](https://grafana.com/docs/loki/latest/configuration/), which uses `.yaml` configs and the `-config.file` CLI option. YAML is also easy to read and write, and is a common configuration format.

I wanted the Config utility to be dynamic, adjusting to new requirements and config options on the fly. By creating a list of default config options and overwriting these with parsed options read in from the YAML config, a list of all config options can be created. Iterating over this list allows for checking of required options (if the default option is blank and the parsed config entry is missing, an error can be thrown) and for the dynamic setting of new options (using the `setattr()` function). This approach also implicitly ignores any provided configs which have not been defined by the developer. To add a new config option, a new key must be added to the `defaults` dictionary, found at the top of [`config.py`](./config.py).

### App Configuration

A starter configuration file can be found at [`./example_config.yaml`](./example_config.yaml). The current config options are:
```yaml
# The URL to your GitLab instance. 
gl_url: 'https://gitlab.com'

# The personal access token to use when accessing GitLab
gl_pat: ''

# The ID of the group to create all new synced groups under
# The GitLab API disallows creation of top-level groups
gl_root: ''

# The URL to your Active Directory instance
ad_url: ''

# The username to use when accessing Active Directory
ad_user: ''

# The password to use when accessing Active Directory.
ad_pass: ''

# The base distinguished name to be used for LDAP searches.
ldap_base: 'OU=Project Groups,OU=Groups,DC=ad,DC=iti,DC=lab'

# A semicolon (;) separated list distinguished names of the groups to sync.
ldap_sync_groups: ''

# The access level to give to each person added to a GitLab group
# Must be one of: [GUEST, REPORTER, DEVELOPER, MAINTAINER, OWNER]
access_level: 'DEVELOPER'

# The log file to write to.
# If no path is given, print to stdout.
log_file: ''

```

## Dependencies

### [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html)

The `python-gitlab` package provides a Python wrapper for the GitLab API. It is used in [`gladsync.py`](./gladsync.py) to connect and modify a GitLab instance.

### [`ldap3`](https://ldap3.readthedocs.io/en/latest/index.html)

The `ldap3` package provides LDAP functionality for Python. It is used in [`gladsync.py`](./gladsync.py) to read data from the Active Directory instance.

### [Typer](https://typer.tiangolo.com/)

The Typer framework allows for easier CLI creation in Python. It is used in [`main.py`](./main.py) to generate the actual CLI functionality, such as writing help text and configuring CLI options.

### Other

- [`logging`](https://docs.python.org/3/library/logging.html) is used for log messages.
- [`pathlib`](https://docs.python.org/3/library/pathlib.html) is used to parse config file paths.
- [`PyYAML`](https://pyyaml.org/wiki/PyYAMLDocumentation) is used to parse the YAML config file.
  - I chose this over other config file formats (I also considered .INI, .py, .config, or other arbitrary formats) since it is common and easy to parse.
