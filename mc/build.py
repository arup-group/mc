from mc.base import _Config, Module, ParamSet, Param
import os
from . import get_default_path
from pathlib import Path
from typing import List


class Config(_Config):

    print("Initiated empty config")


class DefaultConfig(Config):

    def __init__(self):
        super().__init__(path=get_default_path())


class BuildConfig(Config):

    def __init__(
            self,
            input_dir: Path,
            output_dir: Path,
            subpops=List[str],
            modes=List[str],
            acts=List[str]
    ):

        super().__init__()

        defaults_config = Config(path=get_default_path())

        # build paths
        attributes_path = input_dir / 'attributes.xml.gz'
        plans_path = input_dir / 'plans.xml.gz'
        schedule_path = input_dir / 'schedule.xml.gz'
        vehciles_path = input_dir / 'vehicles.xml.gz'

        # JDEQSim module
        self['JDEQSim'] = defaults_config['JDEQSim']  # TODO flow capacity factor????

        # controler
        self['controler'] = Module(name='controler')
        self['controler']['lastIteration'] = '100'
        self['controler']['mobsim'] = 'qsim'
        self['controler']['outputDirectory'] = output_dir.as_posix()



        # set dir
        #
        # self['plans']['inputPersonAttributesFile'] = attributes_path.as_posix()
        # self['plans']['inputPlansFile'] = plans_path.as_posix()
        # self['transit']['transitScheduleFile'] = schedule_path.as_posix()
        # self['transit']['vehiclesFile'] = vehciles_path.as_posix()

        # scoring default



        # if not input_dir
        #
        # if not modes:
        #     modes = ['car', 'pt', 'bike', 'walk',]
        # if not acts:
        #     acts = ['home', 'work', 'education', 'other',]
        # if not subpops:
        #     subpops = ['default',]
        # elif not 'default' in subpops:
        #     subpops += ['default']

        # build









