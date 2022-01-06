import os


def build_summary(config):
    """
    Summarise the key information as text log from matsim config when submitting jobs via the Bitsim Orchestration
    """
    message = []

    # add paths of the input files
    message.append("{:=^100s}".format("input files"))
    message.append(f"network_path:{config['network']['inputNetworkFile']}")
    message.append(f"plans_path:{config['plans']['inputPlansFile']}")
    message.append(f"schedule_path:{config['transit']['transitScheduleFile']}")
    message.append(f"vehicles_path:{config['transit']['vehiclesFile']}")

    # add mobsim setting summary
    message.append("{:=^100s}".format("mobsim setting"))
    message.append(f"mobsim:{config['controler']['mobsim']}")
    message.append(f"Flow_Capacity_Factor:{config[config['controler']['mobsim']]['flowCapacityFactor']}")
    message.append(f"Storage_Capacity_Factor:{config[config['controler']['mobsim']]['storageCapacityFactor']}")

    # check mode choice
    message.append("{:=^100s}".format("mode"))
    message.append(f"{config['subtourModeChoice']['modes']}")

    # summarise the scoring parameters for each mode
    message.append("{:=^100s}".format("parameters for scoring"))
    for i in config['subtourModeChoice']['modes'].split(','):
        message.append("{:-^100s}".format("mode:" + str(i)))
        score_para = config['planCalcScore']['scoringParameters:default']
        message.append(f"mode_specific_constant:\
{score_para['modeParams:' + str(i)]['monetaryDistanceRate']}")
        message.append(f"marginal_utility_of_distance:\
{score_para['modeParams:' + str(i)]['marginalUtilityOfDistance_util_m']}")
        message.append(f"marginal_utility_of_traveling:\
{score_para['modeParams:' + str(i)]['marginalUtilityOfTraveling_util_hr']}")
        message.append(f"monetary_distance_rate:\
{score_para['modeParams:' + str(i)]['monetaryDistanceRate']}")
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
    text = build_summary(config)
    write_text(text, output_path)
