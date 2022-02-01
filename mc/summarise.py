import os
from datetime import date


def diretory_log_summary(config):
    """
    Summarise the input and out diretories and key information as text log from matsim config
    When submitting jobs via the Bitsim Orchestration
    """
    message = []
    # add the date
    message.append(f"Date:{date.today()}")

    # add paths of the input files
    message.append("{:=^100s}".format("input files"))
    message.append(f"network_path:{config['network']['inputNetworkFile']}")
    message.append(f"plans_path:{config['plans']['inputPlansFile']}")
    message.append(f"schedule_path:{config['transit']['transitScheduleFile']}")
    message.append(f"vehicles_path:{config['transit']['vehiclesFile']}")

    # add paths of the output diretory
    message.append("{:=^100s}".format("output directory"))
    message.append(f"output_directory:{config['controler']['outputDirectory']}")

    # add mobsim setting summary
    message.append("{:=^100s}".format("mobsim setting"))
    message.append(f"mobsim:{config['controler']['mobsim']}")
    message.append(f"Flow_Capacity_Factor:{config[config['controler']['mobsim']]['flowCapacityFactor']}")
    message.append(f"Storage_Capacity_Factor:{config[config['controler']['mobsim']]['storageCapacityFactor']}")

    return message


def scoring_summary(config):
    """
    Summarise the key scoring parameters

    """
    message = diretory_log_summary(config)

    # check mode choice
    message.append("{:=^100s}".format("mode"))
    message.append(f"{config['subtourModeChoice']['modes']}")
    dict1 = {}
    for mode in (config['subtourModeChoice']['modes'].split(',')):
        dict1[mode] = ["mode_specific_constant:",
                       "marginal_utility_of_distance:",
                       "marginal_utility_of_traveling:",
                       "monetary_distance_rate:"]

    # add subpopulation in the score calcualtion
    subpopulation_set = {}
    subpop = 'subpopulation: '
    for i in config['planCalcScore'].find('subpopulation'):
        subpopulation_set.setdefault(str(i.value), [])
        subpop = subpop + str(i.value) + ','
        for j in config.find("scoringParameters:" + str(i.value) + "/mode"):
            subpopulation_set[str(i.value)].append(j.value)

    # summarise the scoring parameters for each mode
    performing = "performing:"
    utility = 'marginalUtilityOfMoney:'
    message.append("{:=^100s}".format("parameters for scoring"))
    for i in subpopulation_set:
        score_para = config['planCalcScore']['scoringParameters:' + str(i)]
        performing += score_para['performing'] + ','
        utility += score_para['marginalUtilityOfMoney'] + ','

        for idx, mode in enumerate(config['subtourModeChoice']['modes'].split(',')):
            if mode not in subpopulation_set[str(i)]:
                dict1[mode][0] += 'NA'
                dict1[mode][1] += 'NA'
                dict1[mode][2] += 'NA'
                dict1[mode][3] += 'NA'
            else:
                dict1[mode][0] += str(score_para['modeParams:' + str(mode)]['monetaryDistanceRate'] + ',')
                dict1[mode][1] += str(score_para['modeParams:' + str(mode)]['marginalUtilityOfDistance_util_m'] + ',')
                dict1[mode][2] += str(score_para['modeParams:' + str(mode)]['marginalUtilityOfTraveling_util_hr'] + ',')
                dict1[mode][3] += str(score_para['modeParams:' + str(mode)]['monetaryDistanceRate'] + ',')

    # add scoring parameters for different subpopulation
    message.append("{:=^100s}".format("subpopulation"))
    message.append(subpop)
    message.append("{:=^50s}".format("scoring parameters for subpopulation"))
    message.append(utility)
    message.append(performing)

    # append the scoring parameters for each mode to the log
    for mode in (config['subtourModeChoice']['modes'].split(',')):
        message.append("{:-^50s}".format("mode:" + str(mode)))
        for para in dict1[mode]:
            message.append(para)

    return message


def write_text(text, output_path):
    """
    Write the key information into a text file
    """
    textfile = open(os.path.join(output_path, 'simulation_log.txt'), 'w')
    for element in text:
        textfile.write(element + "\n")
    textfile.close()


def summarise_config(config, output_path):
    text = scoring_summary(config)
    write_text(text, output_path)
