import ast
import logging
from typing import Optional
from pathlib import Path

from mc.base import BaseConfig


def update_config_wildcards(input_file: Path, output_file: Path, overrides: str):
    """
    Overwrite wildcards in a passed input_file and output to output_file
    :param input_file: str path of input
    :param output_file: str path of output
    :param overrides: str representation of dictionary mapping wildcard to replacing values
    """

    logging.info("Writing overrides: {} to file: {}".format(overrides, input_file))
    override_map = ast.literal_eval(overrides)

    with open(input_file, 'r') as f:
        input_lines = f.readlines()

    with open(output_file, 'w') as o:
        for line in input_lines:
            for token in override_map:
                wildcard = "${}".format(token)
                line = line.replace(wildcard, str(override_map[token]))
            o.write(line)


def update_write_path(config: BaseConfig, output_file: Path, override: Optional[str] = None):
    """
    Overwrite config path values for keys ending in "File" with new dir location.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param output_file: Path of output
    :param override: optional str representation of new dir path
    """

    if not override:
        override = output_file.parent
    else:
        override = Path(override)

    old_path = Path(config['controler']['outputDirectory'])
    print(old_path)
    new_path = override / old_path.name
    print(new_path)
    config['controler']['outputDirectory'] = str(new_path)


def update_read_paths(config: BaseConfig, output_file: Path, override: Optional[str] = None):

    # todo @Sean not sure if you want to use new file path or dir path, assuming file for now
    """
    Overwrite config path in given Config for keys ending in "File" with new dir location,
    maintaining file name. Can be optionally overwritten.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param output_file: Path of output
    :param override: optional str representation of new dir path
    """

    if not override:
        override = output_file.parent
    else:
        override = Path(override)

    logging.info(f"Input file path overrides: {override} to config: {config.path}")
    if not override.exists():
        raise NotADirectoryError

    for module_name, module in config.items():
        for param_name, param in module.params.items():
            if param_name[-4:] == 'File':
                if param.value == 'null' or "":
                    continue
                # if not Path(param.value).exists():  # doesn't work in tests
                #     continue
                old_path = Path(param.value)
                new_path = override / old_path.name
                print(f"Input file path override: {str(old_path)} to: {str(new_path)}")
                logging.info(f"Input file path override: {str(old_path)} to: {str(new_path)}")
                param.value = str(new_path)

