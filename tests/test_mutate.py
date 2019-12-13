from pathlib import Path
import pytest

from . import test_data_dir
from mc.base import BaseConfig, Param
from mc import mutate


def test_distributions_map():
    for name, distribution in mutate.DISTRIBUTION_MAP.items():
        assert isinstance(distribution(), str)


def test_triangle_param_mutate():
    mutator_params = {
        "distribution": "triangle",
        "lower": 0,
        "centre": 10,
        "upper": 100,
        "digits": 1
    }
    mutate_param = Param('a', mutator_params)
    test_param = Param('test', 'init')
    mutate.mutate(test_param, mutate_param)
    assert test_param.value != 'init'


def test_normal_param_mutate():
    mutator_params = {
        "distribution": "normal",
        "mu": 20,
        "upper_conf": 50,
        "lower": 0,
        "upper": 100,
        "digits": 1
    }
    mutate_param = Param('a', mutator_params)
    test_param = Param('test', 'init')
    mutate.mutate(test_param, mutate_param)
    assert test_param.value != 'init'


def test_exponential_param_mutate():
    mutator_params = {
        "distribution": "exponential",
        "beta": 1,
        "scale": 1,
        "base": 0,
        "lower": 0,
        "upper": 100,
        "digits": 1
    }
    mutate_param = Param('a', mutator_params)
    test_param = Param('test', 'init')
    mutate.mutate(test_param, mutate_param)
    assert test_param.value != 'init'


def test_mutate_config_read():
    mutate_config = BaseConfig(test_data_dir() / "test_mutate_config.json")
    assert isinstance(mutate_config['planCalcScore']['scoringParameters:*']['modeParams:car'][
                          'monetaryDistanceRate'], dict)
    assert isinstance(mutate_config['planCalcScore']['scoringParameters:*'][
                          'marginalUtilityOfMoney'], dict)


def test_yield_pairs():
    config = BaseConfig(test_data_dir() / "test_config.xml")
    mutate_config = BaseConfig(test_data_dir() / "test_mutate_config.json")
    collected_yields = [(mutate_dict, param) for mutate_dict, param in mutate.yield_pairs_safe(
        mutate_config, config)]
    assert len(collected_yields) == 10


def test_yield_pairs_fail():
    config = BaseConfig(test_data_dir() / "test_config_missing_mode_params.xml")
    mutate_config = BaseConfig(test_data_dir() / "test_mutate_config.json")
    with pytest.raises(KeyError):
        _ = [(mutate_dict, param) for mutate_dict, param in mutate.yield_pairs_safe(
            mutate_config, config)]


def test_find_and_mutate():
    config = BaseConfig(test_data_dir() / "test_config.xml")
    mutate_config = BaseConfig(test_data_dir() / "test_mutate_config.json")

    mutate.find_and_mutate(config, mutate_config)

    assert config != BaseConfig(test_data_dir() / "test_config.xml")
