"""
BaseConfig method tests.
"""

import pytest
import env
from unittest.mock import MagicMock


env.set_module()
from mc.base import BaseConfig, Module, ParamSet, Param, build_paramset_key


def test_test_env_paths():
    assert env.test_xml_path.exists()
    assert env.test_json_path.exists()
    assert env.test_temp_xml_path.exists()
    assert env.test_temp_json_path.exists()
    assert env.test_bad_config_path.exists()


def test_default_read_xml():
    test_config = BaseConfig(path=env.test_xml_path)
    assert len(test_config.modules)


def test_default_read_json():
    test_config = BaseConfig(path=env.test_json_path)
    assert len(test_config.modules)


def test_param_equality_same():
    test_config1 = BaseConfig(path=env.test_xml_path)["planCalcScore"]['scoringParameters::default']["lateArrival"]
    test_config2 = BaseConfig(path=env.test_xml_path)["planCalcScore"]['scoringParameters::default']["lateArrival"]
    assert test_config1 == test_config2


def test_paramset_equality_same():
    test_config1 = BaseConfig(path=env.test_xml_path)["planCalcScore"]['scoringParameters::default']
    test_config2 = BaseConfig(path=env.test_xml_path)["planCalcScore"]['scoringParameters::default']
    assert test_config1 == test_config2


def test_dmc_paramset_equality_same():
    test_config1 = BaseConfig(path=env.test_xml_path)["DiscreteModeChoice"]["selector:MultinomialLogit"]
    test_config2 = BaseConfig(path=env.test_xml_path)["DiscreteModeChoice"]["selector:MultinomialLogit"]
    assert test_config1 == test_config2

def test_module_equality_same():
    test_config1 = BaseConfig(path=env.test_xml_path)["planCalcScore"]
    test_config2 = BaseConfig(path=env.test_xml_path)["planCalcScore"]
    assert test_config1 == test_config2


def test_config_equality_same():
    test_config1 = BaseConfig(path=env.test_xml_path)
    test_config2 = BaseConfig(path=env.test_xml_path)
    assert test_config1 == test_config2


def test_equality_not_same():
    test_config1 = BaseConfig(path=env.test_xml_path)
    test_config2 = BaseConfig(path=env.test_bad_config_path)
    assert not test_config1 == test_config2


def test_xml_and_json_test_dmc_paramset_equal():
    test_config1 = BaseConfig(path=env.test_xml_path)["DiscreteModeChoice"]
    test_config2 = BaseConfig(path=env.test_json_path)["DiscreteModeChoice"]

    assert test_config1 == test_config2


def test_xml_and_json_test_configs_equal():
    test_config1 = BaseConfig(path=env.test_xml_path)
    test_config2 = BaseConfig(path=env.test_json_path)

    assert set(test_config1.modules.keys()) == set(test_config2.modules.keys())
    assert test_config1 == test_config2


def test_build_xml():
    test_config = BaseConfig(path=env.test_xml_path)
    root = test_config.build_xml()
    assert len(root)


def test_write_xml():
    test_config = BaseConfig(path=env.test_xml_path)
    test_config.write_xml(env.test_temp_xml_path)


def test_build_json_dict():
    test_config = BaseConfig(path=env.test_xml_path)
    d = test_config.build_json()
    assert len(d)


def test_write_json():
    test_config = BaseConfig(path=env.test_xml_path)
    test_config.write_json(env.test_temp_json_path)


def test_xml_read_json_write_read_consistency():
    test_config1 = BaseConfig(path=env.test_xml_path)
    test_config1.write_json(env.test_temp_json_path)
    test_config2 = BaseConfig(path=env.test_temp_json_path)
    assert test_config1 == test_config2


def test_json_read_xml_write_read_consistency():
    test_config1 = BaseConfig(path=env.test_json_path)
    test_config1.write_json(env.test_temp_json_path)
    test_config2 = BaseConfig(path=env.test_temp_xml_path)
    assert test_config1 == test_config2


def test_print(capfd):
    test_config = BaseConfig(path=env.test_xml_path)
    test_config.print()
    out, err = capfd.readouterr()
    assert out


def test_diff():
    test_config1 = BaseConfig(path=env.test_json_path)
    test_config2 = BaseConfig(path=env.test_bad_config_path)
    assert len(test_config1.diff(test_config2)) == 40


def test_config_dict_navigation():
    test_config = BaseConfig(path=env.test_xml_path)
    test_module = test_config.modules['planCalcScore']
    scoringParameters = test_module.parametersets['scoringParameters::default']
    activityParams = scoringParameters.parametersets['activityParams::home']
    activityType = activityParams.params['activityType']
    assert activityType.value == 'home'


def test_module_dict_get():
    test_config = BaseConfig(path=env.test_xml_path)
    assert isinstance(test_config['planCalcScore'], Module)


def test_paramset_level_1_dict_get():
    test_config = BaseConfig(path=env.test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters::default'], ParamSet)


def test_dmc_paramset_level_1():
    test_config = BaseConfig(path=env.test_xml_path)
    assert isinstance(test_config['DiscreteModeChoice']['selector:MultinomialLogit'], ParamSet)


def test_paramset_level_2_dict_get():
    test_config = BaseConfig(path=env.test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters::default']['activityParams::home'], ParamSet)


def test_param_dict_get():
    test_config = BaseConfig(path=env.test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters::default']['activityParams::home']['activityType'], str)


def test_module_dict_set():
    test_config_transit = BaseConfig(path=env.test_bad_config_path)['transit']
    test_config = BaseConfig(path=env.test_json_path)
    test_config['transit'] = test_config_transit
    assert test_config['transit']['transitScheduleFile'] == ''


def test_paramset_level_1_dict_set():
    test_config_score = BaseConfig(path=env.test_bad_config_path)['planCalcScore']["scoringParameters::default"]
    test_config = BaseConfig(path=env.test_json_path)
    test_config['planCalcScore']['scoringParameters::unknown'] = test_config_score
    assert test_config['planCalcScore']['scoringParameters::unknown']['performing'] == '5.0'


def test_param_dict_set():
    test_config = BaseConfig(path=env.test_json_path)
    assert isinstance(test_config['planCalcScore']["scoringParameters::default"].params['performing'], Param)
    test_config['planCalcScore']["scoringParameters::default"]['performing'] = '7.0'
    assert isinstance(test_config['planCalcScore']["scoringParameters::default"].params['performing'], Param)
    assert test_config['planCalcScore']["scoringParameters::default"]['performing'] == '7.0'


def test_module_key_valid():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config.is_valid_key('NOTVALID')


def test_paramset_level_1_key_valid():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config['planCalcScore'].is_valid_paramset_key('NOTVALID')


def test_param_level_1_key_valid():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config['planCalcScore']['scoringParameters::default'].is_valid_param_key('NOTVALID')


def test_build_paramset_key_with_colon():
    mock_elem = MagicMock()
    mock_elem.attrib = {'type': 'selector:MultinomialLogit'}
    test_config = BaseConfig(path=env.test_json_path)

    paramset_type, key, uid = build_paramset_key(mock_elem)
    assert paramset_type == 'selector:MultinomialLogit', "Paramset type did not match"
    assert key == 'selector:MultinomialLogit', "Key did not match"
    assert uid == 'MultinomialLogit', "UID did not match"
