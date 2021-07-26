from pathlib import Path

from mc.base import BaseConfig, Param
from mc.logger import logging


def step_config(input_file: Path, output_file: Path, overrides: tuple) -> None:
    """
    Step a config for bitsim based on overrides map.
    Note that MATSim configs use paths relative to config location.
    Args:
        input_file (Path): Input config path ("mc_input_config")
        output_file (Path): Output config path ("current matsim")
        overrides (tuple): Tuple representation of overrides
    """
    if isinstance(input_file, str):
        input_file = Path(input_file)
    if isinstance(output_file, str):
        output_file = Path(output_file)

    logging.info(f"Loading config from: {input_file}")
    config = BaseConfig(input_file)

    logging.info(f"Applying overrides: {overrides}")
    overrides = construct_override_map_from_tuple(overrides=overrides)
    set_write_path(config=config, overrides=overrides)
    set_input_paths(config=config, overrides=overrides)
    set_last_iteration(config=config, overrides=overrides)
    find_and_set_overrides(config=config, overrides=overrides)

    logging.info(f"Writing config to: {output_file}")
    try:
        output_file.parent.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.error(f"Folder for {output_file} is already there")
    else:
        logging.info(f"Creating dir for {output_file}")
    config.write(output_file)


def construct_override_map_from_tuple(overrides: tuple) -> dict:
    if not overrides:
        return {}
    override_map = {}
    for i in range(0, len(overrides), 2):
        override_map[overrides[i]] = overrides[i+1]
    return override_map


def set_write_path(config: BaseConfig, overrides: dict) -> None:
    logging.info("Write path override to config")
    old_write_path = Path(config['controler']['outputDirectory'])
    new_write_path = Path(overrides.pop("outputDirectory"))
    config['controler']['outputDirectory'] = str(new_write_path)
    logging.info(f"Write file path override: {str(old_write_path)} to: {str(new_write_path)}")


def set_input_paths(config: BaseConfig, overrides: dict) -> None:
    """
    Change input config path value for <>File names parameters, eg inputNetworkFile.
    Note that MATSim configs use paths relative to config location.
    TODO path names can be hardcoded to 'output_plans.xml.gz' and so
    after 1st biteration.
    :param config: Config
    :param overrides: Path of output
    """
    logging.info("Input path overrides to config")
    dir = Path(overrides.pop("matsim_source"))

    for _, module in config.modules.items():
        for param_name, param in module.params.items():
            """
            This is a bit dangerous, ie if we add new params in future
            we need to check they do or don't end in 'File' as appropriate.
            But on the plus side - this method is also more flexible than
            hardcoding, which would require us to check which version of
            MATSim is being used.
            """
            if param_name[-4:] == 'File':
                if param.value in ['null', "", "true", "false"]:
                    continue

                old_path = Path(param.value)
                file_name = old_path.name
                new_path = dir / file_name
                logging.info(f"Input file path override: {str(old_path)} to: {str(new_path)}")
                param.value = str(new_path)


def set_last_iteration(config: BaseConfig, overrides: dict) -> None:
    """
    Set config last iteration to "step".
    TODO - pretty sure we could set the firstIteration and last Iteration such
    'biteration' 0 would be firstIteration=0 and lastIteration=10,
    'biteration' 10 would be firstIteration=10 and lastIteration=20,
    and so on, which will be nicer for the user. This would require we pass
    'index' and 'next_index' from the orchestration to the cli.
    """
    logging.info("Step overrides to config")
    old_step = config['controler']['lastIteration']
    new_step = overrides.pop('step')
    config['controler']['lastIteration'] = new_step
    logging.info(f"LastIteration (step) override: {old_step} to: {new_step}")


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
