from lxml import etree as et
import os
import pandas as pd
import click
import numpy as np
from halo import Halo
from datetime import datetime
from mc import params

# get args {default_xml path, test schedule}

# Get defaults from xml
# Get values from test schedule

# set params
# first level
# embedded as scoringParams - modeParams - activityParams

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("schedule_path", type=click.Path(exists=True))
@click.argument("default_path", type=click.Path(exists=True))
@click.option('--out_dir', default='output', help='output directory, default: "output/"')
@click.option('--select', default=None, help='option to select single test for config')
def cli(schedule_path, default_path, out_dir, select):
    """
    Command line tool for creating MATSim configs from defaults and test schedule.
    :param schedule_path: Parameter schedule file path
    :param default_path: Default parameter schedule file path
    """
    print('\n============MC============')
    params_df, (test_ids, subpops) = get_tests(schedule_path)
    print('Found {} tests:'.format(len(test_ids)))
    if select:
        print('Config selected for test: "{}" only'.format(select))
        assert select in test_ids, "Can't find selected test id"
    for test_id in test_ids:
        if select and not str(select) == str(test_id):
            continue
        config = TestConfig(test_id, subpops, params_df, default_path, schedule_path, out_dir)
        config.build_config()


def get_tests(path):
    """
    Load and validate csv schedule of params.
    :param path: Schedule path String
    :return: (parameter DataFrame, (test id List, sub population id List))
    """
    params_df = pd.read_csv(path, header=[0, 1, 2, 3, 4], index_col=[0, 1])
    return params_df, params.validate_schedule(params_df)


class TestConfig:

    def __init__(self, test_id, subpops, param_df, defaults_path, schedule_path, out_dir):
        """
        Test Config Object, loads default config xml object and sets values for PlanCalcScore
        and Strategy Modules, using input from Schedule csv. If a new value is not found in
        schedule then the default is maintained.
        :param test_id: Test id, String
        :param subpops: Sub population id, List
        :param param_df: Parameter values, DataFrame
        :param defaults_path: path to default config xml, String
        :param schedule_path: path to param schedule csv, String
        :param out_dir: path for output directory, String
        """

        self.id = test_id
        self.subpops = subpops
        self.param_df = param_df
        self.defaults_path = defaults_path
        self.schedule_path = schedule_path
        self.out_dir = out_dir

        self.root = self.load_xml(defaults_path)

        _, output_name = os.path.split(defaults_path)
        output_name = '{}_test_{}.xml'.format(output_name[:-4], test_id)
        self.output_path = os.path.join(out_dir, output_name)

    def build_config(self):
        with Halo(text='Test {}: Config builder...'.format(self.id), spinner='dots') as spinner:
            self.set_planCalcScore(spinner)
            self.set_strategy(spinner)
            self.write_xml(spinner)

    def set_planCalcScore(self, spinner):
        spinner.text = 'Test {}: Scoring module...'.format(self.id)
        module = self.root.xpath("//module[@name='planCalcScore']")[0]
        # loop through module children - parametersets for subpops:
        for subpop_paramset in module.xpath("./parameterset[@type='scoringParameters']"):
            subpop = subpop_paramset.xpath("./param[@name='subpopulation']/@value")[0]
            levels = ['planCalcScore']
            self.set_element(subpop_paramset, params.ParamList.scoringParameters, subpop, levels)

            # loop throgh modeParams
            spinner.text = 'Test {}: {} mode params...'.format(self.id, subpop)
            for mode_paramset in subpop_paramset.xpath("./parameterset[@type='modeParams']"):
                levels = ['planCalcScore', 'modeParams']
                self.set_elements(mode_paramset, 'mode', params.ParamList.modeParams, subpop, levels)

            # loop throgh modeParams
            spinner.text = 'Test {}: {} activity params...'.format(self.id, subpop)
            for act_paramset in subpop_paramset.xpath("./parameterset[@type='activityParams']"):
                levels = ['planCalcScore', 'activityParams']
                self.set_elements(act_paramset, 'activityType', params.ParamList.activityParams, subpop, levels)

    def set_strategy(self, spinner):
        spinner.text = 'Test {}: Strategy module...'.format(self.id)
        module = self.root.xpath("//module[@name='strategy']")[0]

        # loop through module children - parametersets for subpops:
        for paramset in module.xpath("./parameterset[@type='strategysettings']"):
            subpop = paramset.xpath("./param[@name='subpopulation']/@value")[0]
            param = paramset.xpath("./param[@name='strategyName']/@value")[0]
            # get value from schedule
            data = self.param_df.loc[self.id, subpop].loc['strategy', 'strategysettings', param, :, :].values
            if is_blank(data):
                # print('test {} {} set to default'.format(self.id, param))
                continue
            # print('test {} {} set to {}'.format(self.id, param, data))
            # Set value
            param_set = paramset.xpath("./param[@name='weight']")[0]
            param_set.attrib['value'] = str(data)

    def set_element(self, parent, param_list, subpop, levels):
        """
        Get and set element for single set of params (from param_list), for given subpopulation.
        :param parent: lxml Element
        :param param_list: List of parameters
        :param subpop: Subpopulation id
        :param levels: INput param table headers
        :return: None
        """

        for level2 in param_list:
            full_levels = levels + [level2]
            (lv1, lv2, lv3, lv4, lv5) = full_levels + [slice(None)] * (5 - len(full_levels))
            data = self.param_df.loc[self.id, subpop].loc[lv1, lv2, lv3, lv4, lv5].values
            if is_blank(data):
                # print('test {} {} set to default'.format(self.id, full_levels[-1]))
                return None
            # print('test {} {} set to {}'.format(self.id, full_levels[-1], data))
            # set
            param = parent.xpath("./param[@name='{}']".format(full_levels[-1]))[0]
            param.attrib['value'] = str(data)

    def set_elements(self, parent, param_set, param_list, subpop, levels):
        """
        Get and set elements for set of params in param_set (for example modes or activities),
        for given subpopulation.
        :param parent: lxml Element
        :param param_list: List of parameters
        :param subpop: Subpopulation id
        :param levels: INput param table headers
        :return: None
        """

        level1 = parent.xpath("./param[@name='{}']/@value".format(param_set))[0]
        for level2 in param_list:
            full_levels = levels + [level1] + [level2]
            (lv1, lv2, lv3, lv4, lv5) = full_levels + [slice(None)] * (5 - len(full_levels))
            data = self.param_df.loc[self.id, subpop].loc[lv1, lv2, lv3, lv4, lv5].values
            if is_blank(data):
                # print('test {} {} set to default'.format(self.id, full_levels[-1]))
                return None
            # print('test {} {} set to {}'.format(self.id, full_levels[-1], data))
            # set
            param = parent.xpath("./param[@name='{}']".format(full_levels[-1]))[0]
            param.attrib['value'] = str(data)

    def write_xml(self, spinner):
        spinner.text = 'Test {}: Writing config to disk...'.format(self.id)
        tree = et.tostring(self.root,
                           pretty_print=True,
                           xml_declaration=False,
                           encoding='UTF-8')
        make_dirs(self.out_dir)
        with open(self.output_path, 'wb') as f:
            time = datetime.strftime(datetime.now(), "%d-%m-%Y %H:%M")
            comment = '<!--Test: {}\n Generated: {}\n Default Source: {}\n Schedule Source: {}-->\n'.\
                format(self.id, time, self.defaults_path, self.schedule_path).\
                encode()
            f.write(b'<?xml version="1.0" ?>\n')
            f.write(b'<!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">\n')
            f.write(comment)
            f.write(tree)
        spinner.succeed('Test {}: Config complete'.format(self.id))

    def load_xml(self, path):
        tree = et.parse(path)
        return tree.getroot()


def is_blank(num):
    return not type(num) == str and np.isnan(num)


def make_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print('creating {}'.format(directory))
