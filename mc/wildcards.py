import ast
import logging
from pathlib import Path
import os

def update_config_wildcards(input_file: str, output_file: str, overrides):
    """
    Overwrite wildcards in a passed input_file and output to output_file
    :param input_file: str path of input
    :param output_file: str path of output
    :param overrides: str representation of dictioary mapping wildcard to replacing values
    """
    logging.info("Writing overrides: {} to file: {}".format(overrides, input_file))
    override_map = construct_override_map_from_list(overrides)

    with open(input_file, 'r') as f:
        input_lines = f.readlines()

    # Create target directory & all intermediate directories if they don't exist
    intermediate_dir = os.path.dirname(output_file)
    try:
        os.makedirs(intermediate_dir)
        logging.info("Directory {} Created".format(intermediate_dir))
    except IOError:
        logging.info("Directory {} already exists".format(intermediate_dir))

    with open(output_file, 'w') as o:
        for line in input_lines:
            for token in override_map:
                wildcard = "${}".format(token)
                line = line.replace(wildcard, str(override_map[token]))
            o.write(line)

def construct_override_map_from_list(overrides: tuple):
    override_map = {}
    for i in range(0, len(overrides), 2):
        override_map[overrides[i]] = overrides[i+1]
    return override_map

def construct_override_map_from_literal(overrides):
    return ast.literal_eval(overrides)

