import os

def write_summary_log(config, output_path):
    """
    Summarise the key information as text log from matsim config when submitting jobs via the Bitsim Orchestration
    
    """
    message = []
    
    #add paths of the input files
    message.append("{:=^100s}".format("input files"))
    message.append(f"network_path:{config['network']['inputNetworkFile']}")
    message.append(f"plans_path:{config['plans']['inputPlansFile']}")
    message.append(f"schedule_path:{config['transit']['transitScheduleFile']}")
    message.append(f"vehicles_path:{config['transit']['vehiclesFile']}")
    
    #add mobsim setting summary
    message.append("{:=^100s}".format("mobsim setting"))
    message.append(f"mobsim:{config['controler']['mobsim']}")
    message.append(f"Flow_Capacity_Factor:{config[config['controler']['mobsim']]['flowCapacityFactor']}")
    message.append(f"Storage_Capacity_Factor:{config[config['controler']['mobsim']]['storageCapacityFactor']}")
    
    #check mode choice
    message.append("{:=^100s}".format("mode"))
    message.append(f"{config['subtourModeChoice']['modes']}")

    #summarise the scoring parameters for each mode 
    message.append("{:=^100s}".format("parameters for scoring"))
    for i in config['subtourModeChoice']['modes'].split(','):
        message.append("{:-^100s}".format("mode:"+ str(i)))
        message.append(f"mode_specific_constant:{config['planCalcScore']['scoringParameters:default']['modeParams:'+ str(i)]['monetaryDistanceRate']}")
        message.append(f"marginal_utility_of_distance:{config['planCalcScore']['scoringParameters:default']['modeParams:'+ str(i)]['marginalUtilityOfDistance_util_m']}") 
        message.append(f"marginal_utility_of_traveling:{config['planCalcScore']['scoringParameters:default']['modeParams:'+ str(i)]['marginalUtilityOfTraveling_util_hr']}") 
        message.append(f"monetary_distance_rate:{config['planCalcScore']['scoringParameters:default']['modeParams:'+ str(i)]['monetaryDistanceRate']}") 
    
    #write the above key information to a text file
    textfile = open(os.path.join(output_path,'simulation_log.txt'), 'w')
    for element in message:
        textfile.write(element + "\n")
    textfile.close()
