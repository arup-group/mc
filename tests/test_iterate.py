from pathlib import Path

from mc.base import BaseConfig
from mc import iterate


def test_update_config_update_paths_override():

    in_file = Path("tests/test_data/test_config.xml")
    config = BaseConfig(in_file)

    current_dir = Path("tests/test_data/new_dir/")
    next_dir = Path("tests/test_data/new_dir")

    iterate.write_path(config, current_dir, next_dir)
    iterate.input_paths(config, current_dir, next_dir)

    # don't write for test
    correct_ouput = Path("tests/test_data/test_config_new_paths.xml")

    for line in config.diff(BaseConfig(correct_ouput)):
        print(line)

    assert config == BaseConfig(correct_ouput)
