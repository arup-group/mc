"""
Test environment setup.
"""

import os
from pathlib import Path


def test_data_dir():
    return Path(os.path.abspath(__file__)).parent / 'test_data'
