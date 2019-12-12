import logging
from pathlib import Path

from mc.base import BaseConfig


def write_path(config: BaseConfig, current_dir: Path) -> None:
    """
    Change input config path value for outputDirectory path.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param current_dir: Path of output
    """

    logging.info(f"Write path override to config")

    old_path = Path(config['controler']['outputDirectory'])
    logging.info(f"Write file path override: {str(old_path)} to: {str(next_dir)}")

    config['controler']['outputDirectory'] = str(current_dir)


def input_paths(config: BaseConfig, parent_dir: Path) -> None:
    """
    Change input config path value for <>File paths.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param parent_dir: Path of output
    """

    logging.info(f"Input path overrides to config")

    for module_name, module in config.items():
        for param_name, param in module.params.items():
            if param_name[-4:] == 'File':

                if param.value == 'null' or "":
                    continue

                old_path = Path(param.value)
                file_name = old_path.name
                new_path = parent_dir / file_name
                logging.info(f"Input file path override: {str(old_path)} to: {str(new_path)}")
                param.value = str(new_path)
