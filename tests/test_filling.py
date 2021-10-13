import filecmp
import os

from mc.fill import match_replace, param_replace


def test_matchreplace_config_update_one_matching_fill():
    in_file = "tests/test_data/test_wildcard.json"
    out_file = "tests/test_data/test_wildcard_out.json"
    correct_ouput = "tests/test_data/test_wildcard_filled.json"
    overrides = ["wildcard", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)


def test_matchreplace_config_update_one_matching_fill_xml():
    in_file = "tests/test_data/test_wildcard.xml"
    out_file = "tests/test_data/test_wildcard_out.xml"
    correct_ouput = "tests/test_data/test_wildcard_filled.xml"
    overrides = ["wildcard", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)


def test_matchreplace_config_no_update_when_no_match():
    in_file = "tests/test_data/test_wildcard.json"
    out_file = "tests/test_data/test_wildcard_out.json"
    overrides = ["matchless", "filled"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, in_file)
    os.remove(out_file)


def test_paramreplace_config_update_one_matching_fill_xml():
    in_file = "tests/test_data/test_wildcard.xml"
    out_file = "tests/test_data/test_paramreplace_out.xml"
    correct_ouput = "tests/test_data/test_paramreplace_filled.xml"
    overrides = ["fluxCapacitorFactor", "1955"]

    param_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, correct_ouput)
    os.remove(out_file)


def test_paramreplace_config_no_update_when_no_match_xml():
    in_file = "tests/test_data/test_wildcard.xml"
    out_file = "tests/test_data/test_paramreplace_out.xml"
    overrides = ["fluxResistorFactor", "1955"]

    match_replace(in_file, out_file, overrides)

    assert filecmp.cmp(out_file, in_file)
    os.remove(out_file)
