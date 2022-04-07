"""
Init/Source module.
"""
import os
from pathlib import Path


__version__ = "1.0.0"
_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))

_DEFAULTS_DIR = _ROOT / 'default_data'
if not _DEFAULTS_DIR.is_dir():
    raise NotADirectoryError(f"Default data dir not found at {_DEFAULTS_DIR}")
