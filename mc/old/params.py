

class ParamValidList:

    modules = ['planCalcScore', 'strategy']

    scoringParameters = [
        'marginalUtilityOfMoney',
        'performing',
        'lateArrival',
        'earlyDeparture',
        'waiting',
        'waitingPt',
        'utilityOfLineSwitch',
        'modeParams',
        'activityParams'
    ]

    modes = [
        'car',
        'pt',
        'walk',
        'bike'
    ]

    modeParams = [
        'constant',
        'marginalUtilityOfDistance_util_m',
        'marginalUtilityOfTraveling_util_hr',
        'monetaryDistanceRate'
    ]

    activities = [
        'depot',
        'delivery',
        'education',
        'escort',
        'home_0_8',
        'home_8_p',
        'medical',
        'other',
        'personal',
        'work_0_3',
        'work_3_7',
        'work_7_p',
        'work_9_5',
        'work_9_5_am',
        'work_9_5_pm',
        'recreation',
        'shop',
        'visit',
        'religious'
    ]

    activityParams = [
        'priority',
        'openingTime',
        'closingTime',
        'typicalDuration',
        'minimalDuration',
        'earliestEndTime',
        'latestStartTime'
    ]

    strategysettingsParams = [
        'SubtourModeChoice',
        'ReRoute',
        'TimeAllocationMutator_ReRoute',
        'ChangeExpBeta'
    ]


class ParamList:

    scoringParameters = [
        'marginalUtilityOfMoney',
        'performing',
        'lateArrival',
        'earlyDeparture',
        'waiting',
        'waitingPt',
        'utilityOfLineSwitch'
    ]

    modeParams = [
        'constant',
        'marginalUtilityOfDistance_util_m',
        'marginalUtilityOfTraveling_util_hr',
        'monetaryDistanceRate'
    ]

    activityParams = [
        'priority',
        'openingTime',
        'closingTime',
        'typicalDuration',
        'minimalDuration',
        'earliestEndTime',
        'latestStartTime'
    ]


def validate_schedule(df):
    print('Schedule Validation:')
    # validate index
    test_ids = list(df.index.levels[0])
    print('test ids: {}'.format(test_ids))

    subpops = [list(df.loc[tid].index) for tid in test_ids]
    for index in subpops:
        assert is_equal(index, subpops[0]), 'check: {}'.format(subpops[0])
    print('sub-populations: {}'.format(subpops[0]))

    # validate modules
    expected_modules = ParamValidList.modules
    module_ids = list(df.columns.levels[0])
    assert is_equal(expected_modules, module_ids), 'check: {}'.format(module_ids)
    print('module ids: {}'.format(expected_modules))

    # validate planCalcScore
    expected_names = ParamValidList.scoringParameters
    names = list(df.loc[:, 'planCalcScore'].columns.get_level_values(0).unique())
    assert is_equal(names, expected_names), 'check: {}'.format(names)
    print('sub-population scoring params: {}'.format(expected_names))

    # validate modes
    expected_modes = ParamValidList.modes
    modes = list(df.loc[:, 'planCalcScore']['modeParams'].columns.get_level_values(0).unique())
    assert is_equal(modes, expected_modes), 'check: {}'.format(modes)
    print('modes: {}'.format(expected_modes))

    # validate mode params
    mode_params = list(df.loc[:, 'planCalcScore']['modeParams'].columns.get_level_values(1).unique())
    assert is_equal(mode_params, ParamValidList.modeParams), 'check: {}'.format(mode_params)
    print('mode-params: {}'.format(ParamValidList.modeParams))

    # validate activities
    expected_activities = ParamValidList.activities
    activities = list(df.loc[:, 'planCalcScore']['activityParams'].columns.get_level_values(0).unique())
    assert is_equal(activities, expected_activities), 'check: {}'.format(activities)
    print('activities: {}'.format(expected_activities))

    # validate activity params
    activity_params = list(df.loc[:, 'planCalcScore']['activityParams'].columns.get_level_values(1).unique())
    assert is_equal(activity_params, ParamValidList.activityParams), 'check: {}'.format(activity_params)
    print('activity-params: {}'.format(ParamValidList.modeParams))

    # validate strategy settings
    expected_names = ParamValidList.strategysettingsParams
    names = list(df.loc[:, 'strategy']['strategysettings'].columns.get_level_values(0).unique())
    assert is_equal(names, expected_names), 'check: {}'.format(names)
    print('strategy setting params: {}'.format(expected_names))

    return test_ids, subpops[0]


def is_equal(list_a, list_b):
    return len(list_a) == len(list_b) and sorted(list_a) == sorted(list_b)