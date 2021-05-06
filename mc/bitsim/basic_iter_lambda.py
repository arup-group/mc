def lambda_handler(event, context=None):
    """
    Iterate the orchestration dictionary.
    Check for stopping criteria.
    Update matsim config path.
    Update output path (used by Elara).
    Check for and add elara config path.
    """
    DEFAULT_MATSIM_CONFIG_NAME = "matsim_config.xml"
    DEFAULT_ELARA_CONFIG_NAME = "elara_config.toml"

    orchestration = event["orchestration"]

    # set some defaults as required
    if not "index" in orchestration:  # default to 0
        orchestration["index"] = "0"
    if not "seed_matsim_config_path"in orchestration:  # default to looking in root
        orchestration["seed_matsim_config_path"] = orchestration["sim_root"] + "/" + DEFAULT_MATSIM_CONFIG_NAME
    if not "elara_config_path" in orchestration:  # default to looking in root
        orchestration["elara_config_path"] = orchestration["sim_root"] + "/" + DEFAULT_ELARA_CONFIG_NAME
    if not "cooling_iterations" in orchestration:
        orchestration["cooling_iterations"] = "0"

    # update matsim config path that will be used by MATSim (after being output by mc.autostep)
    orchestration["biteration_matsim_config_path"] = \
        orchestration["sim_root"] + "/" + str(orchestration["index"]) + "/" + DEFAULT_MATSIM_CONFIG_NAME

    # update biteration output path
    next_index = str(
        int(orchestration["index"]) + int(orchestration["step"])
        ) 
    orchestration["biteration_output_path"] = \
        orchestration["sim_root"] + "/" + next_index
    
    # iterate index (note that future jobs with the ASL will now receive the stepped value of 'index'
    orchestration["index"] = next_index

    # stopping criteria:
    if int(orchestration["index"]) > int(orchestration["iterations"]) + int(orchestration["cooling_iterations"]):
        raise Exception("Iteration & cooling limit exceeded")

    return orchestration