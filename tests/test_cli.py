"""
CLI function tests.
"""
import os
import traceback
from pathlib import Path
from click.testing import CliRunner

import env
env.set_module()
from mc import cli


def test_string_to_tuple():
    assert len(cli.string_to_tuple("1,2,3")) == 3


def test_step(tmpdir):
    runner = CliRunner()
    temp_xml = os.path.join(tmpdir, "test.xml")
    result = runner.invoke(
        cli.cli,
        [
            "step",
            str(env.test_v12_xml_path),
            temp_xml,
            "outputDirectory", "outputDirectory",
            "matsim_source", "matsim_source",
            "step", "10"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_autostep(tmpdir):
    runner = CliRunner()
    temp_xml = os.path.join(tmpdir, "0", "test.xml")
    result = runner.invoke(
        cli.cli,
            [
            "autostep",
            str(tmpdir),
            str(env.test_v12_xml_path),
            "10",
            "100",
            "10",
            temp_xml,
            "a", "a",
            "b", "b",
            "c", "c"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_fill(tmpdir):
    runner = CliRunner()
    temp_xml = os.path.join(tmpdir, "test.xml")
    result = runner.invoke(
        cli.cli,
        [
            "fill",
            str(env.test_v12_xml_path),
            temp_xml,
            "outputDirectory", "outputDirectory",
            "matsim_source", "matsim_source",
            "step", "10"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_convert(tmpdir):
    runner = CliRunner()
    temp_xml = Path(tmpdir) / "test.json"
    result = runner.invoke(
        cli.cli,
        [
            "convert",
            str(env.test_v12_xml_path),
            str(temp_xml),
            "-d",
            "-p"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_gen(tmpdir):
    runner = CliRunner()
    temp_xml = Path(tmpdir) / "test.json"
    result = runner.invoke(
        cli.cli,
        [
            "gen",
            "empty",
            str(temp_xml),
            "-d",
            "-p"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_build(tmpdir):
    runner = CliRunner()
    temp_xml = Path(tmpdir) / "test.json"
    result = runner.invoke(
        cli.cli,
        [
            "build",
            str(temp_xml),
            "-i", "temp/path",
            "-o", "temp/path",
            "-e", "1111",
            "-d",
            "-p"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    assert os.path.isfile(temp_xml)


def test_diff(tmpdir):
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "diff",
            str(env.test_v12_xml_path),
            str(env.test_v12_xml_path)
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0


def test_debug(tmpdir):
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "debug",
            str(env.test_v12_xml_path),
            "-p"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0


def test_print(tmpdir):
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "print",
            str(env.test_v12_xml_path),
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0


def test_find(tmpdir):
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "find",
            str(env.test_v12_xml_path),
            "controler/*"
            ]
        )
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0