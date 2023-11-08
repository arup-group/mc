"""
Find method tests.
"""

import pytest
import env


env.set_module()
from mc.base import BaseConfig


def test_test_env_paths():
    assert env.test_xml_path.exists()


@pytest.fixture
def config():
    return BaseConfig(path=env.test_xml_path)


def test_find_nothing(config):
    assert config.find('') == []


def test_find_module(config):
    assert config.find("controler")[0].class_type == 'module'


def test_find_param_at_module_level(config):
    params = config.find("transitModes")
    assert len(params) == 1
    assert params[0].value == 'bus,train'


def test_find_param_at_paramset_level(config):
    params = config.find("earlyDeparture")
    assert len(params) == 2
    assert params[0].value == '-0.0'


def test_find_module_param_at_module_level(config):
    params = config.find("transit/transitModes")
    assert len(params) == 1
    assert params[0].value == 'bus,train'


def test_find_all_param_at_module_level(config):
    params = config.find("*/transitModes")
    assert len(params) == 1
    assert params[0].value == 'bus,train'


def test_find_paramset_at_module_level(config):
    paramsets = config.find("scoringParameters::default")
    assert len(paramsets) == 1
    assert paramsets[0].class_type == 'paramset'


def test_find_paramsets_at_module_level(config):
    paramsets = config.find("scoringParameters::*")
    assert len(paramsets) == 2
    assert paramsets[0].class_type == 'paramset'


def test_find_module_paramset_at_module_level(config):
    paramsets = config.find("planCalcScore/scoringParameters::default")
    assert len(paramsets) == 1
    assert paramsets[0].class_type == 'paramset'


def test_find_module_paramsets_at_module_level(config):
    paramsets = config.find("planCalcScore/scoringParameters::*")
    assert len(paramsets) == 2
    assert paramsets[0].class_type == 'paramset'


def test_find_all_paramset_at_module_level(config):
    paramsets = config.find("*/scoringParameters::default")
    assert len(paramsets) == 1
    assert paramsets[0].class_type == 'paramset'


def test_find_all_paramsets_at_module_level(config):
    paramsets = config.find("*/scoringParameters::*")
    assert len(paramsets) == 2
    assert paramsets[0].class_type == 'paramset'


def test_find_paramsets_at_paramsets_level(config):
    paramsets = config.find("scoringParameters::*/activityParams::*")
    assert len(paramsets) == 6
    assert paramsets[0].class_type == 'paramset'


def test_find_paramset_at_paramsets_level(config):
    paramsets = config.find("scoringParameters::default/activityParams::*")
    assert len(paramsets) == 3
    assert paramsets[0].class_type == 'paramset'


def test_find_param_at_paramsets_level(config):
    paramsets = config.find("scoringParameters::default/activityParams::work/priority")
    assert len(paramsets) == 1
    assert paramsets[0].value == '1.0'


def test_find_params_at_paramsets_level(config):
    paramsets = config.find("activityParams::work/priority")
    assert len(paramsets) == 2
    assert paramsets[0].value == '1.0'


def test_find_params_at_nested_paramsets_level(config):
    paramsets = config.find("scoringParameters::default/priority")
    assert len(paramsets) == 3
    assert paramsets[0].value == '1.0'
