from pathlib import Path
import pytest
from copy import deepcopy
import os

from mc.base import BaseConfig
from mc import bitsim


@pytest.fixture()
def config():
    in_file = Path("tests/test_data/test_config.xml")
    return BaseConfig(in_file)


def test_set_write_path(config):
    bitsim.set_write_path(config, {'outputDirectory': 'testing'})
    assert config['controler']['outputDirectory'] == 'testing'


def test_set_input_paths(config):
    bitsim.set_input_paths(config, {'matsim_source': 'test/ing'})
    assert config['network']['inputNetworkFile'] == 'test/ing/network.xml'
    assert config['plans']['inputPlansFile'] == 'test/ing/population.xml.gz'
    assert config['plans']['inputPersonAttributesFile'] == 'test/ing/population_attributes.xml.gz'
    assert config['transit']['transitScheduleFile'] == 'test/ing/schedule-merged.xml'
    assert config['transit']['vehiclesFile'] == 'test/ing/vehicles.xml'
    assert config['transit']['transitLinesAttributesFile'] == 'null'


def test_set_step(config):
    bitsim.set_last_iteration(config, {'step': '999'})
    assert config['controler']['lastIteration'] == '999'


def test_find_and_set_param(config):
    bitsim.find_and_set_overrides(
        config,
        {"modeParams:car/constant": "-1.0"}
        )
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "0.0"


def test_find_and_set_params(config):
    bitsim.find_and_set_overrides(
        config,
        {
            "modeParams:car/constant": "-1.0",
            "scoringParameters:unknown/modeParams:bus/constant": "-1.0"
            }
        )
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"

def test_find_and_set_bad_param(config):
    cnfg = deepcopy(config)
    bitsim.find_and_set_overrides(
        config,
        {"modeParams:*/horseback": "-1.0"}
        )
    assert cnfg == config


def test_construct_overrides_map_from_tuple():
    assert bitsim.construct_override_map_from_tuple(
        ('a','b','c','d')
    ) == {'a':'b', 'c':'d'}


def test_step_config(tmp_path):
    in_file = Path("tests/test_data/test_config.xml")
    out_file = Path(tmp_path) / "test_config.xml"
    bitsim.step_config(
        input_file=in_file,
        output_file=out_file,
        overrides=(
           'matsim_source', 'test/ing',
           'outputDirectory', 'testing',
           'step', '999',
           "modeParams:car/constant", "-1.0",
           "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
        )
    )
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == '999'
    assert config['controler']['outputDirectory'] == 'testing'
    assert config['network']['inputNetworkFile'] == 'test/ing/network.xml'
    assert config['plans']['inputPlansFile'] == 'test/ing/population.xml.gz'
    assert config['plans']['inputPersonAttributesFile'] == 'test/ing/population_attributes.xml.gz'
    assert config['transit']['transitScheduleFile'] == 'test/ing/schedule-merged.xml'
    assert config['transit']['vehiclesFile'] == 'test/ing/vehicles.xml'
    assert config['transit']['transitLinesAttributesFile'] == 'null'
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
