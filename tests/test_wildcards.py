import filecmp
import os
from pathlib import Path

from mc.base import BaseConfig
from mc.wildcards import update_config_wildcards, update_write_path, update_read_paths


def test_update_config_update_one_matching_wildcard():
    in_file = "tests/test_data/test_wildcard.json"
    out_file = "tests/test_data/test_wildcard_out.json"
    correct_ouput = "tests/test_data/test_wildcard_filled.json"
    overrides = "{'wildcard': 'filled'}"

    update_config_wildcards(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)


def test_update_config_update_one_matching_wildcard_xml():
    in_file = "tests/test_data/test_wildcard.xml"
    out_file = "tests/test_data/test_wildcard_out.xml"
    correct_ouput = "tests/test_data/test_wildcard_filled.xml"
    overrides = "{'wildcard': 'filled'}"

    update_config_wildcards(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)


def test_update_config_no_update_when_no_match():
    in_file = "tests/test_data/test_wildcard.json"
    out_file = "tests/test_data/test_wildcard_out.json"
    overrides = "{'matchless': 'filled'}"

    update_config_wildcards(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, in_file)
    os.remove(out_file)


def test_update_config_update_paths_override():
    in_file = Path("tests/test_data/test_config.xml")
    out_file = Path("tests/test_data/new_dir/test_config_out.xml")
    correct_ouput = Path("tests/test_data/test_config_new_paths.xml")
    override = "tests/test_data/new_dir"

    config = BaseConfig(in_file)

    update_read_paths(config, out_file, override)
    update_write_path(config, out_file, override)

    # don't write for test

    assert config == BaseConfig(correct_ouput)


def test_update_config_update_paths_auto():
    in_file = Path("tests/test_data/test_config.xml")
    out_file = Path("tests/test_data/new_dir/test_config_out.xml")
    correct_ouput = Path("tests/test_data/test_config_new_paths.xml")
    override = None

    config = BaseConfig(in_file)

    update_read_paths(config, out_file, override)
    update_write_path(config, out_file, override)

    # don't write for test

    assert config == BaseConfig(correct_ouput)
