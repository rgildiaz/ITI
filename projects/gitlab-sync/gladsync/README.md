# GLADSync Reference

#### 🚧 UNDER CONSTRUCTION 🚧

The GLADSync package is split into three components:

- [`main.py`](#mainpy) is the main entry-point for the CLI.
- [`gladsync.py`](#gladsyncpy) contains the actual program logic.
- [`config.py`](#configpy) is a utility for parsing config files.

It additionally contains:

- [`example_config.yaml`](#app-configuration), which is a starter config file.

## [`main.py`](./main.py)

`main.py` initializes the [Typer](#typer) app and provides it an entry-point through the [`main()`](#main) function.

### `main(config_path, test, verbose)`

Define the app's command line options and create a [`Config`](#config) and [`GladSync`](#gladsync) object.

Typer works with built-in type hints. By setting the default value of this functions parameters to `typer.Option()` objects, default values, required options, and help text can be set. The `@app.command()` decorator is required for `main()` to be recognized as a CLI command.

Args:

- `config_path`
- `test`
- `verbose`

## [`gladsync.py`](./gladsync.py)

`gladsync.py` contains the main functionality and program logic of the app. Using data given by the app's [configuration](#configpy), [`GladSync`](#gladsync) calls the [GitLab](#python-gitlab) and [Active Directory](../README.md#active-directory-api) APIs. It fetches available groups from the specified Active Directory instance, and then ([optionally](#mainconfig_path-test-verbose)) modifies the given GitLab instance to match.

### `GladSync`

A `GladSync` object is created by [`main.py`](#mainconfig_path-test-verbose).

## [`config.py`](./config.py)

### `Config`

the `Config` class parses the `.yaml` config file that is given by the `-config.file` command line option. It is called by [`GladSync`](#gladsync) on startup.

### App Configuration

A starter configuration file can be found at [`./example_config.yaml`](./example_config.yaml).

## Dependencies

### `python-gitlab`

### Typer

### Other

- [pathlib]()
