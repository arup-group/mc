"""
Build Module tests.
"""

import os
from pathlib import Path

from mc.build import BaseConfig, DefaultConfig, BuildConfig
from mc import _DEFAULTS_DIR


def test_default_config_path():
    assert os.path.exists(_DEFAULTS_DIR / 'default_config.xml')


def test_load_config():
    config = BaseConfig(path=_DEFAULTS_DIR / 'default_config.xml')
    assert config["planCalcScore"]['scoringParameters:default']["lateArrival"]


def test_init_default_config():
    config = DefaultConfig()
    assert isinstance(config["controler"]['mobsim'], str)


def test_init_build_config():
    in_path = Path('~/in_path')
    out_path = Path('~/out_path')

    config = BuildConfig(
        input_dir=in_path,
        output_dir=out_path,
        subpops=['default', 'high', 'low'],
        modes=['car', 'walk', 'pt'],
        acts=['home', 'work']
    )
    assert isinstance(config["controler"]['mobsim'], str)

