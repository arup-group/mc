from pathlib import Path

"""
Dictionary of valid config names for modules, paramsets and params.
"""


class ValidParam:
    def __init__(self, default):
        self.default = default
        self.value = default

    @staticmethod
    def is_valid(value):
        raise NotImplementedError


class Str(ValidParam):
    __name__ = 'Str'

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        return isinstance(value, str)


class ValidPath(ValidParam):
    __name__ = 'ValidPath'

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        if value in ["null", "undefined"]:
            return True

        try:
            Path(value)
            return True
        except ValueError:
            return False


class Int(ValidParam):
    __name__ = 'Int'

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        if value in ["null", "undefined"]:
            return True

        try:
            int(value)
            return True
        except ValueError:
            return False


class Float(ValidParam):
    __name__ = 'Float'

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        if value in ["null", "undefined"]:
            return True

        try:
            float(value)
            return True
        except ValueError:
            return False


class Bool(ValidParam):
    __name__ = "'true','false'"

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        return value in ['true', 'false']


class Time(ValidParam):
    __name__ = "{hh:mm:ss}"

    def __init__(self, default):
        super().__init__(default)

    @staticmethod
    def is_valid(value):
        if value in ["null", "undefined"]:
            return True

        try:
            [int(v) for v in value.split(':')]
            return True
        except ValueError:
            return False


VALID_MAP = {

    "modules": {

        "global": {
                "params": {
                    "coordinateSystem": Str("EPSG:27700"),
                    "numberOfThreads": Int("32"),
                    "randomSeed": Int("4711"),
                    "insistingOnDeprecatedConfigVersion": Bool("true"),
                }
            },

        "network": {
            "params": {
                "inputCRS": Str("null"),
                "inputChangeEventsFile": Str("null"),
                "inputNetworkFile": ValidPath("./output_network.xml.gz"),
                "laneDefinitionsFile": Str("null"),
                "timeVariantNetwork": Bool("false"),
            }
        },

        "plans": {
            "params": {
                "inputPlansFile": ValidPath("./output_plans.xml.gz"),
                "inputPersonAttributesFile": ValidPath("./output_personAttributes.xml.gz"),
                "subpopulationAttributeName": Str("subpopulation"),
                "activityDurationInterpretation": Str("tryEndTimeThenDuration"),
                "inputCRS": Str("null"),
                "networkRouteType": Str("LinkNetworkRoute"),
                "removingUnnecessaryPlanAttributes": Bool("false"),
            }
        },

        "transit": {
            "params": {
                "useTransit": Bool("true"),
                "transitScheduleFile": ValidPath("./output_transitSchedule.xml.gz"),
                "vehiclesFile": ValidPath("./output_transitVehicles.xml"),
                "inputScheduleCRS": Str("null"),
                "transitLinesAttributesFile": ValidPath("null"),
                "transitModes": Str("pt"),
                "transitStopsAttributesFile": ValidPath("null"),
            }
        },

        "multimodal": {
            "params": {
                "createMultiModalNetwork": Bool("true"),
                "numberOfThreads": Int("1"),
                "cuttoffValueForNonCarModes": Float("25.0"),
                "dropNonCarRoutes": Bool("true"),
                "multiModalSimulationEnabled": Bool("true"),
                "simulatedModes": Str("walk,bike"),
                "ensureActivityReachability": Bool("true"),
            }
        },

        "travelTimeCalculator": {
            "params": {
                "analyzedModes": Str("car,bus,walk"),
                "filterModes": Bool("true"),
                "separateModes": Bool("false"),
                "calculateLinkToLinkTravelTimes": Bool("false"),
                "calculateLinkTravelTimes": Bool("true"),
                "maxTime": Int("108000"),
                "travelTimeAggregator": Str("optimistic"),
                "travelTimeBinSize": Int("900"),
                "travelTimeCalculator": Str("TravelTimeCalculatorArray"),
                "travelTimeGetter": Str("average"),
            }
        },

        "JDEQSim": {
            "params": {
                "carSize": Float("7.5"),
                "endTime": Str("undefined"),
                "flowCapacityFactor": Float("1.0"),
                "gapTravelSpeed": Float("15.0"),
                "minimumInFlowCapacity": Float("1800.0"),
                "squeezeTime": Float("1800.0"),
                "storageCapacityFactor": Float("1.0"),
            }
        },

        "TimeAllocationMutator": {
            "params": {
                "mutationAffectsDuration": Bool("true"),
                "mutationRange": Float("1000.0"),
                "useIndividualSettingsForSubpopulations": Bool("false"),
            }
        },

        "changeMode": {
            "params": {
                "ignoreCarAvailability": Bool("true"),
                "modes": Str("car,pt"),
            }
        },

        "controler": {
            "params": {
                "createGraphs": Bool("true"),
                "dumpDataAtEnd": Bool("true"),
                "enableLinkToLinkRouting": Bool("false"),
                "eventsFileFormat": Str("xml"),
                "firstIteration": Int("0"),
                "lastIteration": Int("100"),
                "mobsim": Str("qsim"),
                "outputDirectory": ValidPath("home/arup/tii/1p_models/3_default_config/model_out"),
                "overwriteFiles": Str("failIfDirectoryExists"),
                "routingAlgorithmType": Str("Dijkstra"),
                "runId": Str("null"),
                "snapshotFormat": Str(""),
                "writeEventsInterval": Int("1"),
                "writePlansInterval": Int("50"),
                "writeSnapshotsInterval": Int("1"),
            }
        },

        "counts": {
            "params": {
                "analyzedModes": Str("car"),
                "averageCountsOverIterations": Int("5"),
                "countsScaleFactor": Float("1.0"),
                "distanceFilter": Str("null"),
                "distanceFilterCenterNode": Str("null"),
                "filterModes": Bool("false"),
                "inputCRS": Str("null"),
                "inputCountsFile": ValidPath("null"),
                "outputformat": Str("txt"),
                "writeCountsInterval": Int("10"),
            }
        },

        "facilities": {
            "params": {
                "addEmptyActivityOption": Bool("false"),
                "assigningLinksToFacilitiesIfMissing": Bool("true"),
                "assigningOpeningTime": Bool("false"),
                "facilitiesSource": Str("none"),
                "idPrefix": Str(""),
                "inputCRS": Str("null"),
                "inputFacilitiesFile": Str("null"),
                "inputFacilityAttributesFile": ValidPath("null"),
                "oneFacilityPerLink": Bool("true"),
                "removingLinksAndCoordinates": Bool("true"),
            }
        },

        "households": {
            "params": {
                "inputFile": ValidPath("null"),
                "inputHouseholdAttributesFile": ValidPath("null"),
            }
        },

        "linkStats": {
            "params": {
                "averageLinkStatsOverIterations": Int("5"),
                "writeLinkStatsInterval": Int("10"),
            }
        },

        "parallelEventHandling": {
            "params": {
                "estimatedNumberOfEvents": Str("null"),
                "numberOfThreads": Int("32"),
                "oneThreadPerHandler": Bool("false"),
                "synchronizeOnSimSteps": Bool("true"),
            }
        },

        "planCalcScore": {
            "params": {
                "BrainExpBeta": Float("1.0"),
                "ValidPathSizeLogitBeta": Float("1.0"),
                "fractionOfIterationsToStartScoreMSA": Float("null"),
                "learningRate": Float("1.0"),
                "usingOldScoringBelowZeroUtilityDuration": Bool("false"),
                "writeExperiencedPlans": Bool("false"),
            },

            "parametersets": {
                "scoringParameters": {
                    "params": {
                        "earlyDeparture": Float("-0.0"),
                        "lateArrival": Float("-18.0"),
                        "marginalUtilityOfMoney":
                            Float("20.0"),
                        "performing":
                            Float("6.0"),
                        "subpopulation": Str("default"),
                        "utilityOfLineSwitch": Float("-1.0"),
                        "waiting": Float("-1.0"),
                        "waitingPt": Float("-1.0"),
                    },

                    "parametersets": {
                        "activityParams": {
                            "params": {
                                "activityType": Str("education"),
                                "closingTime": Time("17:00:00"),
                                "earliestEndTime": Time("undefined"),
                                "latestStartTime": Time("undefined"),
                                "minimalDuration": Time("06:00:00"),
                                "openingTime": Time("08:30:00"),
                                "priority": Float("1.0"),
                                "scoringThisActivityAtAll": Bool("true"),
                                "typicalDuration": Time("06:00:00"),
                                "typicalDurationScoreComputation": Str("relative"),
                            }
                        },

                        "modeParams": {
                            "params": {
                                "constant": Float("0.0"),
                                "marginalUtilityOfDistance_util_m": Float("0.0"),
                                "marginalUtilityOfTraveling_util_hr": Float("-6.0"),
                                "mode": Str("car"),
                                "monetaryDistanceRate": Float("-0.0"),
                            }
                        }
                    }
                }
            }
        },

        "planscalcroute": {
            "params": {
                "networkModes": Str("car"),
            },

            "parametersets": {
                "teleportedModeParameters": {
                    "params": {
                        "beelineDistanceFactor": Float("1.3"),
                        "mode": Str("bike"),
                        "teleportedModeFreespeedFactor": Float("null"),
                        "teleportedModeSpeed": Float("4.166666666666667"),
                    }
                }
            }
        },

        "ptCounts": {
            "params": {
                "countsScaleFactor": Float("1.0"),
                "distanceFilter": Str("null"),
                "distanceFilterCenterNode": Str("null"),
                "inputAlightCountsFile": ValidPath("null"),
                "inputBoardCountsFile": ValidPath("null"),
                "inputOccupancyCountsFile": ValidPath("null"),
                "outputformat": Str("null"),
                "ptCountsInterval": Float("10"),
            }
        },

        "qsim": {
            "params": {
                "creatingVehiclesForAllNetworkModes": Bool("true"),
                "endTime": Time("24:00:00"),
                "flowCapacityFactor": Float("0.01"),
                "insertingWaitingVehiclesBeforeDrivingVehicles": Bool("false"),
                "isRestrictingSeepage": Bool("true"),
                "isSeepModeStorageFree": Bool("false"),
                "linkDynamics": Str("FIFO"),
                "linkWidth": Float("30.0"),
                "mainMode": Str("bus,car,rail,tram"),
                "nodeOffset": Float("0.0"),
                "numberOfThreads": Int("32"),
                "removeStuckVehicles": Bool("false"),
                "seepMode": Str("bike"),
                "simEndtimeInterpretation": Str("null"),
                "simStarttimeInterpretation": Str("maxOfStarttimeAndEarliestActivityEnd"),
                "snapshotStyle": Str("equiDist"),
                "snapshotperiod": Time("00:00:00"),
                "startTime": Time("00:00:00"),
                "storageCapacityFactor": Float("0.01"),
                "stuckTime": Float("10.0"),
                "timeStepSize": Time("00:00:01"),
                "trafficDynamics": Str("queue"),
                "useLanes": Bool("false"),
                "usePersonIdForMissingVehicleId": Bool("true"),
                "usingFastCapacityUpdate": Bool("true"),
                "usingThreadpool": Bool("true"),
                "vehicleBehavior": Str("teleport"),
                "vehiclesSource": Str("defaultVehicle"),
            }
        },

        "scenario": {},
        "strategy": {
            "params": {
                "ExternalExeConfigTemplate": Str("null"),
                "ExternalExeTimeOut": Int("3600"),
                "ExternalExeTmpFileRootDir": ValidPath("null"),
                "fractionOfIterationsToDisableInnovation": Float("0.9"),
                "maxAgentPlanMemorySize": Int("5"),
                "planSelectorForRemoval": Str("WorstPlanSelector"),
            },

            "parametersets": {
                "strategysettings": {
                    "params": {
                        "disableAfterIteration": Int("-1"),
                        "executionValidPath": ValidPath("null"),
                        "strategyName": Str("SelectExpBeta"),
                        "subpopulation": Str("unknown"),
                        "weight": Float("0.6"),
                    }
                }
            }
        },

        "subtourModeChoice": {
            "params": {
                "chainBasedModes": Str("car,bike"),
                "considerCarAvailability": Bool("false"),
                "modes": Str("car,pt,walk,bike"),
            }
        },

        "transitRouter": {
            "params": {
                "additionalTransferTime": Float("0.0"),
                "directWalkFactor": Float("1.0"),
                "extensionRadius": Float("100.0"),
                "maxBeelineWalkConnectionDistance": Float("100.0"),
                "searchRadius": Float("1000.0"),
            }
        },

        "vehicles": {
            "params": {
                "vehiclesFile": ValidPath("null"),
            }
        },

        "vspExperimental": {
            "params": {
                "isAbleToOverwritePtInteractionParams": Bool("false"),
                "isGeneratingBoardingDeniedEvent": Bool("false"),
                "isUsingOpportunityCostOfTimeForLocationChoice": Bool("true"),
                "logitScaleParamForPlansRemoval": Float("1.0"),
                "vspDefaultsCheckingLevel": Str("ignore"),
                "writingOutputEvents": Bool("true"),
            }
        }
    }
}
