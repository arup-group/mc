"""
Class inherited by BaseConfig for carrying out debugging.
"""
from typing import Tuple


class BaseDebug:
    """
    Debugging Base class.
    """

    def get(self, key, default):
        raise NotImplementedError

    def debug(self, verbose=True) -> Tuple[bool, list]:
        """
        Build a list of debug messages.
        :param verbose: bool
        :return: tuple[bool, list]
        """
        logger = list()
        logger.extend(self.log_multimodal_module())
        logger.extend(self.log_bad_paths())
        logger.extend(self.log_bad_subpopulations())
        logger.extend(self.log_bad_scoring())
        logger.extend(self.log_missing_modes())

        if verbose and len(logger):
            print('\n---------WARNING--------')
            for log in logger:
                print(log)
            print('----------DONE----------')

        return len(logger) < 1, logger

    def log_multimodal_module(self) -> list:
        """
        Report if multimodal module may be being used incorrectly.
        :return: list
        """
        logger = []
        if self.get('multimodal'):

            modes = self['multimodal']['simulatedModes'].split(",")

            if (not self['multimodal'].get('createMultiModalNetwork'))\
                    or self['multimodal']['createMultiModalNetwork'] != "true":
                logger.append(f"MULTIMODAL: auto multimodal network disabled, input network must "
                              f"include all modes: {modes}")

            if not self.get('travelTimeCalculator'):
                logger.append(f"MULTIMODAL: multimodal module requires travelTimeCalculator module")

            else:
                if not self['travelTimeCalculator'].get('analyzedModes'):
                    logger.append(
                        f"MULTIMODAL: multimodal module requires "
                        f"list of modes at analyzedModes@travelTimeCalculator")

                if not self['travelTimeCalculator'].get('filterModes') == 'true':
                    logger.append(
                        f"MULTIMODAL: multimodal module requires filterModes@travelTimeCalculator"
                        f" set to 'true'")

                if not self['travelTimeCalculator'].get('separateModes') == 'false':
                    logger.append(
                        f"MULTIMODAL: multimodal module requires separateModes@travelTimeCalculator"
                        f" set to 'false'")

            for m in modes:
                if not self['planscalcroute'].get(f'teleportedModeParameters:{m}'):
                    logger.append(
                        f"MULTIMODAL: depending on the MATSim version, multimodal module requires "
                        f"mode:{m} teleport speed to be set in planscalcroute module.")

        return logger

    def log_bad_paths(self) -> list:
        """
        Build a list of debug messages for bad paths.
        :return: list
        """
        logger = []
        for name, path in self.get_paths().items():
            log = bad_path(name, path)
            if log:
                logger.append([log])

        return logger

    def get_paths(self) -> dict:
        """
        Build a dict of paths from config.
        :return: dict
        """
        return {
            'network_path': self['network']['inputNetworkFile'],
            'plans_path': self['plans']['inputPlansFile'],
            'attributes_path': self['plans']['inputPersonAttributesFile'],
            'transit_path': self['transit']['transitScheduleFile'],
            'transit_vehicles_path': self['transit']['vehiclesFile'],
        }

    def log_bad_subpopulations(self) -> list:
        """
        Build a list of debug messages for bad subpopulations.
        :return: list
        """
        logger = []

        # Scoring:
        scoring_subpops = []
        for paramset in self['planCalcScore'].parametersets.values():
            scoring_subpops.append(paramset['subpopulation'])

        # check for duplicates
        for s in scoring_subpops:
            if scoring_subpops.count(s) > 1:
                logger.append(f"SUBPOP:{s} defined more than once in planCalcScore")

        # check for default
        if not 'default' in scoring_subpops:
            logger.append(f"SUBPOP default subpop missing from planCalcScore")

        # Strategy:
        strategy_subpops = []
        for paramset in self['strategy'].parametersets.values():
            strategy_subpops.append(paramset['subpopulation'])

        # check for duplicates
        for s in strategy_subpops:
            if scoring_subpops.count(s) > 1:
                logger.append(f"SUBPOP:{s} defined more than once in strategy")

        # check equal
        missing_scoring = set(strategy_subpops) - set(scoring_subpops)
        if missing_scoring:
            logger.append(f"SUBPOP {missing_scoring} subpop missing from planCalcScore")

        missing_strategy = set(scoring_subpops) - set(strategy_subpops) - set(['default'])
        if missing_strategy:
            logger.append(f"SUBPOP {missing_strategy} subpop missing from strategy")

        return logger

    def log_bad_scoring(self) -> list:
        """
        Build a list of debug messages for bad scoring.
        :return: list
        """
        logger = []

        # Scoring:
        scoring_modes = {}
        scoring_acts = {}

        for subpop_paramset in self['planCalcScore'].parametersets.values():
            subpop_modes = []
            subpop_acts = []
            subpop_mode_cost = {}
            subpopulation = subpop_paramset['subpopulation']
            mum = subpop_paramset['marginalUtilityOfMoney']

            for paramset in subpop_paramset.parametersets.values():
                mode = paramset.get("mode")
                act = paramset.get("activityType")
                if mode:
                    subpop_modes.append(mode)
                    dist_cost_rate = paramset.get('monetaryDistanceRate')
                    dist_util_rate = paramset.get('marginalUtilityOfDistance_util_m')
                    hour_util_rate = paramset.get('marginalUtilityOfTraveling_util_hr')
                    subpop_mode_cost[mode] = calc_cost(
                        logger, dist_cost_rate, mum, dist_util_rate, hour_util_rate, mode
                    )
                if act:
                    subpop_acts.append(act)

            # check for duplicates
            log_duplicates(logger, subpop_modes, 'MODES', subpopulation)
            log_duplicates(logger, subpop_acts, 'ACTIVITIES', subpopulation)

            # compare cost to walking
            log_cost_comparison(logger, subpop_mode_cost, 'MODE COST', subpopulation)

            scoring_modes[subpopulation] = subpop_modes
            scoring_acts[subpopulation] = subpop_acts

        # check for consistency
        all_modes = set([m for ml in scoring_modes.values() for m in ml])
        all_acts = set([a for al in scoring_acts.values() for a in al])
        for subpopulation, ml in scoring_modes.items():
            log_consistency(logger, ml, all_modes, 'MODES', subpopulation)
        for subpopulation, al in scoring_acts.items():
            log_consistency(logger, al, all_acts, 'ACTIVITIES', subpopulation)

        return logger

    def log_missing_modes(self) -> list:
        """
        build debug messages for missing modes.
        :return: list
        """
        logger = []

        # build set of observed modes from config
        all_modes = set()

        # look for modes in qsim module
        # if 'qsim' not in self:
        #     logger.append(
        #         "MISSING MODULE: 'qsim' module not found"
        #     )
        # elif 'mainMode' not in list(self['qsim'].params):
        #     logger.append(
        #         "MISSING MODES: 'mainMode' param not found in: qsim"
        #     )
        # else:
        #     all_modes.update(self['qsim']['mainMode'].split(','))

        # look for modes in subtourModeChoice module
        if 'SubtourModeChoice' in self:
            logger.append(
                "BAD MODULE SPELLING: 'SubtourModeChoice' => 'subtourModeChoice'"
            )
        if 'subtourModeChoice' not in self:
            logger.append(
                "MISSING MODULE: 'subtourModeChoice' module not found"
            )
        elif 'modes' not in list(self['subtourModeChoice'].params):
            logger.append(
                "MISSING MODES: 'modes' param not found in: subtourModeChoice"
            )
        else:
            all_modes.update(self['subtourModeChoice']['modes'].split(','))

        if 'swissRailRaptor' in self:
            all_modes.add('pt')
            for name, paramset in self['swissRailRaptor'].parametersets.items():
                if 'passengerMode' in paramset.params:
                    all_modes.add(paramset['passengerMode'])

        # # look for modes in planscalcroute module
        # if 'planscalcroute' not in self:
        #     logger.append(
        #         "MISSING MODULE: 'planscalcroute' module not found - need 'access_walk' config"
        #     )

        #     # Additionally check that access walk has been set up in plancalcroute
        #     if 'teleportedModeParameters:access_walk' not in list(
        #             self['planscalcroute'].parametersets
        #     ):
        #         logger.append(f"MISSING MODE: access_walk mode not found in: planscalcroute")

        # elif 'networkModes' in list(self['planscalcroute'].params):
        #     all_modes.update(self['planscalcroute']['networkModes'].split(','))

        all_modes.update(['access_walk'])

        # check for scoring configuration of all modes across all subpopulations
        modes = []
        for subpop_paramset in self['planCalcScore'].parametersets.values():
            subpopulation = subpop_paramset['subpopulation']
            for paramset in subpop_paramset.parametersets.values():
                mode = paramset.get("mode")
                if mode:
                    modes.append(mode)
            for _mode in all_modes:
                if _mode not in modes:
                    logger.append(
                        f"MISSING MODE SCORING: {_mode} not found in: planCalcScore:{subpopulation}"
                    )

        return logger


def bad_path(name: str, path: str) -> str:
    """
    Build diff for bad path.
    :param name: str
    :param path: str
    :return: str
    """
    if not path:
        return f"PATH: missing {name}"
    if not (path[-4:] == '.xml' or path[-7:] == '.xml.gz'):
        return f"PATH: unknown extension {name, path}"

    return None


def log_duplicates(logger: list, targets: list, log_type: str, location: str) -> None:
    """
    Add diffs to logger for duplicated items in list.
    :param logger: list
    :param targets: list
    :param log_type: str
    :param location: str
    :return: None
    """
    for t in list(set(targets)):
        if targets.count(t) > 1:
            logger.append(f"{log_type}:{t} defined more than once in: {location}")


def log_consistency(logger, targets, master, log_type, location):
    missing_scoring = set(master) - set(targets)
    if missing_scoring:
        logger.append(f"{log_type} {missing_scoring} missing in: {location}")


def log_cost_comparison(logger, costs, log_type, location):
    walk_cost = costs.get('walk')
    if not walk_cost:
        logger.append(f"{log_type}: walking mode not found in: {location}")
    for mode, cost in costs.items():
        if mode == 'walk':
            continue
        if walk_cost and cost < walk_cost:
            logger.append(f"{log_type}: {mode} may be more expensive than walking: {location}")


def calc_cost(logger, dist_cost_rate, mum, dist_util_rate, hour_util_rate, mode):

    speed_map = {
        'bike': 4.2,
        'piggyback': 0.6,
        'walk': 0.83,
        'access_walk': 0.83,
        'egress_walk': 0.83,
        'pt': 10,
        'car': 10
    }
    if mode not in list(speed_map):
        logger.append(f"WARNING: {mode} mode speed unknown, approximating as car speed: {speed_map['car']}")
        mode = 'car'  # default to car speed
    dist_cost = (float(dist_cost_rate) * float(mum)) + float(dist_util_rate)
    time_cost = float(hour_util_rate) / (speed_map[mode] * 3600)
    return dist_cost + time_cost





