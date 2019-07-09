import pytest
import os
import env


env.set_module()
from mc.base import Config
from mc.validation import *


THIS_DIR = env.this_dir()

test_xml_path = os.path.join(THIS_DIR, 'test_data', 'test_config.xml')
test_json_path = os.path.join(THIS_DIR, 'test_data', 'test_config.json')
test_temp_xml_path = os.path.join(THIS_DIR, 'test_data', 'test_temp_config.xml')
test_temp_json_path = os.path.join(THIS_DIR, 'test_data', 'test_temp_config.json')
test_bad_config_path = os.path.join(THIS_DIR, 'test_data', 'test_diff.json')


def test_path_good():
    assert not bad_path('test_path', 'good.xml')
    assert not bad_path('test_path', 'good.xml.gz')
    assert bad_path('test_path', '')
    assert bad_path('test_path', 'bad.csv')


def test_path_validate():
    test_config = Config(path=test_xml_path)
    logs = test_config.log_bad_paths()
    assert len(logs) == 0
    bad_config = Config(path=test_bad_config_path)
    logs = bad_config.log_bad_paths()
    assert logs


def test_subpop_validate_good():
    test_config = Config(path=test_xml_path)
    log = test_config.log_bad_subpopulations()
    assert len(log) == 0


def test_subpop_validate_bad():
    bad_config = Config(path=test_bad_config_path)
    assert bad_config.log_bad_subpopulations()


def test_mode_validate_good():
    test_config = Config(path=test_xml_path)
    assert len(test_config.log_bad_scoring()) == 0


def test_mode_validate_bad():
    bad_config = Config(path=test_bad_config_path)
    assert bad_config.log_bad_scoring()

