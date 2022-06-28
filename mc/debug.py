"""
Class inherited by BaseConfig for carrying out debugging.
"""
from prettytable import PrettyTable


class TEXT:
    TITLE = '\n\033[95m\033[4m\033[1m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warning(string: str):
    print(f"{TEXT.WARNING}{string}{TEXT.END}")


def fail(string: str):
    print(f"{TEXT.FAIL}{string}{TEXT.END}")


def check(string: str):
    print(f"{TEXT.OKBLUE}{string}{TEXT.END}")


def headed(head, text):
    print(f"{TEXT.HEADER}{head}{TEXT.END} {text}")


class BaseDebug:
    """
    Debugging Base class.
    """

    def get(self, key, default):
        raise NotImplementedError

    def summary(self):
        print(f"{TEXT.TITLE}Summary:{TEXT.END}")
        self.print_top()

        print(f"{TEXT.TITLE}Subpopulations:{TEXT.END}")
        for sub in self.get_subpopulations():
            print(f"\t{sub}")

        print(f"{TEXT.TITLE}Modes:{TEXT.END}")
        self.print_mode_table()
        self.print_modes()

        print(f"{TEXT.TITLE}Activities:{TEXT.END}")
        self.print_activity_table()

        print(f"{TEXT.TITLE}Strategies:{TEXT.END}")
        self.print_strategy_table()

    def debug(self):
        print(f"{TEXT.TITLE}Debug:{TEXT.END}")
        self.log_controler_module()
        self.log_version()
        self.log_subtour_mode_choice_module()
        self.log_transit_router_module()
        self.log_deterministic()
        self.log_inconsistent_iterations()
        self.log_parallel_event_handling()
        self.log_multimodal_module()
        self.log_bad_paths()
        self.log_subpopulation_consistency()
        self.log_missing_mode_scoring()
        self.log_plan_calc_scoring_module()

    # TOP

    def print_top(self):
        headed("CRS:", self.get('global', {}).get('coordinateSystem'))
        headed("Global threads:", self.get('global', {}).get('numberOfThreads'))
        headed("Event handling threads:", self.get('parallelEventHandling', {}).get('numberOfThreads'))
        headed("Flow scaling:", self.get('hermes', {}).get('flowCapacityFactor'))
        headed("Storage scaling:", self.get('hermes', {}).get('storageCapacityFactor'))
        controler = self.get('controler', {})
        headed("Iterations:", f"{controler.get('firstIteration')}->{controler.get('lastIteration')}")
        headed("Write events interval:", self.get('controler', {}).get('writeEventsInterval'))
        headed("Write plans interval:", self.get('controler', {}).get('writePlansInterval'))
        headed("Deterministic PT links interval:", self.get('SBBPt', {}).get('createLinkEventsInterval'))

    # SUBPOPULATIONS

    def get_subpopulations(self):
        subpops = set()
        for paramset in self['planCalcScore'].parametersets.values():
            subpops.add(paramset['subpopulation'])
        for paramset in self['strategy'].parametersets.values():
            subpops.add(paramset['subpopulation'])
        return subpops

    # MODES

    def get_modes(self):
        modes = set()
        modes.update(self.get_main_mode())
        modes.update(self.get_mode_choices())
        modes.update(self.get_chained_modes())
        modes.update(self.get_transit_modes())
        modes.update(self.get_deterministic_modes())
        modes.update(self.get_intermodal_access_egress_modes())
        modes.update(self.get_scoring_modes())
        return modes

    def print_modes(self):
        print(f"{TEXT.HEADER}Main mode:{TEXT.END} {self.get_main_mode()}")
        print(f"{TEXT.HEADER}Mode choices:{TEXT.END} {self.get_mode_choices()}")
        print(f"{TEXT.HEADER}Chained modes:{TEXT.END} {self.get_chained_modes()}")
        print(f"{TEXT.HEADER}Transit modes:{TEXT.END} {self.get_transit_modes()}")
        print(f"{TEXT.HEADER}Deterministic modes:{TEXT.END} {self.get_deterministic_modes()}")
        print(f"{TEXT.HEADER}Access/egress modes:{TEXT.END} {self.get_intermodal_access_egress_modes()}")
        print(f"{TEXT.HEADER}Passenger mode mapping:{TEXT.END} {self.get_mapped_passenger_modes()}")
        print(f"{TEXT.HEADER}Scored modes:{TEXT.END} {self.get_scoring_modes()}")

    def get_main_mode(self) -> set:
        return {self.get("hermes", self.get("qsim", {})).get("mainMode", set())}

    def get_mode_choices(self) -> set:
        # TODO not sure if subtourModeChoice are network or passenger modes?
        # TODO ie do they need to be mapped?
        modes = set()
        if "subtourModeChoice" not in self:
            return modes
        # look for modes in subtourModeChoice module
        modes.update(self['subtourModeChoice']['modes'].split(','))
        self.apply_mode_passenger_mapping(modes)
        return modes

    def get_chained_modes(self) -> set:
        # TODO not sure if subtourModeChoice are network or passenger modes?
        # TODO ie do they need to be mapped?
        modes = set()
        if "subtourModeChoice" not in self:
            return modes
        # look for modes in subtourModeChoice module
        modes.update(self['subtourModeChoice']['chainBasedModes'].split(','))
        self.apply_mode_passenger_mapping(modes)
        return modes

    def get_transit_modes(self) -> set:
        # TODO not sure if transit are network or passenger modes?
        # TODO ie do they need to be mapped?
        modes = set()
        if not self.get("transit", {}).get("transitModes"):
            return modes
        # look for modes in subtourModeChoice module
        modes.update(self['transit']['transitModes'].split(','))
        self.apply_mode_passenger_mapping(modes)
        return modes

    def get_deterministic_modes(self) -> set:
        modes = set()
        if not self.get("SBBPt", {}).get("deterministicServiceModes"):
            return modes
        # look for modes in SBBPt module
        modes.update(self['SBBPt']['deterministicServiceModes'].split(','))
        return modes

    def get_intermodal_access_egress_modes(self) -> set:
        modes = set()
        if "swissRailRaptor" not in self:
            return modes
        for _, paramset in self['swissRailRaptor'].parametersets.items():
            if paramset.type == "intermodalAccessEgress":
                modes.add(paramset['mode'])
        return modes

    def get_mapped_passenger_modes(self) -> set:
        modes = set()
        if "swissRailRaptor" not in self:
            return modes
        for _, paramset in self['swissRailRaptor'].parametersets.items():
            if paramset.type == "modeMapping":
                modes.add(f"{paramset['routeMode']}->{paramset['passengerMode']}")
        return modes

    def get_scoring_modes(self) -> set:
        modes = set()
        if "planCalcScore" not in self:
            return modes
        for subpop_paramset in self['planCalcScore'].parametersets.values():
            for paramset in subpop_paramset.parametersets.values():
                if paramset.get("mode"):
                    modes.add(paramset.get("mode"))
        return modes

    def print_mode_table(self):
        print(self.get_mode_table())

    def get_mode_table(self) -> PrettyTable:
        if "planCalcScore" not in self:
            return None
        modes = sorted(list(self.get_modes()))
        subpopulations = list(self.get_subpopulations())
        table = PrettyTable()
        table.field_names = ["Mode"] + subpopulations
        for mode in modes:
            row = []
            missing = 0
            for subpopulation in subpopulations:
                if self['planCalcScore'].get(f"scoringParameters:{subpopulation}", {}).get(f"modeParams:{mode}"):
                    row.append("\033[92m✔\033[0m")
                else:
                    row.append("\033[1m\033[91m○\033[0m")
                    missing += 1
            if missing == 0:
                row = [f"\033[92m{mode}\033[0m"] + row
            elif missing == len(subpopulations):
                row = [f"\033[1m\033[91m{mode}\033[0m"] + row
            else:
                row = [f"\033[1m\033[93m{mode}\033[0m"] + row
            table.add_row(row)
        table.align["Mode"] = "r"
        return table

    def apply_mode_passenger_mapping(self, modes):
        if 'swissRailRaptor' in self:
            for _, paramset in self['swissRailRaptor'].parametersets.items():
                if paramset.type == "modeMapping":
                    if not paramset["routeMode"] in modes:
                        continue
                    modes.remove(paramset["routeMode"])
                    modes.add(paramset['passengerMode'])

    # ACTIVITIES

    def get_activities(self) -> set:
        activities = set()
        if "planCalcScore" not in self:
            return activities
        for subpop_paramset in self['planCalcScore'].parametersets.values():
            for paramset in subpop_paramset.parametersets.values():
                if paramset.get("activityType"):
                    activities.add(paramset.get("activityType"))
        return activities

    def print_activity_table(self):
        print(self.get_activity_table())

    def get_activity_table(self) -> PrettyTable:
        if "planCalcScore" not in self:
            return None
        activities = sorted(list(self.get_activities()))
        subpopulations = list(self.get_subpopulations())
        table = PrettyTable()
        table.field_names = ["Activity"] + subpopulations
        for act in activities:
            row = []
            missing = 0
            for subpopulation in subpopulations:
                if self['planCalcScore'].get(f"scoringParameters:{subpopulation}", {}).get(f"activityParams:{act}"):
                    row.append("\033[92m✔\033[0m")
                else:
                    row.append("\033[1m\033[91m○\033[0m")
                    missing += 1
            if missing == 0:
                row = [f"\033[92m{act}\033[0m"] + row
            elif missing == len(subpopulations):
                row = [f"\033[1m\033[91m{act}\033[0m"] + row
            else:
                row = [f"\033[1m\033[93m{act}\033[0m"] + row
            table.add_row(row)
        table.align["Activity"] = "r"
        return table

    # STRATEGIES

    def get_strategies(self) -> set:
        strategies = set()
        if "strategy" not in self:
            return strategies
        for paramset in self['strategy'].parametersets.values():
            if paramset.get("strategyName"):
                strategies.add(paramset.get("strategyName"))
        return strategies

    def print_strategy_table(self):
        print(self.get_strategy_table())

    def get_strategy_table(self) -> PrettyTable:
        if "strategy" not in self:
            return None
        strategies = sorted(list(self.get_strategies()))
        subpopulations = list(self.get_subpopulations())
        table = PrettyTable()
        table.field_names = ["Strategy"] + subpopulations
        for strat in strategies:
            row = []
            missing = 0
            for subpopulation in subpopulations:
                if self['strategy'].get(f"strategysettings:{subpopulation}:{strat}"):
                    weight = self["strategy"].get(f"strategysettings:{subpopulation}:{strat}", {})["weight"]
                    row.append(f"\033[92m{weight}\033[0m")
                else:
                    row.append("\033[1m\033[91m○\033[0m")
                    missing += 1
            if missing == 0:
                row = [f"\033[92m{strat}\033[0m"] + row
            elif missing == len(subpopulations):
                row = [f"\033[1m\033[91m{strat}\033[0m"] + row
            else:
                row = [f"\033[1m\033[93m{strat}\033[0m"] + row
            table.add_row(row)
        table.align["Strategy"] = "r"
        return table

    # MODULES

    def log_version(self):
        if self.get("plans", {}).get("inputPersonAttributesFile"):
            check(
                "VERSION: you have specified an input 'inputPersonAttributesFile',"
                "this is an old version (<12)."
                )
            if self["plans"].get("insistingOnUsingDeprecatedPersonAttributeFile") == "true":
                warning(
                    "VERSION: if you wish to use an 'inputPersonAttributesFile', "
                    "you must set 'insistingOnUsingDeprecatedPersonAttributeFile' to 'true'."
                    )

    def log_controler_module(self):
        """
        check controler is defined and hermes is being used.
        :return list
        """
        if "controler" not in self:
            fail("MISSING MODULE: no controler module defined (note that it is spelt with and single 'l'.")
        if not self.get("controler", {}).get("mobsim") == "hermes":
            check("CONTROLER MODULE: recommended you use the 'hermes' mobsim.")

    def log_deterministic(self):
        if not self.get("hermes", {}).get("useDeterministicPt") == "true":
            check("DETERMINISTIC: recommend you configure 'useDeterministicPt' as 'true' in the 'hermes' module.")
            return None
        if not self.get("SBBPt", {}).get("deterministicServiceModes"):
            check("DETERMINISTIC: cannot find deterministic modes definition.")
            return None
        scoring_modes = self.get_scoring_modes()
        deterministic_modes = self.get_deterministic_modes()
        missing_scoring = scoring_modes - deterministic_modes
        if missing_scoring:
            check(f"CHECK DETERMINISTIC MODES: {missing_scoring} not defined as deterministic.")

    def log_subtour_mode_choice_module(self):
        logger = []
        if 'SubtourModeChoice' in self:
            fail(
                "BAD MODULE SPELLING: 'SubtourModeChoice' => 'subtourModeChoice'"
            )
        if 'subtourModeChoice' not in self:
            fail(
                "MISSING MODULE: 'subtourModeChoice' module not found"
            )
        elif 'modes' not in list(self['subtourModeChoice'].params):
            warning(
                "MISSING PARAM: 'modes' param not found in: subtourModeChoice"
            )
        return logger

    def log_transit_router_module(self):
        if self.get("transitRouter", {}).get("maxBeelineWalkConnectionDistance") is None:
            check(
                "CHECK: 'maxBeelineWalkConnectionDistance' not defined in 'transitRouter' module, "
                "using default may limit interchanges."
                )
            return None
        distance = self["transitRouter"]["maxBeelineWalkConnectionDistance"]
        check(f"CHECK: 'maxBeelineWalkConnectionDistance' is set to {distance}, this may limit interchanges.")

    def log_inconsistent_iterations(self):
        first = self.get('controler', {}).get('firstIteration')
        if not first:
            fail("ITERATIONS: please define firstIteration in controler module")
        last = self.get('controler', {}).get('lastIteration')
        if not last:
            fail("ITERATIONS: please define lastIteration in controler module")

        events = self.get('controler', {}).get('writeEventsInterval')
        plans = self.get('controler', {}).get('writePlansInterval')
        links = self.get('SBBPt', {}).get('createLinkEventsInterval')
        if not last == events == plans == links:
            check(
                "CHECK: recommend setting 'writwriteEventsInterval', 'writePlansInterval' "
                "and 'createLinkEventsInterval' to 'finalIteration'."
                )

    def log_parallel_event_handling(self):
        estimated_events = self.get("parallelEventHandling", {}).get("estimatedNumberOfEvents")
        if estimated_events is None or estimated_events == "null":
            check(
                "CHECK: recommend setting 'estimatedNumberOfEvents' in 'parallelEventHandling' "
                "module to something high for big sims."
                )

    def log_multimodal_module(self):
        if self.get('multimodal'):

            modes = self['multimodal']['simulatedModes'].split(",")

            if (not self['multimodal'].get('createMultiModalNetwork'))\
                    or self['multimodal']['createMultiModalNetwork'] != "true":
                warning(
                    f"MULTIMODAL: auto multimodal network disabled, input network must "
                    f"include all modes: {modes}"
                    )

            if not self.get('travelTimeCalculator'):
                fail("MULTIMODAL: multimodal module requires travelTimeCalculator module")

            else:
                if not self['travelTimeCalculator'].get('analyzedModes'):
                    fail(
                        "MULTIMODAL: multimodal module requires list of modes at analyzedModes@travelTimeCalculator")

                if not self['travelTimeCalculator'].get('filterModes') == 'true':
                    fail(
                        "MULTIMODAL: multimodal module requires filterModes@travelTimeCalculator set to 'true'")

                if not self['travelTimeCalculator'].get('separateModes') == 'false':
                    fail(
                        "MULTIMODAL: multimodal module requires separateModes@travelTimeCalculator set to 'false'")

            for m in modes:
                if not self['planscalcroute'].get(f'teleportedModeParameters:{m}'):
                    fail(
                        f"MULTIMODAL: depending on the MATSim version, multimodal module requires "
                        f"mode:{m} teleport speed to be set in planscalcroute module.")

    # PATHS

    def log_bad_paths(self):
        """
        Build a list of debug messages for bad paths.
        :return: list
        """
        for name, path in self.paths().items():
            check_path(name, path)

    def paths(self) -> dict:
        """
        Build a dict of paths from config.
        :return: dict
        """
        return {
            'network_path': self.get('network', {}).get('inputNetworkFile', None),
            'plans_path': self.get('plans', {}).get('inputPlansFile', None),
            'transit_path': self.get('transit', {}).get('transitScheduleFile', None),
            'transit_vehicles_path': self.get('transit', {}).get('vehiclesFile', None),
        }

    # OTHER

    def log_subpopulation_consistency(self):
        # Scoring:
        scoring_subpops = []
        for paramset in self['planCalcScore'].parametersets.values():
            scoring_subpops.append(paramset['subpopulation'])

        # check for default
        if "default" not in scoring_subpops:
            fail("MISSING SUBPOP: 'default' subpopulation must be configures in planCalcScore.")

        # check for duplicates
        for s in scoring_subpops:
            if scoring_subpops.count(s) > 1:
                warning(f"SUBPOP:{s} defined more than once in planCalcScore")

        # check for default
        if 'default' not in scoring_subpops:
            fail("SUBPOP default subpop missing from planCalcScore")

        # Strategy:
        strategy_subpops = []
        for paramset in self['strategy'].parametersets.values():
            strategy_subpops.append(paramset['subpopulation'])

        # check for duplicates
        for s in strategy_subpops:
            if scoring_subpops.count(s) > 1:
                warning(f"SUBPOP:{s} defined more than once in strategy")

        # check equal
        missing_scoring = set(strategy_subpops) - set(scoring_subpops)
        if missing_scoring:
            warning(f"SUBPOP {missing_scoring} subpop missing from planCalcScore")

        missing_strategy = set(scoring_subpops) - set(strategy_subpops) - set(['default'])
        if missing_strategy:
            warning(f"SUBPOP {missing_strategy} subpop missing from strategy")

    def log_plan_calc_scoring_module(self):
        # Scoring:
        scoring_modes = {}
        scoring_acts = {}

        for subpop_paramset in self['planCalcScore'].parametersets.values():
            subpop_modes = []
            subpop_acts = []
            subpop_mode_cost = {}
            subpopulation = subpop_paramset['subpopulation']
            mum = float(subpop_paramset['marginalUtilityOfMoney'])
            performing = float(subpop_paramset['performing'])

            # check for possitive
            if mum < 0:
                warning(f"WARNING: {subpopulation} marginal utility of money is negative: {mum}")
            if performing < 0:
                warning(f"WARNING: {subpopulation} value of performing is negative: {performing}")

            for paramset in subpop_paramset.parametersets.values():
                mode = paramset.get("mode")
                act = paramset.get("activityType")
                if mode:
                    subpop_modes.append(mode)
                    dist_cost_rate = float(paramset.get('monetaryDistanceRate'))
                    dist_util_rate = float(paramset.get('marginalUtilityOfDistance_util_m'))
                    hour_util_rate = float(paramset.get('marginalUtilityOfTraveling_util_hr'))

                    # check for possitive costs
                    if dist_cost_rate > 0:
                        warning(f"WARNING: {subpopulation} {mode} monetary distance rate is positive: {dist_cost_rate}")
                    if dist_util_rate > 0:
                        warning(f"WARNING: {subpopulation} {mode} util distance rate is positive: {dist_util_rate}")
                    if hour_util_rate > 0:
                        warning(f"WARNING: {subpopulation} {mode} hourly util rate is positive: {hour_util_rate}")

                    subpop_mode_cost[mode] = calc_cost(
                        dist_cost_rate, mum, dist_util_rate, hour_util_rate, performing, mode
                    )
                if act:
                    subpop_acts.append(act)

            # check for duplicates
            log_duplicates(subpop_modes, 'DUPLICATE MODES SCORING', subpopulation)
            log_duplicates(subpop_acts, 'DUPLICATE ACTIVITIES SCORING', subpopulation)

            # compare cost to walking
            log_cost_comparison(subpop_mode_cost, 'MODE COST', subpopulation)

            scoring_modes[subpopulation] = subpop_modes
            scoring_acts[subpopulation] = subpop_acts

        # check for consistency
        all_modes = set([m for ml in scoring_modes.values() for m in ml])
        all_acts = set([a for al in scoring_acts.values() for a in al])
        for subpopulation, ml in scoring_modes.items():
            log_consistency(ml, all_modes, 'INCONSISTENT MODES SCORING', subpopulation)
        for subpopulation, al in scoring_acts.items():
            log_consistency(al, all_acts, 'INCONSISTENT ACTIVITIES SCORING', subpopulation)

    def log_missing_mode_scoring(self):
        # build set of observed modes from config
        all_modes = self.get_mode_choices()
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
                    fail(
                        f"MISSING MODE SCORING: {_mode} not found in: planCalcScore:{subpopulation}"
                    )


def check_path(name: str, path: str) -> bool:
    """
    Build diff for bad path.
    :param name: str
    :param path: str
    :return: str
    """
    if not path:
        fail(f"MISSING PATH: {name}")
        return False
    if not (path[-4:] == '.xml' or path[-7:] == '.xml.gz'):
        fail(f"UNRECOGNISED EXTENSION: {name}: {path}, expecting '.xml(.gz)'")
        return False
    return True


def log_duplicates(targets: list, log_type: str, location: str) -> None:
    """
    :param targets: list
    :param log_type: str
    :param location: str
    :return: None
    """
    for t in list(set(targets)):
        if targets.count(t) > 1:
            warning(f"{log_type}:{t} defined more than once in: {location}")


def log_consistency(targets, master, log_type, location):
    missing_scoring = set(master) - set(targets)
    if missing_scoring:
        check(f"{log_type}: {missing_scoring} missing in: {location}")


def log_cost_comparison(costs, log_type, location):
    walk_cost = costs.get('walk')
    if not walk_cost:
        warning(f"{log_type}: walking mode not found in: {location}")
    for mode, cost in costs.items():
        if mode == 'walk':
            continue
        if walk_cost and (cost < walk_cost):  # (if more negative)
            check(f"{log_type}: {mode} may be more expensive than walking: {location}")


def calc_cost(dist_cost_rate, mum, dist_util_rate, hour_util_rate, performing, mode):

    speed_map = {  # m/saaa
        'bike': 3,
        'piggyback': 0.6,
        'walk': 0.83,
        'gondola': 0.83,
        'access_walk': 0.83,
        'egress_walk': 0.83,
        'pt': 10,
        'car': 10,  # approx 40km/hr
        'bus': 8,
        'tram': 8,
        'train': 10,
        'rail': 15,
        'subway': 15,
        'metro': 15,
        'ferry': 10
    }
    if mode not in list(speed_map):
        warning(f"WARNING: {mode} mode speed unknown, approximating as car speed: {speed_map['car']}")
        mode = 'car'  # default to car speed

    dist_cost = (dist_cost_rate * mum) + dist_util_rate  # utils/m
    time_cost = (hour_util_rate - performing) / (speed_map[mode] * 3600)  # converted to utils/m
    return dist_cost + time_cost  # utils/m
