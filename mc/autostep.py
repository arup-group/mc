import os
from pathlib import Path

from mc.base import BaseConfig, Param
from mc.logger import logging
from mc.summarise import summarise_config

DEFAULT_MATSIM_CONFIG_NAME = "matsim_config.xml"
DEFAULT_PLANS_NAME = "output_plans.xml.gz"
DEFAULT_NETWORK_NAME = "output_network.xml.gz"
DEFAULT_TRANSITSCHEDULE_NAME = "output_transitSchedule.xml.gz"
DEFAULT_TRANSITVEHICLES_NAME = "output_transitVehicles.xml.gz"
DEFAULT_FRACTION_OF_ITERATIONS_TO_DISABLE_INNOVATION = 0.8


def autostep_config(
        sim_root: Path,
        seed_matsim_config_path: Path,
        start_index: str,
        total_iterations: str,
        step: str,
        biteration_matsim_config_path: Path,
        overrides: tuple
) -> None:
    """
    Step a config for bitsim based on arguments and an overrides map.
    Note that start_index will have already been incremented by a step.
    Note that MATSim configs use paths relative to config location.
    """

    # force the input types as required
    if not isinstance(sim_root, Path):
        sim_root = Path(sim_root)
    if not isinstance(seed_matsim_config_path, Path):
        seed_matsim_config_path = Path(seed_matsim_config_path)
    if not isinstance(biteration_matsim_config_path, Path):
        biteration_matsim_config_path = Path(biteration_matsim_config_path)
    if not isinstance(start_index, int):
        start_index = int(start_index)
    if not isinstance(total_iterations, int):
        total_iterations = int(total_iterations)
    if not isinstance(step, int):
        step = int(step)

    if not len(overrides) % 2 == 0:
        raise UserWarning(
            f"""
            Overrides must be of even length (key value pairs, eg k1, v1, k2, v2, ...).
            Provided overrides '{overrides}' have length {len(overrides)}.
            """
        )

    overrides = construct_override_map_from_tuple(overrides)

    logging.info(f"Loading seed config from: {seed_matsim_config_path}")
    config = BaseConfig(seed_matsim_config_path)
    set_default_behaviours(config, step, seed_matsim_config_path)

    first_iteration = start_index - step
    last_iteration = start_index
    new_write_path = sim_root / str(last_iteration)

    set_cooling(config=config, total_iterations=total_iterations, start_index=last_iteration, step=step)
    set_write_path(config=config, new_write_path=new_write_path)
    set_iterations(config=config, first_iteration=first_iteration, last_iteration=last_iteration)
    find_and_set_overrides(config=config, overrides=overrides)

    if not first_iteration == 0:  # if first iteration - don't update input paths
        previous_root = sim_root / str(first_iteration)
        auto_set_input_paths(config=config, root=previous_root)

    logging.info(f"Writing config to: {biteration_matsim_config_path}")
    # after first iteration, matsim should have created the dir already (for previous step outputs).
    biteration_matsim_config_path.parent.mkdir(parents=True, exist_ok=True)
    config.write(biteration_matsim_config_path)

    # summarise the key information from matsim config to a text file
    text_log_path = biteration_matsim_config_path.parent
    summarise_config(config, text_log_path)

    logging.info("Autostep complete")


def construct_override_map_from_tuple(overrides: tuple) -> dict:
    if not overrides:
        return {}
    override_map = {}
    for i in range(0, len(overrides), 2):
        override_map[overrides[i]] = overrides[i + 1]
    return override_map


def set_cooling(config, total_iterations, start_index, step, target=20):
    """
    Set fractionOfIterationsToDisableInnovation to 0 if iterations exceeded.
    Otherwise set for lesser of [0.2 * step, 20]
    """
    if start_index > total_iterations:  # assume cooling
        set_innovation(config=config, new_fraction="0")
    else:
        desired_intermediate_cooling_steps = min([(0.2 * step), target])
        new_fraction = 1 - (desired_intermediate_cooling_steps / step)
        set_innovation(config=config, new_fraction=str(new_fraction))


def set_innovation(config, new_fraction):
    """
    Set config fractionOfIterationsToDisableInnovation.
    """
    fraction = config['strategy'].get('fractionOfIterationsToDisableInnovation')
    config['strategy']['fractionOfIterationsToDisableInnovation'] = new_fraction
    logging.info(f"Changing fractionOfIterationsToDisableInnovation: {fraction} to: {new_fraction}")


def set_default_behaviours(config: BaseConfig, step: int, seed_matsim_config_path: Path):
    """
    Set common behaviours in config.
    """
    step = str(step)

    logging.info("Setting common behaviour overrides.")
    overwriteFiles = config['controler']['overwriteFiles']
    config['controler']['overwriteFiles'] = "deleteDirectoryIfExists"
    logging.info(f"Changing: {overwriteFiles} to: 'deleteDirectoryIfExists'")

    writeEventsInterval = config['controler']['writeEventsInterval']
    config['controler']['writeEventsInterval'] = step
    logging.info(f"Changing: {writeEventsInterval} to: {step}")

    writePlansInterval = config['controler']['writePlansInterval']
    config['controler']['writePlansInterval'] = step
    logging.info(f"Changing: {writePlansInterval} to: {step}")

    config['planCalcScore']['writeExperiencedPlans'] = "true"
    logging.info("Forcing writeExperiencedPlans to true")

    fix_relative_input_paths_to_abs(config=config, seed_matsim_config_path=seed_matsim_config_path)


def set_write_path(config: BaseConfig, new_write_path: Path) -> None:
    """
    Note that 'outputDirectory' == '$next_matsim_dir' from overrides
    """
    logging.info("Write path override to config")
    old_write_path = Path(config['controler']['outputDirectory'])
    config['controler']['outputDirectory'] = str(new_write_path)
    logging.info(f"Write file path override: {str(old_write_path)} to: {str(new_write_path)}")


def auto_set_input_paths(config: BaseConfig, root: Path) -> None:
    """
    Change input config path value for <>File names parameters, eg inputNetworkFile.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param root: Path
    """

    logging.info("Input path overrides to config")
    for module, param, default in [
        ("network", "inputNetworkFile", DEFAULT_NETWORK_NAME),
        ("plans", "inputPlansFile", DEFAULT_PLANS_NAME),
        ("transit", "transitScheduleFile", DEFAULT_TRANSITSCHEDULE_NAME),
        ("transit", "vehiclesFile", DEFAULT_TRANSITVEHICLES_NAME),
    ]:
        prev_path = config[module][param]
        new_path = root / default
        logging.info(f"Input ({param}) file path override: {str(prev_path)} to: {str(new_path)}")
        config[module][param] = str(new_path)


def fix_relative_input_paths_to_abs(config: BaseConfig, seed_matsim_config_path: Path):
    logging.info("Input path overrides to config")
    for module, param in [
        ("network", "inputNetworkFile"),
        ("plans", "inputPlansFile"),
        ("transit", "transitScheduleFile"),
        ("transit", "vehiclesFile"),
    ]:
        prev_path = Path(config[module][param])
        if not prev_path.is_absolute():
            new_path = Path(os.path.join(
                os.path.dirname(seed_matsim_config_path), os.path.expanduser(prev_path)
            )).resolve()
            logging.info(f"Input ({param}) file path override: {str(prev_path)} to: {str(new_path)}")
            config[module][param] = str(new_path)


def set_iterations(config: BaseConfig, first_iteration: int, last_iteration: int) -> None:
    """
    Set config firstIteration and lastIteration.
    """
    logging.info("Step overrides to config")
    old_firstIteration = config['controler']['firstIteration']
    config['controler']['firstIteration'] = str(first_iteration)
    logging.info(f"firstIteration (step) override: {old_firstIteration} to: {first_iteration}")
    old_lastIteration = config['controler']['lastIteration']
    config['controler']['lastIteration'] = str(last_iteration)
    logging.info(f"lastIteration (step) override: {old_lastIteration} to: {last_iteration}")


def find_and_set_overrides(config: BaseConfig, overrides: dict) -> None:
    """
    Set mutations (for example from a random or grid search) based on
    mc addresses in the overrides. For example given:
    {
        'planCalcScore/scoringParameters:default/performing': '10',
        'planCalcScore/scoringParameters:default/activityParams:work/openingTime': '07:00:00',
        'planCalcScore/scoringParameters:default/modeParams:car/monetaryDistanceRate': '-0,00001',
        'planCalcScore/scoringParameters:*/modeParams:car/monetaryDistanceRate': '-0,00001',
        'strategy/fractionOfIterationsToDisableInnovation': '0',
        'strategy/strategysettings:default/weight': '0'
    }
    """
    for k, v in overrides.items():
        params = config.find(k)
        for param in params:
            if isinstance(param, Param):
                old_value = param.value
                param.value = v
                logging.info(f"Override {param.ident}: {old_value} to: {v}")
