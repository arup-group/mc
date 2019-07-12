import os
import sys
from pathlib import Path
import click


__version__ = "0.0.0"


def get_default_path():
    root = Path(os.path.abspath(os.path.dirname(__file__)))
    path = root / 'default_data' / 'default_config.xml'
    if not path.is_file():
        raise FileNotFoundError(f"Default data not found at {path}")
    return path


def print_and_exit(msg):
    """
    Print error message and exit with error code 1.
    """
    click.echo(msg, err=True)
    sys.exit(1)

