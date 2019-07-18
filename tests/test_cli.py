"""
CLI function tests.
"""
import env
env.set_module()
from mc import cli, build


def test_string_to_tuple():
    assert len(cli.string_to_tuple("1,2,3")) == 3
