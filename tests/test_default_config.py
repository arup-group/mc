"""
Build Module tests.
"""

import pytest
import os
import env
from pathlib import Path


env.set_module()
from mc.base import BaseConfig, get_params_search, get_paramsets_search, get_paramset_type
from mc.build import BaseConfig, DefaultConfig, BuildConfig
from mc import get_default_path


def test_default_config_path():
    assert os.path.exists(get_default_path())


def test_load_config():
    config = BaseConfig(path=get_default_path())
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

