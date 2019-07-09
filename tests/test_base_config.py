import pytest
import os
import env

env.set_module()
from mc.base import Config, Module, ParamSet, Param


THIS_DIR = env.this_dir()

test_xml_path = os.path.join(THIS_DIR, 'test_data', 'test_config.xml')
test_json_path = os.path.join(THIS_DIR, 'test_data', 'test_config.json')
test_temp_xml_path = os.path.join(THIS_DIR, 'test_data', 'test_temp_config.xml')
test_temp_json_path = os.path.join(THIS_DIR, 'test_data', 'test_temp_config.json')
test_bad_config_path = os.path.join(THIS_DIR, 'test_data', 'test_diff.json')


def test_test_env_paths():

    assert os.path.exists(test_xml_path)
    assert os.path.exists(test_json_path)


def test_default_read_xml():
    test_config = Config(path=test_xml_path)
    assert len(test_config.modules)


def test_default_read_json():
    test_config = Config(path=test_json_path)
    assert len(test_config.modules)


def test_equality_same():
    test_config1 = Config(path=test_xml_path)
    test_config2 = Config(path=test_xml_path)
    assert test_config1 == test_config2


def test_equality_not_same():
    test_config1 = Config(path=test_xml_path)
    test_config2 = Config(path=test_bad_config_path)
    assert not test_config1 == test_config2


def test_xml_and_json_test_configs_equal():
    test_config1 = Config(path=test_xml_path)
    test_config2 = Config(path=test_json_path)
    assert test_config1 == test_config2


def test_build_xml():
    test_config = Config(path=test_xml_path)
    root = test_config.build_xml()
    assert len(root)


def test_write_xml():
    test_config = Config(path=test_xml_path)
    test_config.write_xml(test_temp_xml_path)


def test_build_json_dict():
    test_config = Config(path=test_xml_path)
    d = test_config.build_json()
    assert len(d)


def test_write_json():
    test_config = Config(path=test_xml_path)
    test_config.write_json(test_temp_json_path)


def test_xml_read_json_write_read_consistency():
    test_config1 = Config(path=test_xml_path)
    test_config1.write_json(test_temp_json_path)
    test_config2 = Config(path=test_temp_json_path)
    assert test_config1 == test_config2


def test_json_read_xml_write_read_consistency():
    test_config1 = Config(path=test_json_path)
    test_config1.write_json(test_temp_json_path)
    test_config2 = Config(path=test_temp_xml_path)
    assert test_config1 == test_config2


def test_print(capfd):
    test_config = Config(path=test_xml_path)
    test_config.print()
    out, err = capfd.readouterr()
    assert out


def test_diff():
    test_config1 = Config(path=test_json_path)
    test_config2 = Config(path=test_bad_config_path)
    assert len(test_config1.add_diffs(test_config2)) == 15


def test_config_dict_navigation():
    test_config = Config(path=test_xml_path)
    test_module = test_config.modules['planCalcScore']
    scoringParameters = test_module.parametersets['scoringParameters:default']
    activityParams = scoringParameters.parametersets['activityParams:home']
    activityType = activityParams.params['activityType']
    assert activityType.data['value'] == 'home'


def test_module_dict_get():
    test_config = Config(path=test_xml_path)
    assert isinstance(test_config['planCalcScore'], Module)


def test_paramset_level_1_dict_get():
    test_config = Config(path=test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters:default'], ParamSet)


def test_paramset_level_2_dict_get():
    test_config = Config(path=test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters:default']['activityParams:home'], ParamSet)


def test_param_dict_get():
    test_config = Config(path=test_xml_path)
    assert isinstance(test_config['planCalcScore']['scoringParameters:default']['activityParams:home']['activityType'], str)


def test_module_dict_set():
    test_config_transit = Config(path=test_bad_config_path)['transit']
    test_config = Config(path=test_json_path)
    test_config['transit'] = test_config_transit
    assert test_config['transit']['transitScheduleFile'] == ''


def test_paramset_level_1_dict_set():
    test_config_score = Config(path=test_bad_config_path)['planCalcScore']["scoringParameters:default"]
    test_config = Config(path=test_json_path)
    test_config['planCalcScore']['scoringParameters:unknown'] = test_config_score
    assert test_config['planCalcScore']['scoringParameters:unknown']['performing'] == '5.0'


def test_param_dict_set():
    test_config = Config(path=test_json_path)
    assert isinstance(test_config['planCalcScore']["scoringParameters:default"].params['performing'], Param)
    test_config['planCalcScore']["scoringParameters:default"]['performing'] = '7.0'
    assert isinstance(test_config['planCalcScore']["scoringParameters:default"].params['performing'], Param)
    assert test_config['planCalcScore']["scoringParameters:default"]['performing'] == '7.0'


def test_module_key_valid():
    test_config = Config(path=test_json_path)
    with pytest.raises(KeyError):
        test_config.is_valid_key('NOTVALID')


def test_paramset_level_1_key_valid():
    test_config = Config(path=test_json_path)
    with pytest.raises(KeyError):
        test_config['planCalcScore'].is_valid_paramset_key('NOTVALID')

def test_param_level_1_key_valid():
    test_config = Config(path=test_json_path)
    with pytest.raises(KeyError):
        test_config['planCalcScore']['scoringParameters:default'].is_valid_param_key('NOTVALID')

