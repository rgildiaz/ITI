from gladsync import GladSync
from config import Config
from pathlib import Path
import typer

# The CLI app
app = typer.Typer(
    # Disable local vars showing in error messages
    pretty_exceptions_show_locals=False
)


@app.command()
def main(
    config_path: Path = typer.Option(
        ...,    # make this required by passing no default value
        "-config.file",
        help="The config file to use."
    ),
    test: bool = typer.Option(
        True,   # On by default
        "--test",
        "-T",
        help="Test mode. Print expected changes but make no modifications."
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose. Print extra information while running."
    ),
    delete: bool = typer.Option(
        True,
        help="Delete GitLab groups and members as necessary. Otherwise, print expected changes but make no modifications."
    ),
    skip_ad: bool = typer.Option(
        False,
        "--skip_ad",
        "-s",
        help="Skip AD authentication and print GitLab data. This is only here for testing."
    ),
    std_out: bool = typer.Option(
        True,
        "--std_out",
        "-o",
        help="Print logs to standard out."
    )
):
    '''
    Sync AD groups to GitLab!\n
    Fetches groups from AD and creates/modifies GitLab groups to match.\n
    A .yaml config file must be provided with the -config.file option. See `./gladsync/example_config.yaml`.
    '''
    config = Config(config_path, test, verbose, std_out)
    # all program logic is contained in the GladSync object
    GladSync(config, test, verbose, delete, skip_ad)


if __name__ == "__main__":
    app()
