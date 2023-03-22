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

### `main(config_path, test, verbose, delete)`

Define the app's command line options and create a [`Config`](#config) and [`GladSync`](#gladsync) object.

Typer works with built-in type hints. By setting the default value of this functions parameters to `typer.Option()` objects, default values, required options, and help text can be set. The `@app.command()` decorator is required for `main()` to be recognized as a CLI command.

Args:

- `config_path` (`str`) - the path to a .yaml config file to use. This is a **required** CLI option.
- `test` (`bool`) - whether or not to use "test" mode. In test mode, log changes that would be made, but make no actual modifications. Default: `True`
- `verbose` (`bool`) - whether or not to use verbose logging. Default: `False`
- `delete` (`bool`) - whether or not to delete any remote resources. This is intended to prevent any accidental deletion of GitLab members or groups during the syncing process. Default: `True`

Typer also (helpfully) auto-generates text for the `--help` CLI option, based on the `help=` arguments within the `typer.Option()` definitions, as well as the docstring within the body of `main()`.

The flow of the program can also be more easily seen in `main()`, as it first collects these arguments, then creates a [`config.Config()`](#config) to parse the config file, and finally runs [`gladsync.Gladsync()`](#gladsync) to complete the program logic.

## [`gladsync.py`](./gladsync.py)

`gladsync.py` contains the main functionality and program logic of the app. Using data given by the app's [configuration](#configpy), [`GladSync`](#gladsync) calls the [GitLab](#python-gitlab) and [Active Directory](../README.md#active-directory-api) APIs. It fetches available groups from the specified Active Directory instance, and then ([optionally](#mainconfig_path-test-verbose)) modifies the given GitLab instance to match.

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

the `Config` class parses the `.yaml` config file that is given by the `-config.file` command line option. It is called by [`GladSync`](#gladsync) on startup.

### App Configuration

A starter configuration file can be found at [`./example_config.yaml`](./example_config.yaml).

## Dependencies

### [`python-gitlab`](https://python-gitlab.readthedocs.io/en/stable/index.html)

The `python-gitlab` package provides a Python wrapper for the GitLab API. It is used in [`gladsync.py`](./gladsync.py) to connect and modify a GitLab instance.

### [Typer](https://typer.tiangolo.com/)

The Typer framework allows for easier CLI creation in Python. It is used in [`main.py`](./main.py) to generate the actual CLI functionality, such as writing help text and configuring CLI options.

### Other

- [`logging`](https://docs.python.org/3/library/logging.html) is used for log messages.
- [`pathlib`](https://docs.python.org/3/library/pathlib.html) is used to parse config file paths.
- [`PyYAML`](https://pyyaml.org/wiki/PyYAMLDocumentation) is used to parse the YAML config file.
  - I chose this over other config file formats (I also considered .INI, .py, .config, or other arbitrary formats) since it is common and easy to parse.
