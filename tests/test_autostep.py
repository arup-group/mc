from pathlib import Path
import pytest
from copy import deepcopy
import os

from mc.base import BaseConfig
from mc import autostep
from mc.bitsim.basic_iter_lambda import lambda_handler
from tests.env import this_dir


def test_construct_overrides_map_from_tuple():
    assert autostep.construct_override_map_from_tuple(
        ('a','b','c','d')
    ) == {'a':'b', 'c':'d'}


def test_construct_overrides_map_from_empty_tuple():
    assert autostep.construct_override_map_from_tuple(()) == {}


@pytest.fixture()
def config():
    in_file = Path(os.path.join(this_dir(), "test_data/test_config.xml"))
    return BaseConfig(in_file)


@pytest.fixture()
def test_path_config():
    in_file = Path(os.path.join(this_dir(), "test_data/test_path_config.xml"))
    return BaseConfig(in_file)


def test_set_innovation(config):
    assert not config['strategy']['fractionOfIterationsToDisableInnovation'] == "0"
    autostep.set_innovation(config=config, new_fraction="0")
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0"


@pytest.mark.parametrize(
    "total_iterations,start_index,step,new_fraction",
    [
        (100, 10, 10, "0.8"),
        (100, 20, 20, "0.8"),
        (100, 20, 50, "0.8"),
        (200, 100, 100, "0.9"),
        (100, 200, 100, "0"),
    ]
)


def test_set_cooling(config, total_iterations, start_index, step, new_fraction):
    assert not config['strategy']['fractionOfIterationsToDisableInnovation'] == new_fraction
    autostep.set_cooling(config=config, total_iterations=total_iterations, start_index=start_index, step=step, target=10)
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == new_fraction


def test_set_default_behaviours(config, tmp_path):
    assert config['controler']['overwriteFiles'] == "failIfDirectoryExists"
    assert config['controler']['writeEventsInterval'] == "1"
    assert config['controler']['writePlansInterval'] == "50"

    step = 5
    autostep.set_default_behaviours(config, step, tmp_path)

    assert config['controler']['overwriteFiles'] == "deleteDirectoryIfExists"
    assert config['controler']['writeEventsInterval'] == "5"
    assert config['controler']['writePlansInterval'] == "5"


def test_set_write_path(config):
    autostep.set_write_path(config, Path("new/path"))
    assert config['controler']['outputDirectory'] == "new/path"


def test_autoset_input_paths(config):
    autostep.auto_set_input_paths(config, Path("test/ing"))
    assert config['network']['inputNetworkFile'] == 'test/ing/output_network.xml.gz'
    assert config['plans']['inputPlansFile'] == 'test/ing/output_plans.xml.gz'
    assert config['transit']['transitScheduleFile'] == 'test/ing/output_transitSchedule.xml.gz'
    assert config['transit']['vehiclesFile'] == 'test/ing/output_transitVehicles.xml.gz'


def test_fix_relative_input_paths_to_abs(test_path_config):
    seed_matsim_config_path = os.path.join(this_dir(), "test_data/test_path_config.xml")
    config_dir = os.path.dirname(seed_matsim_config_path)

    assert test_path_config['network']['inputNetworkFile'] == "./test/network.xml"
    assert test_path_config['plans']['inputPlansFile'] == "../test/population.xml.gz"

    autostep.fix_relative_input_paths_to_abs(test_path_config, seed_matsim_config_path)

    assert test_path_config['network']['inputNetworkFile'] == os.path.abspath(
        os.path.join(config_dir, "test", "network.xml")
    )
    assert test_path_config['plans']['inputPlansFile'] == os.path.abspath(
        os.path.join(config_dir, "..", "test", "population.xml.gz")
    )


def test_absolute_input_paths_retained(test_path_config):
    seed_matsim_config_path = os.path.join(this_dir(), "test_data/test_path_config.xml")

    assert test_path_config['transit']['vehiclesFile'] == "/test/vehicles.xml"

    autostep.fix_relative_input_paths_to_abs(test_path_config, seed_matsim_config_path)

    assert test_path_config['transit']['vehiclesFile'] == os.path.abspath(
        os.path.join("/", "test", "vehicles.xml")
    )


def test_fix_relative_home_input_paths_to_abs(test_path_config):
    seed_matsim_config_path = os.path.join(this_dir(), "test_data/test_path_config.xml")

    assert test_path_config['transit']['transitScheduleFile'] == "~/test/schedule-merged.xml"

    autostep.fix_relative_input_paths_to_abs(test_path_config, seed_matsim_config_path)

    assert test_path_config['transit']['transitScheduleFile'] == os.path.expanduser(
        os.path.join("~", "test", "schedule-merged.xml")
    )


def test_set_iterations(config):
    autostep.set_iterations(config, first_iteration=0, last_iteration=10)
    assert config['controler']['firstIteration'] == '0'
    assert config['controler']['lastIteration'] == '10'


def test_find_and_set_param(config):
    autostep.find_and_set_overrides(
        config,
        {"modeParams:car/constant": "-1.0"}
        )
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "0.0"


def test_find_and_set_params(config):
    autostep.find_and_set_overrides(
        config,
        {
            "modeParams:car/constant": "-1.0",
            "scoringParameters:unknown/modeParams:bus/constant": "-1.0"
            }
        )
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"

def test_finding_and_setting_bad_param_leaves_config_unchanged(config):
    cnfg = deepcopy(config)
    autostep.find_and_set_overrides(
        config,
        {"modeParams:*/horseback": "-1.0"}
        )
    assert cnfg == config


def test_autostep_config_first_iteration(tmp_path):
    in_file = os.path.join("tests", "test_data", "test_config.xml")
    out_dir = os.path.join(tmp_path, "10")
    out_file = os.path.join(tmp_path, "0", "matsim_config.xml")
    autostep.autostep_config(
        sim_root=tmp_path,
        seed_matsim_config_path=in_file,
        start_index="10",
        total_iterations="100",
        step="10",
        biteration_matsim_config_path=out_file,
        overrides=(
           "modeParams:car/constant", "-1.0",
           "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
        )
    )
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == '10'
    assert config['controler']['outputDirectory'] == out_dir
    assert config['network']['inputNetworkFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "network.xml")
    ))
    assert config['plans']['inputPlansFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "population.xml.gz")
    ))
    assert config['transit']['transitScheduleFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "schedule-merged.xml")
    ))
    assert config['transit']['vehiclesFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "vehicles.xml")
    ))
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"


def test_autostep_config(tmp_path):
    in_file = os.path.join("tests", "test_data", "test_config.xml")
    out_dir = os.path.join(tmp_path, "20")
    out_file = os.path.join(tmp_path, "10", "matsim_config.xml")
    autostep.autostep_config(
        sim_root=tmp_path,
        seed_matsim_config_path=in_file,
        start_index="20",
        total_iterations="100",
        step="10",
        biteration_matsim_config_path=out_file,
        overrides=(
           "modeParams:car/constant", "-1.0",
           "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
        )
    )
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == '20'
    assert config['controler']['outputDirectory'] == out_dir
    assert config['network']['inputNetworkFile'] == os.path.join(tmp_path, "10", "output_network.xml.gz")
    assert config['plans']['inputPlansFile'] == os.path.join(tmp_path, "10", "output_plans.xml.gz")
    assert config['transit']['transitScheduleFile'] == os.path.join(tmp_path, "10", "output_transitSchedule.xml.gz")
    assert config['transit']['vehiclesFile'] == os.path.join(tmp_path, "10", "output_transitVehicles.xml.gz")
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"


@pytest.fixture()
def fake_lambda_handler():
    return lambda_handler


def test_step_lambda(tmp_path, fake_lambda_handler):
    event = {
        "orchestration": {
            "sim_root": str(tmp_path),
            "seed_matsim_config_path": os.path.join("tests", "test_data", "test_config.xml"),
            "start_index": "0",
            "total_iterations": "100",
            "step": "10",
            }
        }
    orchestration = fake_lambda_handler(event)

    assert(orchestration["start_index"] == "10")
    assert(orchestration["biteration_matsim_config_path"] == os.path.join(tmp_path, "0", "matsim_config.xml"))


def test_first_two_steps(tmp_path, fake_lambda_handler):
    event = {
        "orchestration": {
            "sim_root": str(tmp_path),
            "seed_matsim_config_path": os.path.join("tests", "test_data", "test_config.xml"),
            "start_index": "0",
            "total_iterations": "100",
            "step": "10",
            }
        }

    orchestration = fake_lambda_handler(event)
    autostep.autostep_config(
        sim_root=orchestration["sim_root"],
        seed_matsim_config_path=orchestration["seed_matsim_config_path"],
        start_index=orchestration["start_index"],
        total_iterations=orchestration["total_iterations"],
        step=orchestration["step"],
        biteration_matsim_config_path=orchestration["biteration_matsim_config_path"],
        overrides=(
           "modeParams:car/constant", "-1.0",
           "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
        )
    )

    out_dir = os.path.join(tmp_path, "10")
    out_file = os.path.join(tmp_path, "0", "matsim_config.xml")
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == '10'
    assert config['controler']['outputDirectory'] == out_dir
    assert config['network']['inputNetworkFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "network.xml")
    ))
    assert config['plans']['inputPlansFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "population.xml.gz")
    ))
    assert config['transit']['transitScheduleFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "schedule-merged.xml")
    ))
    assert config['transit']['vehiclesFile'] == os.path.abspath(
        os.path.expanduser(os.path.join("~", "test", "vehicles.xml")
    ))
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"


    orchestration = fake_lambda_handler({"orchestration": orchestration})
    autostep.autostep_config(
        sim_root=orchestration["sim_root"],
        seed_matsim_config_path=orchestration["seed_matsim_config_path"],
        start_index=orchestration["start_index"],
        total_iterations=orchestration["total_iterations"],
        step=orchestration["step"],
        biteration_matsim_config_path=orchestration["biteration_matsim_config_path"],
        overrides=(
           "modeParams:car/constant", "-1.0",
           "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
        )
    )

    out_dir = os.path.join(tmp_path, "20")
    out_file = os.path.join(tmp_path, "10", "matsim_config.xml")
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == '20'
    assert config['controler']['outputDirectory'] == out_dir
    assert config['network']['inputNetworkFile'] == os.path.join(tmp_path, "10", "output_network.xml.gz")
    assert config['plans']['inputPlansFile'] == os.path.join(tmp_path, "10", "output_plans.xml.gz")
    assert config['transit']['transitScheduleFile'] == os.path.join(tmp_path, "10", "output_transitSchedule.xml.gz")
    assert config['transit']['vehiclesFile'] == os.path.join(tmp_path, "10", "output_transitVehicles.xml.gz")
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"


def test_stepping(tmp_path, fake_lambda_handler):

    orchestration = {
        "sim_root": str(tmp_path),
        "seed_matsim_config_path": os.path.join("tests", "test_data", "test_config.xml"),
        "start_index": "0",
        "total_iterations": "30",
        "step": "10",
        }

    for i in range(10):
        try:
            orchestration = fake_lambda_handler({"orchestration": orchestration})
        except Exception:
            break

        autostep.autostep_config(
            sim_root=orchestration["sim_root"],
            seed_matsim_config_path=orchestration["seed_matsim_config_path"],
            start_index=orchestration["start_index"],
            total_iterations=orchestration["total_iterations"],
            step=orchestration["step"],
            biteration_matsim_config_path=orchestration["biteration_matsim_config_path"],
            overrides=(
            "modeParams:car/constant", "-1.0",
            "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
            )
        )

    assert set(os.listdir(tmp_path)) == {"0", "10", "20"}
    for i in range(10, 30, 10):
        out_dir = os.path.join(tmp_path, str(i+10))
        out_file = os.path.join(tmp_path, str(i), "matsim_config.xml")
        assert os.path.exists(out_file)
        config = BaseConfig(out_file)
        assert config['controler']['lastIteration'] == str(i+10)
        assert config['controler']['outputDirectory'] == out_dir
        assert config['network']['inputNetworkFile'] == os.path.join(tmp_path, str(i), "output_network.xml.gz")
        assert config['plans']['inputPlansFile'] == os.path.join(tmp_path, str(i), "output_plans.xml.gz")
        assert config['transit']['transitScheduleFile'] == os.path.join(tmp_path, str(i), "output_transitSchedule.xml.gz")
        assert config['transit']['vehiclesFile'] == os.path.join(tmp_path, str(i), "output_transitVehicles.xml.gz")
        assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
        assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
        assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
        assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"


def test_stepping_with_cooling(tmp_path, fake_lambda_handler):

    orchestration = {
        "sim_root": str(tmp_path),
        "seed_matsim_config_path": os.path.join("tests", "test_data", "test_config.xml"),
        "start_index": "0",
        "total_iterations": "30",
        "step": "10",
        "cooling_iterations": "10"
        }

    for i in range(10):
        try:
            orchestration = fake_lambda_handler({"orchestration": orchestration})
        except Exception:
            break

        autostep.autostep_config(
            sim_root=orchestration["sim_root"],
            seed_matsim_config_path=orchestration["seed_matsim_config_path"],
            start_index=orchestration["start_index"],
            total_iterations=orchestration["total_iterations"],
            step=orchestration["step"],
            biteration_matsim_config_path=orchestration["biteration_matsim_config_path"],
            overrides=(
            "modeParams:car/constant", "-1.0",
            "scoringParameters:unknown/modeParams:bus/constant", "-1.0"
            )
        )

    assert set(os.listdir(tmp_path)) == {"0", "10", "20", "30"}
    for i in range(10, 30, 10):
        out_dir = os.path.join(tmp_path, str(i+10))
        out_file = os.path.join(tmp_path, str(i), "matsim_config.xml")
        assert os.path.exists(out_file)
        config = BaseConfig(out_file)
        assert config['controler']['lastIteration'] == str(i+10)
        assert config['controler']['outputDirectory'] == out_dir
        assert config['network']['inputNetworkFile'] == os.path.join(tmp_path, str(i), "output_network.xml.gz")
        assert config['plans']['inputPlansFile'] == os.path.join(tmp_path, str(i), "output_plans.xml.gz")
        assert config['transit']['transitScheduleFile'] == os.path.join(tmp_path, str(i), "output_transitSchedule.xml.gz")
        assert config['transit']['vehiclesFile'] == os.path.join(tmp_path, str(i), "output_transitVehicles.xml.gz")
        assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
        assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
        assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
        assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0.8"

    i = 30
    out_dir = os.path.join(tmp_path, str(i+10))
    out_file = os.path.join(tmp_path, str(i), "matsim_config.xml")
    assert os.path.exists(out_file)
    config = BaseConfig(out_file)
    assert config['controler']['lastIteration'] == str(i+10)
    assert config['controler']['outputDirectory'] == out_dir
    assert config['network']['inputNetworkFile'] == os.path.join(tmp_path, str(i), "output_network.xml.gz")
    assert config['plans']['inputPlansFile'] == os.path.join(tmp_path, str(i), "output_plans.xml.gz")
    assert config['transit']['transitScheduleFile'] == os.path.join(tmp_path, str(i), "output_transitSchedule.xml.gz")
    assert config['transit']['vehiclesFile'] == os.path.join(tmp_path, str(i), "output_transitVehicles.xml.gz")
    assert config['planCalcScore']['scoringParameters:default']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:car']["constant"] == "-1.0"
    assert config['planCalcScore']['scoringParameters:unknown']['modeParams:bus']["constant"] == "-1.0"
    assert config['strategy']['fractionOfIterationsToDisableInnovation'] == "0"

