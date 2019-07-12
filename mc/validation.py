

def bad_path(name, path):
    if not path:
        return f"PATH: missing {name}"
    if not (path[-4:] == '.xml' or path[-7:] == '.xml.gz'):
        return f"PATH: unknown extension {name, path}"


class BuildValidator:

    def is_valid(self):
        logger = list()
        logger.append(self.has_bad_paths())
        logger.append(self.has_bad_subpopulations())

        return len(logger) < 1, logger

    def log_bad_paths(self):

        logger = []
        for name, path in self.get_paths().items():
            log = bad_path(name, path)
            if log:
                logger.append([log])

        return logger

    def get_paths(self):

        return {
            'network_path': self['network']['inputNetworkFile'],
            'plans_path': self['plans']['inputPlansFile'],
            'attributes_path': self['plans']['inputPersonAttributesFile'],
            'transit_path': self['transit']['transitScheduleFile'],
            'transit_vehicles_path': self['transit']['vehiclesFile'],
        }

    def log_bad_subpopulations(self):

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

    def log_bad_scoring(self):

        logger = []

        change_modes = self['changeMode']['modes'].split(',')
        qsim_main_modes = self['qsim']['mainMode'].split(',')
        network_modes = self['planscalcroute']['networkModes'].split(',')

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
                        dist_cost_rate, mum, dist_util_rate, hour_util_rate, mode
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


def log_duplicates(logger, targets, log_type, location):
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
        if cost < walk_cost:
            logger.append(f"{log_type}: {mode} may be more expensive than walking: {location}")


def calc_cost(dist_cost_rate, mum, dist_util_rate, hour_util_rate, mode):

    speed_map = {
        'bike': 4.2,
        'walk': 0.83,
        'pt': 10,
        'car': 10
    }
    if mode not in list(speed_map):
         return None
    dist_cost = (float(dist_cost_rate) * float(mum)) + float(dist_util_rate)
    time_cost = float(hour_util_rate) / (speed_map[mode] * 3600)
    return dist_cost + time_cost





