"""
Source module.
"""
import os
from pathlib import Path


__version__ = "0.0.0"


def get_default_path():
    """
    Get default configuration path.
    :return: Path
    """
    root = Path(os.path.abspath(os.path.dirname(__file__)))
    path = root / 'default_data' / 'default_config.xml'
    if not path.is_file():
        raise FileNotFoundError(f"Default data not found at {path}")
    return path
