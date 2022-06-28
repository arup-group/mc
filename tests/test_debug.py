"""
Validator (debug) method tests.
"""

import pytest
import os
import env


env.set_module()
from mc.base import BaseConfig
from mc.debug import *

def test_get_subpopulations():
    assert BaseConfig(path=env.test_v14_xml_path).get_subpopulations() == {'default', 'hhs_caravail_yes', 'hhs_caravail_no'}

def test_get_modes():
    assert BaseConfig(path=env.test_v14_xml_path).get_main_mode() == {"car"}
    assert BaseConfig(path=env.test_v14_xml_path).get_mode_choices() == {'bus'  , 'train', 'tram', 'subway', 'walk', 'bike', 'train', 'ferry', 'car'}
    assert BaseConfig(path=env.test_v14_xml_path).get_chained_modes() == {"car", "bike"}
    assert BaseConfig(path=env.test_v14_xml_path).get_transit_modes() == {"bus", "tram", "train", "ferry", "subway", "helicopter"}
    assert BaseConfig(path=env.test_v14_xml_path).get_deterministic_modes() == {"tram", "rail", "ferry", "subway"}
    assert BaseConfig(path=env.test_v14_xml_path).get_intermodal_access_egress_modes() == {"car", "bike", "walk"}
    assert BaseConfig(path=env.test_v14_xml_path).get_scoring_modes() == {'bus', 'pt', 'rail', 'tram', 'subway', 'walk', 'bike', 'ferry', 'car'}
    assert BaseConfig(path=env.test_v14_xml_path).get_modes() == {'bus', 'pt', 'rail', 'train', 'tram', 'subway', 'walk', 'helicopter', 'bike', 'train', 'ferry', 'car'}

def test_get_activities():
    assert BaseConfig(path=env.test_v14_xml_path).get_activities() == {
        'other',
        'escort_education',
        'work',
        'visit',
        'shop',
        'escort_shop',
        'depot',
        'delivery',
        'escort_work',
        'medical',
        'business',
        'home',
        'escort_home',
        'education',
        'escort_other',
        'escort_business'
        }

def test_get_strategies():
        assert BaseConfig(path=env.test_v14_xml_path).get_strategies() == {
        'ChangeExpBeta',
        'SubtourModeChoice',
        'ReRoute',
        'TimeAllocationMutator_ReRoute',
        }

def test_path_good():
    assert check_path('test_path', 'good.xml')
    assert check_path('test_path', 'good.xml.gz')
    assert not check_path('test_path', '')
    assert not check_path('test_path', None)
    assert not check_path('test_path', 'bad.csv')


def test_smoke_debugs():
    BaseConfig(path=env.test_xml_path).debug()
    BaseConfig(path=env.test_v12_xml_path).debug()
    BaseConfig(path=env.test_v14_xml_path).debug()
    BaseConfig(path=env.test_json_path).debug()
    BaseConfig(path=env.test_temp_xml_path).debug()
    BaseConfig(path=env.test_temp_json_path).debug()
    BaseConfig(path=env.test_mm_path).debug()
