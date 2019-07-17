"""
Commonly implemented Configurations
"""

from mc.base import BaseConfig, Module, ParamSet, Param
import os
from . import get_default_path
from pathlib import Path
from typing import List, Tuple


class Config(BaseConfig):

    def __init__(self, path=None):
        super().__init__(path=path)


class DefaultConfig(BaseConfig):

    def __init__(self):
        super().__init__(path=get_default_path())


class TestConfig(BaseConfig):

    def __init__(self):
        super().__init__()

        # build paths
        output_dir = Path(os.path.join('.', 'test_outputs'))
        input_dir = Path(os.path.join('.', 'test_inputs'))

        attributes_path = input_dir / 'attributes.xml'
        plans_path = input_dir / 'population.xml'
        schedule_path = input_dir / 'transitschedule.xml'
        vehicles_path = input_dir / 'transitVehicles.xml'
        network_path = input_dir / 'network.xml'

        # build config
        self['global']['randomSeed'] = '4711'
        self['global']['coordinateSystem'] = 'EPSG:27700'
        self['global']['numberOfThreads'] = '1'

        self['network']['inputNetworkFile'] = network_path.as_posix()

        self['plans']['inputPlansFile'] = plans_path.as_posix()
        self['plans']['inputPersonAttributesFile'] = attributes_path.as_posix()
        self['plans']['subpopulationAttributeName'] = 'subpopulation'

        self['transit']['useTransit'] = 'true'
        self['transit']['transitScheduleFile'] = schedule_path.as_posix()
        self['transit']['vehiclesFile'] = vehicles_path.as_posix()
        self['transit']['transitModes'] = 'pt'

        self['TimeAllocationMutator']['mutationRange'] = '1000.0'

        self['controler']['outputDirectory'] = output_dir.as_posix()
        self['controler']['firstIteration'] = '0'
        self['controler']['lastIteration'] = '0'
        self['controler']['mobsim'] = 'qsim'
        self['controler']['overwriteFiles'] = 'overwriteExistingFiles'

        self['subtourModeChoice']['chainBasedModes'] = 'car,bike'
        self['subtourModeChoice']['modes'] = 'car,pt,walk,bike'

        self['qsim']['startTime'] = '00:00:00'
        self['qsim']['endTime'] = '24:00:00'
        self['qsim']['flowCapacityFactor'] = '1'
        self['qsim']['storageCapacityFactor'] = '1'
        self['qsim']['mainMode'] = 'car,bus'
        self['qsim']['numberOfThreads'] = '1'

        self['planCalcScore']['BrainExpBeta'] = '1'

        for subpop in ['low income', 'medium income', 'high income', 'freight', 'default']:

            self['planCalcScore'][f'scoringParameters:{subpop}']['lateArrival'] = '-18'
            self['planCalcScore'][f'scoringParameters:{subpop}']['earlyDeparture'] = '-0.0'
            self['planCalcScore'][f'scoringParameters:{subpop}']['marginalUtilityOfMoney'] = '1'
            self['planCalcScore'][f'scoringParameters:{subpop}']['performing'] = '+6'
            self['planCalcScore'][f'scoringParameters:{subpop}']['subpopulation'] = subpop
            self['planCalcScore'][f'scoringParameters:{subpop}']['waiting'] = '-0'
            self['planCalcScore'][f'scoringParameters:{subpop}']['waitingPt'] = '-2'
            self['planCalcScore'][f'scoringParameters:{subpop}']['utilityOfLineSwitch'] = '-1'

            modes = ['car', 'pt', 'walk', 'bike']
            mut_hrs = ['-5', '-5', '-12', '-12']
            mdrs = ['-0.0005', '-0.001', '0', '0']

            for mode, mut_hr, mdr in zip(modes, mut_hrs, mdrs):
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['mode'] = mode
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['constant'] = '0'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['marginalUtilityOfDistance_util_m'] = '0'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['marginalUtilityOfTraveling_util_hr'] = mut_hr
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['monetaryDistanceRate'] = mdr

            activities = ['home', 'work', 'depo', 'dropoff_1', 'dropoff_2', 'dropoff_3']
            typ_durs = ['12:00:00', '08:30:00', '12:00:00', '00:15:00', '00:15:00', '00:15:00']
            min_durs = ['08:00:00', '08:00:00', '08:00:00', '00:10:00', '00:10:00', '00:10:00']

            for act, typ_dur, min_dur in zip(activities, typ_durs, min_durs):
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['activityType'] = act
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['priority'] = '1'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['typicalDuration'] = typ_dur
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['minimalDuration'] = min_dur

        self['strategy']['maxAgentPlanMemorySize'] = '3'

        for subpop in ['low income', 'medium income', 'high income', 'freight']:
            strategies = ['SubtourModeChoice', 'ReRoute', 'TimeAllocationMutator', 'ChangeExpBeta']
            weights = ['0.1', '0.1', '0.1', '0.7']
            for strategy, weight in zip(strategies, weights):

                self['strategy'][f'strategysettings:{subpop}:{strategy}']['strategyName'] = strategy
                self['strategy'][f'strategysettings:{subpop}:{strategy}']['subpopulation'] = subpop
                self['strategy'][f'strategysettings:{subpop}:{strategy}']['weight'] = weight

        self['strategy']['strategysettings:freight:SubtourModeChoice']['weight'] = '0'

        self['transitRouter']['additionalTransferTime'] = '1'
        self['transitRouter']['extensionRadius'] = '100'
        self['transitRouter']['maxBeelineWalkConnectionDistance'] = '500'
        self['transitRouter']['searchRadius'] = '1000'


class BuildConfig(BaseConfig):

    def __init__(
            self,
            input_dir: Path = Path('inputs'),
            output_dir: Path = Path('outputs'),
            sample: float=0.01,
            subpops: Tuple[str]=('low', 'medium', 'high', 'default'),
            modes: Tuple[str]=('car', 'pt', 'bike', 'walk'),
            acts: Tuple[str]=('home', 'work', 'education', 'other')
    ):

        super().__init__()

        defaults_config = BaseConfig(path=get_default_path())

        default_mode_scoring = {
            'car': {
                'mut_hr': '-5',
                'mdr': '-0.0005'
            },
            'pt': {
                'mut_hr': '-5',
                'mdr': '-0.001'
            },
            'walk': {
                'mut_hr': '-12',
                'mdr': '0'
            },
            'bike': {
                'mut_hr': '-12',
                'mdr': '0'
            }
        }

        default_activity_scoring = {
            'home': {
                'typ_dur': '12:00:00',
                'min_dur': '08:00:00'
            },
            'work': {
                'typ_dur': '08:30:00',
                'min_dur': '08:00:00'
            },
            'education': {
                'typ_dur': '08:00:00',
                'min_dur': '06:00:00'
            },
            'depo': {
                'typ_dur': '12:00:00',
                'min_dur': '08:00:00'
            },
            'other': {
                'typ_dur': '00:15:00',
                'min_dur': '00:10:00'
            }
        }

        # build paths
        attributes_path = input_dir / 'attributes.xml.gz'
        plans_path = input_dir / 'plans.xml.gz'
        schedule_path = input_dir / 'schedule.xml.gz'
        vehicles_path = input_dir / 'vehicles.xml.gz'
        network_path = input_dir / 'network.xml.gz'

        # build config
        self['global'] = defaults_config['global']

        self['network']['inputNetworkFile'] = network_path.as_posix()

        self['plans']['inputPlansFile'] = plans_path.as_posix()
        self['plans']['inputPersonAttributesFile'] = attributes_path.as_posix()
        self['plans']['subpopulationAttributeName'] = 'subpopulation'

        self['transit']['useTransit'] = 'true'
        self['transit']['transitScheduleFile'] = schedule_path.as_posix()
        self['transit']['vehiclesFile'] = vehicles_path.as_posix()
        self['transit']['transitModes'] = 'pt'
        if 'pt' not in modes:
            raise UserWarning('Expected to see mode "pt"')

        self['TimeAllocationMutator']['mutationRange'] = '1000.0'

        self['controler'] = defaults_config['controler']
        self['controler']['outputDirectory'] = output_dir.as_posix()

        chained_modes = ['car', 'bike']
        config_chained_modes = [m for m in modes if m in chained_modes]
        chained_mode_str = ','.join(config_chained_modes)

        self['subtourModeChoice']['chainBasedModes'] = chained_mode_str
        self['subtourModeChoice']['modes'] = ','.join(modes)

        self['qsim']['startTime'] = '00:00:00'
        self['qsim']['endTime'] = '24:00:00'
        self['qsim']['flowCapacityFactor'] = str(sample)
        self['qsim']['storageCapacityFactor'] = str(sample)
        self['qsim']['mainMode'] = 'car,bus'
        self['qsim']['numberOfThreads'] = '32'

        self['planCalcScore']['BrainExpBeta'] = '1'

        for subpop in subpops:

            self['planCalcScore'][f'scoringParameters:{subpop}']['lateArrival'] = '-18'
            self['planCalcScore'][f'scoringParameters:{subpop}']['earlyDeparture'] = '-0.0'
            self['planCalcScore'][f'scoringParameters:{subpop}']['marginalUtilityOfMoney'] = '1'
            self['planCalcScore'][f'scoringParameters:{subpop}']['performing'] = '+6'
            self['planCalcScore'][f'scoringParameters:{subpop}']['subpopulation'] = subpop
            self['planCalcScore'][f'scoringParameters:{subpop}']['waiting'] = '-0'
            self['planCalcScore'][f'scoringParameters:{subpop}']['waitingPt'] = '-2'
            self['planCalcScore'][f'scoringParameters:{subpop}']['utilityOfLineSwitch'] = '-1'

            for mode in modes:
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['mode'] = mode
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}']['constant'] = '0'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}'][
                    'marginalUtilityOfDistance_util_m'] = '0'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}'][
                    'marginalUtilityOfTraveling_util_hr'] = default_mode_scoring.get(mode, default_mode_scoring['car'])['mut_hr']
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'modeParams:{mode}'][
                    'monetaryDistanceRate'] = default_mode_scoring.get(mode, default_mode_scoring['car'])['mdr']

            for act in acts:
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['activityType'] = act
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}']['priority'] = '1'
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}'][
                    'typicalDuration'] = default_activity_scoring.get(mode, default_activity_scoring['other'])['typ_dur']
                self['planCalcScore'][f'scoringParameters:{subpop}'][f'activityParams:{act}'][
                    'minimalDuration'] = default_activity_scoring.get(mode, default_activity_scoring['other'])['min_dur']

        self['strategy']['maxAgentPlanMemorySize'] = '5'

        for subpop in subpops:
            strategies = ['SubtourModeChoice', 'ReRoute', 'TimeAllocationMutator', 'ChangeExpBeta']
            weights = ['0.1', '0.1', '0.1', '0.7']
            for strategy, weight in zip(strategies, weights):
                self['strategy'][f'strategysettings:{subpop}:{strategy}']['strategyName'] = strategy
                self['strategy'][f'strategysettings:{subpop}:{strategy}']['subpopulation'] = subpop
                self['strategy'][f'strategysettings:{subpop}:{strategy}']['weight'] = weight

        if 'freight' in subpops:
            self['strategy']['strategysettings:freight:SubtourModeChoice']['weight'] = '0'

        self['transitRouter']['additionalTransferTime'] = '1'
        self['transitRouter']['extensionRadius'] = '100'
        self['transitRouter']['maxBeelineWalkConnectionDistance'] = '500'
        self['transitRouter']['searchRadius'] = '1000'


config_map = {
    'empty': Config,
    'test': TestConfig,
    'default': DefaultConfig,
}







