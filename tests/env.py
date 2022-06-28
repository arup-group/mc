"""
Test environment setup.
"""

import sys
import os
from pathlib import Path


def set_module():
    sys.path.append(os.path.abspath('../mc'))


def this_dir():
    return Path(os.path.abspath(__file__)).parent


def root():
    return this_dir().parent


test_xml_path = this_dir() / 'test_data' / 'test_config.xml'
test_v12_xml_path = this_dir() / 'test_data' / 'test_config_v12.xml'
test_v14_xml_path = this_dir() / 'test_data' / 'test_config_v14.xml'
test_json_path = this_dir() / 'test_data' / 'test_config.json'
test_temp_xml_path = this_dir() / 'test_data' / 'test_temp_config.xml'
test_temp_json_path = this_dir() / 'test_data' / 'test_temp_config.json'
test_bad_config_path = this_dir() / 'test_data' / 'test_diff.json'
temp_xml_path_write = this_dir() / 'test_data' / 'temp.xml'
test_mm_path = this_dir() / 'test_data' / 'mm_test.xml'
