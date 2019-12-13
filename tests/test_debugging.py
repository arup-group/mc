"""
Validator (debug) method tests.
"""
from . import test_data_dir
from mc.base import BaseConfig
from mc.debugging import *


def test_path_good():
    assert not bad_path('test_path', 'good.xml')
    assert not bad_path('test_path', 'good.xml.gz')
    assert bad_path('test_path', '')
    assert bad_path('test_path', 'bad.csv')


def test_multimodal_validate():
    test_config = BaseConfig(path=test_data_dir() / 'mm_test.xml')
    logs = test_config.log_multimodal_module()
    assert len(logs) == 3


def test_path_validate():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    logs = test_config.log_bad_paths()
    assert len(logs) == 0
    bad_config = BaseConfig(path=test_data_dir() / 'test_diff.json')
    logs = bad_config.log_bad_paths()
    assert logs


def test_subpop_validate_good():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    log = test_config.log_bad_subpopulations()
    assert len(log) == 0


def test_subpop_validate_bad():
    bad_config = BaseConfig(path=test_data_dir() / 'test_diff.json')
    assert bad_config.log_bad_subpopulations()


def test_mode_validate_good():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert len(test_config.log_bad_scoring()) == 0


def test_mode_validate_bad():
    bad_config = BaseConfig(path=test_data_dir() / 'test_diff.json')
    assert bad_config.log_bad_scoring()


def test_find_missing_modes_good():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    print(len(test_config.log_missing_modes()))
    assert len(test_config.log_missing_modes()) == 0


def test_find_missing_modes_bad():
    bad_config = BaseConfig(path=test_data_dir() / 'test_diff.json')
    print(len(bad_config.log_missing_modes()))
    assert(bad_config.log_missing_modes())
