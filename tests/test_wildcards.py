import filecmp
import os

from mc.wildcards import update_config_wildcards

def test_update_config_one_wildcard():
    in_file = "tests/test_data/test_wildcard.json"
    out_file = "tests/test_data/test_wildcard_out.json"
    correct_ouput = "tests/test_data/test_wildcard_filled.json"
    overrides = "{'wildcard': 'filled'}"

    update_config_wildcards(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)