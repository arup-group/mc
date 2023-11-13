"""
BaseConfig slicing and making tests.
"""

import pytest
import env


env.set_module()
from mc.base import BaseConfig, get_params_search, get_paramsets_search
from mc.debug import *
from mc.valid import VALID_MAP


def test_module_valid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_module_keys = test_config.valid_keys
    assert valid_module_keys


def test_module_param_valid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_param_keys = test_config["planCalcScore"].valid_param_keys
    assert valid_param_keys


def test_paramset_names_and_types():
    test_config = BaseConfig(path=env.test_json_path)
    ident = test_config["planCalcScore"]["scoringParameters::default"].ident
    ty = test_config["planCalcScore"]["scoringParameters::default"].type
    assert not ident == ty


def test_get_paramsets_type_search():
    assert get_paramsets_search(VALID_MAP, "scoringParameters::default")


def test_get_params_type_search():
    assert get_params_search(VALID_MAP, "scoringParameters::default")


def test_module_paramset_level_1_valid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_paramset_keys = test_config["planCalcScore"].valid_paramset_keys
    assert valid_paramset_keys


def test_module_param_level_1_valid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_param_keys = test_config["planCalcScore"][
        "scoringParameters::default"
    ].valid_param_keys
    assert valid_param_keys


def test_module_paramset_level_2_valid_key_construction_():
    test_config = BaseConfig(path=env.test_json_path)
    valid_paramset_keys = test_config["planCalcScore"][
        "scoringParameters::default"
    ].valid_paramset_keys
    assert valid_paramset_keys


def test_module_paramset_level_2_keys():
    test_config = BaseConfig(path=env.test_json_path)
    paramset_keys = test_config["planCalcScore"][
        "scoringParameters::default"
    ].parametersets
    assert paramset_keys


def test_module_paramset_level_3_invalid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_paramset_keys = test_config["planCalcScore"]["scoringParameters::default"][
        "modeParams::car"
    ].valid_paramset_keys
    assert len(valid_paramset_keys) == 0


def test_module_param_level_2_valid_key_construction():
    test_config = BaseConfig(path=env.test_json_path)
    valid_param_keys = test_config["planCalcScore"]["scoringParameters::default"][
        "modeParams::car"
    ].valid_param_keys
    assert valid_param_keys


def test_invalid_module_invalid_name():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config["NOTVALID"] = test_config["planCalcScore"]


def test_parameterset_level_1_invalid_name():
    test_config = BaseConfig(path=env.test_json_path)
    paramset = test_config["planCalcScore"]["scoringParameters::default"]
    with pytest.raises(KeyError):
        test_config["planCalcScore"]["NOTVALID"] = paramset


def test_param_level_1_invalid_name():
    test_config = BaseConfig(path=env.test_json_path)
    param = test_config["planCalcScore"]["BrainExpBeta"]
    with pytest.raises(KeyError):
        test_config["planCalcScore"]["NOTVALID"] = param


def test_parameterset_level_2_invalid_name():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config["planCalcScore"]["scoringParameters::default"][
            "NOTVALID"
        ] = test_config["planCalcScore"]["scoringParameters::default"][
            "activityParams::education"
        ]


def test_param_level_2_invalid_name():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config["planCalcScore"]["scoringParameters::default"][
            "NOTVALID"
        ] = test_config["planCalcScore"]["scoringParameters::default"]["lateArrival"]


def test_param_level_2_invalid_value():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(ValueError):
        test_config["planCalcScore"]["scoringParameters::default"]["closingTime"] = 4


def test_param_level_2_invalid_key():
    test_config = BaseConfig(path=env.test_json_path)
    with pytest.raises(KeyError):
        test_config["planCalcScore"]["scoringParameters::default"]["cloPPingTime"] = "4"


def test_get_default_to_default():
    test_config = BaseConfig(path=env.test_json_path)
    v = test_config["planCalcScore"]["scoringParameters"]["lateArrival"]
    assert v == "-18.0"


def test_get_default_to_list():
    test_config = BaseConfig(path=env.test_json_path)
    v = test_config["planCalcScore"]["scoringParameters"]["activityParams"]
    assert isinstance(v, list)


def test_nested_set():
    c = BaseConfig()
    c["controler"]["mobsim"] = "a"
    assert c["controler"]["mobsim"] == "a"


def test_nested_set_paramsets():
    c = BaseConfig()
    c["planCalcScore"]["scoringParameters::group1"]["earlyDeparture"] = "1"
    assert c["planCalcScore"]["scoringParameters::group1"]["earlyDeparture"] == "1"


def test_nested_set_fail():
    c = BaseConfig()
    with pytest.raises(KeyError):
        c["INVALID"]["mobsim"] = "a"


def test_nested_set_paramsets_fail():
    c = BaseConfig()
    with pytest.raises(KeyError):
        c["planCalcScore"]["INVALID::group1"]["earlyDeparture"] = "1"


def test_dmc_module_parameters():
    test_config = BaseConfig(path=env.test_json_path)
    dmc_module = test_config["DiscreteModeChoice"]
    assert dmc_module["modelType"] == "Tour"
    assert dmc_module["selector"] == "MultinomialLogit"


def test_dmc_module_parameter_sets():
    test_config = BaseConfig(path=env.test_json_path)
    dmc_module = test_config["DiscreteModeChoice"]
    multinomial_logit_paramset = dmc_module["selector:MultinomialLogit"]
    assert multinomial_logit_paramset["maximumUtility"] == "700.0"


def test_dmc_mode_availability_car_parameter_set():
    test_config = BaseConfig(path=env.test_json_path)
    dmc_module = test_config["DiscreteModeChoice"]
    mode_availability_car_paramset = dmc_module["modeAvailability:Car"]
    assert mode_availability_car_paramset["availableModes"] == "car,pt,walk,bike"
