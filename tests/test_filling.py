import filecmp
import os

import pytest

from mc.fill import match_replace, param_replace, BadFileTypeError

test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))


def test_matchreplace_config_update_one_matching_fill(tmpdir):
    in_file = "{}/test_wildcard.json".format(test_data_dir)
    out_file = "{}/test_wildcard_out.json".format(tmpdir)
    correct_ouput = "{}/test_wildcard_filled.json".format(test_data_dir)
    overrides = ["wildcard", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)


def test_matchreplace_config_update_one_matching_fill_xml(tmpdir):
    in_file = "{}/test_wildcard.xml".format(test_data_dir)
    out_file = "{}/test_wildcard_out.xml".format(tmpdir)
    correct_ouput = "{}/test_wildcard_filled.xml".format(test_data_dir)
    overrides = ["wildcard", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)


def test_matchreplace_config_no_update_when_no_match(tmpdir):
    in_file = "{}/test_wildcard.json".format(test_data_dir)
    out_file = "{}/test_wildcard_out.json".format(tmpdir)
    overrides = ["matchless", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, in_file)


def test_paramreplace_config_update_one_matching_fill_xml(tmpdir):
    in_file = "{}/test_wildcard.xml".format(test_data_dir)
    out_file = "{}/test_paramreplace_out.xml".format(tmpdir)
    correct_ouput = "{}/test_paramreplace_filled.xml".format(test_data_dir)
    overrides = ["fluxCapacitorFactor", "1955"]

    param_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)


def test_paramreplace_config_no_update_when_no_match_xml(tmpdir):
    in_file = "{}/test_wildcard.xml".format(test_data_dir)
    out_file = "{}/test_paramreplace_out.xml".format(tmpdir)
    overrides = ["fluxResistorFactor", "1955"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, in_file)


def test_does_not_replace_params_in_non_xml_file():
    with pytest.raises(BadFileTypeError) as e_info:
        param_replace("/some/path/params.json", "/some/path/new-params.json", "something")
    assert e_info.value.args[0] == "Only XML files are supported", "Unexpected error message"
