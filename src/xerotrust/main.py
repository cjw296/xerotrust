from getpass import getpass
from pprint import pprint

import click
from pathlib import Path



class Config:
    def __init__(self, path: Path) -> None:
        self.path = path


@click.group()
@click.option(
    '--config',
    'config_path',
    type=click.Path(path_type=Path),
    default=Path('.xerotrust.yml'),
    help='Path to the configuration file.'
)
@click.pass_context
def cli(ctx: click.Context, config_path: Path) -> None:
    """Xerotrust command line interface."""
    ctx.obj = Config(path=config_path)


@cli.command()
@click.pass_obj
def login(config: Config) -> None:
    """Authenticate and store credentials."""



@cli.command()
@click.pass_obj
def dump(config: Config) -> None:
    """Dump stored credentials."""
    click.echo(f"Dump command called. Config path: {config.path}")
    # Implementation to follow
