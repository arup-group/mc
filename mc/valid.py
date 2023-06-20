"""
Dictionary of valid config names for modules, paramsets and params.
"""

VALID_MAP = {

    "modules": {
        "ArupReplanning": {
            "params": {
                "maximumBikeTourDistance_m": "45000",
                "maximumWalkTourDistance_m": "12500",
                "minimumTimeMutationStep_s": "300",
            }
        },
        "swissRailRaptor": {
            "params": {
                "scoringParameters": "Default",
                "transferPenaltyBaseCost": "0.0",
                "transferPenaltyCostPerTravelTimeHour": "0.0",
                "transferPenaltyMaxCost": "Infinity",
                "transferPenaltyMinCost": "-Infinity",
                "useIntermodalAccessEgress": "false",
                "useModeMappingForPassengers": "false",
                "useRangeQuery": "false",
            },
            "parametersets": {
                "intermodalAccessEgress": {
                    "params": {
                        "mode": "walk",
                        "radius": "1000"
                    }
                },
                "modeMapping": {
                    "params": {
                        "routeMode": "bus",
                        "passengerMode": "bus"
                    }
                }
            }
        },

        "SBBPt": {
            "params": {
                "createLinkEventsInterval": "1",
                "deterministicServiceModes": "train",
            }
        },

        "global": {
            "params": {
                "coordinateSystem": "EPSG:27700",
                "numberOfThreads": "32",
                "randomSeed": "4711",
                "insistingOnDeprecatedConfigVersion": "true",
            }
        },

        "network": {
            "params": {
                "inputCRS": "null",
                "inputChangeEventsFile": "null",
                "inputNetworkFile": "./output_network.xml.gz",
                "laneDefinitionsFile": "null",
                "timeVariantNetwork": "false"
            }
        },

        "plans": {
            "params": {
                "inputPlansFile": "./output_plans.xml.gz",
                "inputPersonAttributesFile": "./output_personAttributes.xml.gz",
                "subpopulationAttributeName": "subpopulation",
                "activityDurationInterpretation": "tryEndTimeThenDuration",
                "inputCRS": "null",
                "networkRouteType": "LinkNetworkRoute",
                "removingUnnecessaryPlanAttributes": "false",
            }
        },

        "vehicles": {
            "params": {
                "vehiclesFile": "null"
            }
        },

        "transit": {
            "params": {
                "insistingOnUsingDeprecatedPersonAttributeFile": "true",
                "useTransit": "true",
                "transitScheduleFile": "./output_transitSchedule.xml.gz",
                "vehiclesFile": "./output_transitVehicles.xml",
                "inputScheduleCRS": "null",
                "transitLinesAttributesFile": "null",
                "transitModes": "pt",
                "transitStopsAttributesFile": "null",
            }
        },

        "multimodal": {
            "params": {
                "createMultiModalNetwork": "true",
                "numberOfThreads": "1",
                "cuttoffValueForNonCarModes": "25.0",
                "dropNonCarRoutes": "true",
                "multiModalSimulationEnabled": "true",
                "simulatedModes": "walk,bike",
                "ensureActivityReachability": "true",
            }
        },

        "travelTimeCalculator": {
            "params": {
                "analyzedModes": "car,bus,walk",
                "filterModes": "true",
                "separateModes": "false",
                "calculateLinkToLinkTravelTimes": "false",
                "calculateLinkTravelTimes": "true",
                "maxTime": "108000",
                "travelTimeAggregator": "optimistic",
                "travelTimeBinSize": "900",
                "travelTimeCalculator": "TravelTimeCalculatorArray",
                "travelTimeGetter": "average"
            }
        },

        "JDEQSim": {
            "params": {
                "carSize": "7.5",
                "endTime": "undefined",
                "flowCapacityFactor": "1.0",
                "gapTravelSpeed": "15.0",
                "minimumInFlowCapacity": "1800.0",
                "squeezeTime": "1800.0",
                "storageCapacityFactor": "1.0"
            }
        },

        "TimeAllocationMutator": {
            "params": {
                "mutationAffectsDuration": "true",
                "mutationRange": "1000.0",
                "useIndividualSettingsForSubpopulations": "false"
            }
        },

        "changeMode": {
            "params": {
                "ignoreCarAvailability": "true",
                "modes": "car,pt"
            }
        },

        "controler": {
            "params": {
                "createGraphs": "true",
                "dumpDataAtEnd": "true",
                "enableLinkToLinkRouting": "false",
                "eventsFileFormat": "xml",
                "firstIteration": "0",
                "lastIteration": "100",
                "mobsim": "qsim",
                "outputDirectory": "home/arup/tii/1p_models/3_default_config/model_out",
                "overwriteFiles": "failIfDirectoryExists",
                "routingAlgorithmType": "Dijkstra",
                "runId": "null",
                "snapshotFormat": "",
                "writeEventsInterval": "1",
                "writePlansInterval": "50",
                "writeSnapshotsInterval": "1"
            }
        },

        "counts": {
            "params": {
                "analyzedModes": "car",
                "averageCountsOverIterations": "5",
                "countsScaleFactor": "1.0",
                "distanceFilter": "null",
                "distanceFilterCenterNode": "null",
                "filterModes": "false",
                "inputCRS": "null",
                "inputCountsFile": "null",
                "outputformat": "txt",
                "writeCountsInterval": "10"
            }
        },

        "facilities": {
            "params": {
                "addEmptyActivityOption": "false",
                "assigningLinksToFacilitiesIfMissing": "true",
                "assigningOpeningTime": "false",
                "facilitiesSource": "none",
                "idPrefix": "",
                "inputCRS": "null",
                "inputFacilitiesFile": "null",
                "inputFacilityAttributesFile": "null",
                "oneFacilityPerLink": "true",
                "removingLinksAndCoordinates": "true"
            }
        },

        "households": {
            "params": {
                "inputFile": "null",
                "inputHouseholdAttributesFile": "null"
            }
        },

        "linkStats": {
            "params": {
                "averageLinkStatsOverIterations": "5",
                "writeLinkStatsInterval": "10"
            }
        },

        "parallelEventHandling": {
            "params": {
                "estimatedNumberOfEvents": "null",
                "eventsQueueSize": "null",
                "numberOfThreads": "32",
                "oneThreadPerHandler": "false",
                "synchronizeOnSimSteps": "true"
            }
        },

        "planCalcScore": {
            "params": {
                "BrainExpBeta": "1.0",
                "PathSizeLogitBeta": "1.0",
                "fractionOfIterationsToStartScoreMSA": "null",
                "learningRate": "1.0",
                "usingOldScoringBelowZeroUtilityDuration": "false",
                "writeExperiencedPlans": "false"
            },

            "parametersets": {
                "scoringParameters": {
                    "params": {
                        "earlyDeparture": "-0.0",
                        "lateArrival": "-18.0",
                        "marginalUtilityOfMoney": "0.0",
                        "performing": "6.0",
                        "subpopulation": "default",
                        "utilityOfLineSwitch": "-1.0",
                        "waiting": "-1.0",
                        "waitingPt": "-1.0"
                    },

                    "parametersets": {
                        "activityParams": {
                            "params": {
                                "activityType": "education",
                                "closingTime": "17:00:00",
                                "earliestEndTime": "undefined",
                                "latestStartTime": "undefined",
                                "minimalDuration": "06:00:00",
                                "openingTime": "08:30:00",
                                "priority": "1.0",
                                "scoringThisActivityAtAll": "true",
                                "typicalDuration": "06:00:00",
                                "typicalDurationScoreComputation": "relative"
                            }
                        },

                        "modeParams": {
                            "params": {
                                "constant": "0.0",
                                "marginalUtilityOfDistance_util_m": "0.0",
                                "marginalUtilityOfTraveling_util_hr": "-6.0",
                                "mode": "car",
                                "monetaryDistanceRate": "-0.0"
                            }
                        }
                    }
                }
            }
        },

        "planscalcroute": {
            "params": {
                "networkModes": "car"
            },

            "parametersets": {
                "teleportedModeParameters": {
                    "params": {
                        "beelineDistanceFactor": "1.3",
                        "mode": "bike",
                        "teleportedModeFreespeedFactor": "null",
                        "teleportedModeSpeed": "4.166666666666667"
                    }
                }
            }
        },

        "ptCounts": {
            "params": {
                "countsScaleFactor": "1.0",
                "distanceFilter": "null",
                "distanceFilterCenterNode": "null",
                "inputAlightCountsFile": "null",
                "inputBoardCountsFile": "null",
                "inputOccupancyCountsFile": "null",
                "outputformat": "null",
                "ptCountsInterval": "10"
            }
        },

        "qsim": {
            "params": {
                "creatingVehiclesForAllNetworkModes": "true",
                "endTime": "36:00:00",
                "flowCapacityFactor": "0.01",
                "insertingWaitingVehiclesBeforeDrivingVehicles": "false",
                "isRestrictingSeepage": "true",
                "isSeepModeStorageFree": "false",
                "linkDynamics": "FIFO",
                "linkWidth": "30.0",
                "mainMode": "car",
                "nodeOffset": "0.0",
                "numberOfThreads": "32",
                "removeStuckVehicles": "false",
                "seepMode": "bike",
                "simEndtimeInterpretation": "null",
                "simStarttimeInterpretation": "maxOfStarttimeAndEarliestActivityEnd",
                "snapshotStyle": "equiDist",
                "snapshotperiod": "00:00:00",
                "startTime": "00:00:00",
                "storageCapacityFactor": "0.01",
                "stuckTime": "10.0",
                "timeStepSize": "00:00:01",
                "trafficDynamics": "queue",
                "useLanes": "false",
                "usePersonIdForMissingVehicleId": "true",
                "usingFastCapacityUpdate": "true",
                "usingThreadpool": "true",
                "vehicleBehavior": "teleport",
                "vehiclesSource": "defaultVehicle"
            }
        },

        "hermes": {
            "params": {
                "mainMode": "car",
                "endTime": "36:00:00",
                "flowCapacityFactor": "0.01",
                "storageCapacityFactor": "0.01",
                "stuckTime": "10.0",
                "useDeterministicPt": "true"
            }
        },

        "scenario": {},

        "strategy": {
            "params": {
                "ExternalExeConfigTemplate": "null",
                "ExternalExeTimeOut": "3600",
                "ExternalExeTmpFileRootDir": "null",
                "fractionOfIterationsToDisableInnovation": "0.9",
                "maxAgentPlanMemorySize": "5",
                "planSelectorForRemoval": "WorstPlanSelector"
            },

            "parametersets": {
                "strategysettings": {
                    "params": {
                        "disableAfterIteration": "-1",
                        "executionPath": "null",
                        "strategyName": "SelectExpBeta",
                        "subpopulation": "unknown",
                        "weight": "0.6"
                    }
                }
            }
        },

        "subtourModeChoice": {
            "params": {
                "chainBasedModes": "car,bike",
                "considerCarAvailability": "false",
                "modes": "car,pt,walk,bike"
            }
        },

        "transitRouter": {
            "params": {
                "additionalTransferTime": "0.0",
                "directWalkFactor": "1.0",
                "extensionRadius": "100.0",
                "maxBeelineWalkConnectionDistance": "100.0",
                "searchRadius": "1000.0"
            }
        },

        "vspExperimental": {
            "params": {
                "isAbleToOverwritePtInteractionParams": "false",
                "isGeneratingBoardingDeniedEvent": "false",
                "isUsingOpportunityCostOfTimeForLocationChoice": "true",
                "logitScaleParamForPlansRemoval": "1.0",
                "vspDefaultsCheckingLevel": "ignore",
                "writingOutputEvents": "true"
            }
        }
    }
}
