from pathlib import Path

from mc.base import BaseConfig
from mc import step


def test_update_config_update_paths_override():

    in_file = Path("tests/test_data/test_config.xml")
    config = BaseConfig(in_file)

    current_dir = Path("tests/test_data/new_dir/")
    next_dir = Path("tests/test_data/new_dir")

    step.write_path(config, next_dir)
    step.input_paths(config, current_dir)

    # don't write for test
    correct_ouput = Path("tests/test_data/test_config_new_paths.xml")

    assert config == BaseConfig(correct_ouput)
