import filecmp
import os

from mc.wildcards import update_config_wildcards

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