"""
CLI function tests.
"""
from mc import cli


def test_string_to_tuple():
    assert len(cli.string_to_tuple("1,2,3")) == 3
