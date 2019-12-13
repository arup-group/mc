"""
BaseConfig method tests.
"""

import pytest

from . import *
from mc.base import BaseConfig, Module, ParamSet, Param


def test_test_env_paths():
    assert (test_data_dir() / 'test_config.xml').exists()
    assert (test_data_dir() / 'test_config.json').exists()
    assert (test_data_dir() / 'test_temp_config.xml').exists()
    assert (test_data_dir() / 'test_temp_config.json').exists()
    assert (test_data_dir() / 'test_diff.json').exists()
    assert (test_data_dir() / 'mm_test.xml').exists()


def test_default_read_xml():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert len(test_config.modules)


def test_default_read_json():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    assert len(test_config.modules)


def test_param_equality_same():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]['scoringParameters:default']["lateArrival"]
    test_config2 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]['scoringParameters:default']["lateArrival"]
    assert test_config1 == test_config2


def test_paramset_equality_same():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]['scoringParameters:default']
    test_config2 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]['scoringParameters:default']
    assert test_config1 == test_config2


def test_module_equality_same():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]
    test_config2 = BaseConfig(path=test_data_dir() / 'test_config.xml')["planCalcScore"]
    assert test_config1 == test_config2


def test_config_equality_same():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert test_config1 == test_config2


def test_equality_not_same():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_diff.json')
    assert not test_config1 == test_config2


def test_xml_and_json_test_configs_equal():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_config.json')
    assert test_config1 == test_config2


def test_build_xml():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    root = test_config.build_xml()
    assert len(root)


def test_write_xml():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config.write_xml(test_data_dir() / 'test_temp_config.xml')


def test_build_json_dict():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    d = test_config.build_json()
    assert len(d)


def test_write_json():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config.write_json(test_data_dir() / 'test_temp_config.json')


def test_xml_read_json_write_read_consistency():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config1.write_json(test_data_dir() / 'test_temp_config.json')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_temp_config.json')
    assert test_config1 == test_config2


def test_json_read_xml_write_read_consistency():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.json')
    test_config1.write_json(test_data_dir() / 'test_temp_config.json')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_temp_config.xml')
    assert test_config1 == test_config2


def test_print(capfd):
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_config.print()
    out, err = capfd.readouterr()
    assert out


def test_diff():
    test_config1 = BaseConfig(path=test_data_dir() / 'test_config.json')
    test_config2 = BaseConfig(path=test_data_dir() / 'test_diff.json')
    assert len(test_config1.diff(test_config2)) == 18


def test_config_dict_navigation():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    test_module = test_config.modules['planCalcScore']
    scoringParameters = test_module.parametersets['scoringParameters:default']
    activityParams = scoringParameters.parametersets['activityParams:home']
    activityType = activityParams.params['activityType']
    assert activityType.data['value'] == 'home'


def test_module_dict_get():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert isinstance(test_config['planCalcScore'], Module)


def test_paramset_level_1_dict_get():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert isinstance(test_config['planCalcScore']['scoringParameters:default'], ParamSet)


def test_paramset_level_2_dict_get():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert isinstance(test_config['planCalcScore']['scoringParameters:default']['activityParams:home'], ParamSet)


def test_param_dict_get():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.xml')
    assert isinstance(test_config['planCalcScore']['scoringParameters:default']['activityParams:home']['activityType'], str)


def test_module_dict_set():
    test_config_transit = BaseConfig(path=test_data_dir() / 'test_diff.json')['transit']
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    test_config['transit'] = test_config_transit
    assert test_config['transit']['transitScheduleFile'] == ''


def test_paramset_level_1_dict_set():
    test_config_score = BaseConfig(path=test_data_dir() / 'test_diff.json')['planCalcScore']["scoringParameters:default"]
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    test_config['planCalcScore']['scoringParameters:unknown'] = test_config_score
    assert test_config['planCalcScore']['scoringParameters:unknown']['performing'] == '5.0'


def test_param_dict_set():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    assert isinstance(test_config['planCalcScore']["scoringParameters:default"].params['performing'], Param)
    test_config['planCalcScore']["scoringParameters:default"]['performing'] = '7.0'
    assert isinstance(test_config['planCalcScore']["scoringParameters:default"].params['performing'], Param)
    assert test_config['planCalcScore']["scoringParameters:default"]['performing'] == '7.0'


def test_module_key_valid():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    with pytest.raises(KeyError):
        test_config.validate_key('NOTVALID')


def test_paramset_level_1_key_valid():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    with pytest.raises(KeyError):
        test_config['planCalcScore'].validate_paramset_key('NOTVALID')


def test_param_level_1_key_valid():
    test_config = BaseConfig(path=test_data_dir() / 'test_config.json')
    with pytest.raises(KeyError):
        test_config['planCalcScore']['scoringParameters:default'].validate_param('NOTVALID', 1)

