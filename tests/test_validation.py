import pytest
import os
import env


env.set_module()
from mc.base import _Config
from mc.validation import *


def test_path_good():
    assert not bad_path('test_path', 'good.xml')
    assert not bad_path('test_path', 'good.xml.gz')
    assert bad_path('test_path', '')
    assert bad_path('test_path', 'bad.csv')


def test_path_validate():
    test_config = _Config(path=env.test_xml_path)
    logs = test_config.log_bad_paths()
    assert len(logs) == 0
    bad_config = _Config(path=env.test_bad_config_path)
    logs = bad_config.log_bad_paths()
    assert logs


def test_subpop_validate_good():
    test_config = _Config(path=env.test_xml_path)
    log = test_config.log_bad_subpopulations()
    assert len(log) == 0


def test_subpop_validate_bad():
    bad_config = _Config(path=env.test_bad_config_path)
    assert bad_config.log_bad_subpopulations()


def test_mode_validate_good():
    test_config = _Config(path=env.test_xml_path)
    assert len(test_config.log_bad_scoring()) == 0


def test_mode_validate_bad():
    bad_config = _Config(path=env.test_bad_config_path)
    assert bad_config.log_bad_scoring()

