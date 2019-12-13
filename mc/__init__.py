"""
Init/Source module.
"""
import os
from pathlib import Path
import click

__version__ = "0.0.0"
_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))

_DEFAULTS_DIR = _ROOT / 'default_data'
if not _DEFAULTS_DIR.is_dir():
    raise NotADirectoryError(f"Default data dir not found at {path}")


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""
    def convert(self, value, param, ctx):
        return Path(super().convert(value, param, ctx))
