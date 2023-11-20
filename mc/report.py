import os
from datetime import date
import csv


def add_directory_to_report(config):
    """
    Add the input and out diretories and key information as text log from matsim config
    When submitting jobs via the Bitsim Orchestration
    """
    message = []
    # add the date
    message.append(f"Date:{date.today()}")

    # add paths of the input files
    message.append("{:=^150s}".format("input files"))
    message.append(f"network_path:{config['network']['inputNetworkFile']}")
    message.append(f"plans_path:{config['plans']['inputPlansFile']}")
    message.append(f"schedule_path:{config['transit']['transitScheduleFile']}")
    message.append(f"vehicles_path:{config['transit']['vehiclesFile']}")

    # add paths of the output diretory
    message.append("{:=^150s}".format("output directory"))
    message.append(f"output_directory:{config['controler']['outputDirectory']}")

    # add mobsim setting summary
    message.append("{:=^150s}".format("mobsim setting"))
    message.append(f"mobsim:{config['controler']['mobsim']}")
    message.append(
        f"Flow_Capacity_Factor:{config[config['controler']['mobsim']]['flowCapacityFactor']}"
    )
    message.append(
        f"Storage_Capacity_Factor:{config[config['controler']['mobsim']]['storageCapacityFactor']}"
    )

    return message


def add_scoring_to_report(config):
    """
    Display a table with scoring parameters for different modes and subpopulations in tabular format
    """
    message = add_directory_to_report(config)
    # add a header for the mode section
    message.append("{:=^150s}".format(" mode "))
    message.append(f"mode:{config['subtourModeChoice']['modes']}")
    message.append("")
    # Initialize a dictionary to store mode parameters
    parm = {}
    for mode in config["subtourModeChoice"]["modes"].split(","):
        parm[mode] = [
            "mode_specific_constant",
            "marginal_utility_of_distance",
            "marginal_utility_of_traveling",
            "monetary_distance_rate",
        ]

    subpopulation_set = {}
    subpop = "subpopulation: "
    for i in config["planCalcScore"].find("subpopulation"):
        subpopulation_set.setdefault(str(i.value), [])
        subpop = subpop + str(i.value) + ","
        for j in config.find("scoringParameters:" + str(i.value) + "/mode"):
            subpopulation_set[str(i.value)].append(j.value)

    table_header = "|{:^30}|".format("subpopulation")
    for subpop_name in subpopulation_set.keys():
        table_header += "{:^30}|".format(subpop_name)
    message.append(table_header)
    message.append("-" * (31 * (len(subpopulation_set) + 1)))
    # iterate through modes and subpopulations to create the table rows
    for idx, mode in enumerate(config["subtourModeChoice"]["modes"].split(",")):
        row_data = "|{:^30}|".format(mode)
        for subpop_name in subpopulation_set.keys():
            row_data += "{:^30}|".format(" ")
        message.append(row_data)
        message.append("-" * (31 * (len(subpopulation_set) + 1)))
        # iterate through the scoring parameters and add the values to the
        for row_idx, row_name in enumerate(
            ["marginalUtilityOfMoney", "performing", "utilityOfLineSwitch"] + parm[mode]
        ):
            row_data = "|{:^30}|".format(row_name)
            for subpop_name in subpopulation_set.keys():
                if row_idx == 0:
                    cell_value = config["planCalcScore"][
                        "scoringParameters::" + subpop_name
                    ]["marginalUtilityOfMoney"]
                elif row_idx == 1:
                    cell_value = config["planCalcScore"][
                        "scoringParameters::" + subpop_name
                    ]["performing"]
                elif row_idx == 2:
                    cell_value = config["planCalcScore"][
                        "scoringParameters::" + subpop_name
                    ]["utilityOfLineSwitch"]
                else:
                    if mode not in subpopulation_set[subpop_name]:
                        cell_value = "NA"
                    else:
                        if row_name == "mode_specific_constant":
                            cell_value = config["planCalcScore"][
                                "scoringParameters::" + subpop_name
                            ]["modeParams::" + mode]["constant"]
                        elif row_name == "marginal_utility_of_distance":
                            cell_value = config["planCalcScore"][
                                "scoringParameters::" + subpop_name
                            ]["modeParams::" + mode]["marginalUtilityOfDistance_util_m"]
                        elif row_name == "marginal_utility_of_traveling":
                            cell_value = config["planCalcScore"][
                                "scoringParameters::" + subpop_name
                            ]["modeParams::" + mode][
                                "marginalUtilityOfTraveling_util_hr"
                            ]
                        elif row_name == "monetary_distance_rate":
                            cell_value = config["planCalcScore"][
                                "scoringParameters::" + subpop_name
                            ]["modeParam:s:" + mode]["monetaryDistanceRate"]
                row_data += "{:^30}|".format(cell_value)
            message.append(row_data)
            message.append("-" * (31 * (len(subpopulation_set) + 1)))

    return message


def write_text(text, output_path):
    """
    Write the key information into a text file
    """
    textfile = open(os.path.join(output_path, "simulation_report.txt"), "w")
    for element in text:
        textfile.write(element + "\n")
    textfile.close()


def write_csv(data, output_path):
    """
    Write the key information into a CSV file
    """
    with open(
        os.path.join(output_path, "simulation_report.csv"), "w", newline=""
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in data:
            # Skip rows with dividing lines
            if "----" in row:
                continue
            csv_writer.writerow(row.split("|"))


def report_config(config, output_path):
    text = add_scoring_to_report(config)
    write_text(text, output_path)
    write_csv(text, output_path)


def find_log_files(file_name, root_dir):
    """
    Find the path for log files for the jobs from different simulation jobs
    """
    file_directory = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith(file_name):
                if (
                    str(root)[-2:] == "/0"
                ):  # find the file in zero iteration only in the simulation folder
                    file_directory.append(os.path.join(root, file))
    return file_directory


def merge_files(file_directory, root_dir):
    """
    Combine and update the matsim_overrides log from different simulation jobs
    """
    with open(os.path.join(root_dir, "matsim_overrides_summary.log"), "w") as outfile:
        for f in file_directory:
            with open(f) as infile:
                text = infile.readlines()
                text.insert(0, f + "\n")
                text.insert(0, "log_path:")
                text.insert(0, "-" * 100 + "\n")  # split line
                outfile.write("".join(text))


def summarise_overrides_log(file_name, root_dir):
    file_directory = find_log_files(file_name, root_dir)
    merge_files(file_directory, root_dir)
