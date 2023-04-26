from pathlib import Path
import pytest
import os
from mc.base import BaseConfig
from mc import report
import tempfile


@pytest.fixture()
def config():
    in_file = Path(os.path.join(os.path.dirname(__file__), 'test_data', 'test_config.xml'))
    return BaseConfig(in_file)


def test_add_directory_to_report(config):
    result = report.add_directory_to_report(config)
    assert len(result) > 0
    assert isinstance(result, list)
    assert "network_path:" in "".join(result)
    assert "plans_path:" in "".join(result)
    assert "schedule_path:" in "".join(result)
    assert "vehicles_path:" in "".join(result)


def test_add_scoring_to_report(config):
    result = report.add_scoring_to_report(config)
    assert len(result) > 0
    assert isinstance(result, list)
    assert " mode " in "".join(result)
    assert "subpopulation" in "".join(result)


def test_write_text(config):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        text = report.add_scoring_to_report(config)
        report.write_text(text, output_path)
        assert os.path.exists(os.path.join(output_path, 'simulation_report.txt'))


def test_write_csv(config):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        data = report.add_scoring_to_report(config)
        report.write_csv(data, output_path)
        assert os.path.exists(os.path.join(output_path, 'simulation_report.csv'))


def test_report_config(config):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = temp_dir
        report.report_config(config, output_path)
        assert os.path.exists(os.path.join(output_path, 'simulation_report.txt'))
        assert os.path.exists(os.path.join(output_path, 'simulation_report.csv'))


def test_find_log_files():
    root_dir = os.path.dirname(__file__)
    file_name = 'test_log_file'
    file_directory = report.find_log_files(file_name, root_dir)
    assert all(file.startswith(file_name) for file in file_directory)


def test_merge_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        root_dir = temp_dir
        file_name = 'test_log_file'
        file_directory = report.find_log_files(file_name, os.path.dirname(__file__))
        report.merge_files(file_directory, root_dir)
        assert os.path.exists(os.path.join(root_dir, 'matsim_overrides_summary.log'))


def test_summarise_overrides_log():
    with tempfile.TemporaryDirectory() as temp_dir:
        root_dir = temp_dir
        file_name = 'test_log_file'
        report.summarise_overrides_log(file_name, root_dir)
        assert os.path.exists(os.path.join(root_dir, 'matsim_overrides_summary.log'))