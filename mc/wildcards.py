import ast
import logging
from pathlib import Path


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
