import logging
from pathlib import Path

from mc.base import BaseConfig, Param


DEFAULT_MATSIM_CONFIG_NAME = "matsim_config.xml"
DEFAULT_PLANS_NAME = "output_plans.xml.gz"
DEFAULT_NETWORK_NAME = "output_network.xml.gz"
DEFAULT_TRANSITSCHEDULE_NAME = "output_transitSchedule.xml.gz" 
DEFAULT_TRANSITVEHICLES_NAME = "output_transitVehicles.xml.gz"
DEFAULT_FRACTION_OF_ITERATIONS_TO_DISABLE_INNOVATION = 0.8


def lambda_handler(event, context):
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

    # stopping criteria:
    if int(orchestration["index"]) >= int(orchestration["iterations"]):

        if "cooling_iterations" not in orchestration:
            raise Exception("Iteration limit exceeded")

        if int(orchestration["cooling_iterations"]) > 0:
            orchestration["fractionOfIterationsToDisableInnovation"] = "0"
            orchestration["cooling_iterations"] = str(
                int(orchestration["cooling_iterations"]) - int(orchestration["step"]))
        else:
            raise Exception("Iteration & cooling limit exceeded")

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

    return orchestration


# orchestration.json
{
  "orchestration": {
    "iterations": "100",  # count --> iterations
    "step": "5",
    "cooling_iterations": "10",
    "sim_root": "/efs/early_stopping_tests/multimodal_town_B",  # mc_output_dir -> sim_root
    "seed_matsim_config_path": "/efs/early_stopping_tests/multimodal_town_B/bitsim_config.xml",  # mc_input_config -> matsim_config_path
    "elara_config_path": "/efs/early_stopping_tests/multimodal_town_B/elara_config.toml",  # elara_config --> elara_config_path
    "workflow": "test-multimodal-town",
    "channel": "#city-modelling-feeds-test"
  }
}


# template.asl
{
  "Comment": "Amazon States Language implementation of basic BitSim iterator via AWS Batch",
  "StartAt": "ITERATOR",
  "States": {
    "ITERATOR": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:$AWS_CONFIG_default_region:$AWS_CONFIG_account_id:function:BitsimIterator",
      "ResultPath": "$.orchestration",
      "Next": "MC",
      "Catch": [{
        "ErrorEquals": [ "States.ALL" ],
        "Next": "ROLLYPOLLY_FINAL",
        "ResultPath": "$.taskresult"
      }]
    },
    "MC": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "ResultPath": "$.taskresult",
      "Parameters": {
        "JobDefinition": "$MC_jobDefinition",
        "JobName": "$MC_jobName",
        "JobQueue": "$jobQueue",
        "Parameters.$": "$.orchestration",
        "ContainerOverrides": {
          "Command": [
            "autostep",
            "Ref::sim_root",
            "Ref::seed_matsim_config_path",
            "Ref::index"
            "Ref::iterations",
            "Ref::step",
            "Ref::biteration_matsim_config_path"
            "--",
            "fractionOfIterationsToDisableInnovation",
            "Ref::fractionOfIterationsToDisableInnovation"
            $sampleParameters
          ]
        }
      },
      "Next": "MATSIM"
    },
    "MATSIM": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "ResultPath": "$.taskresult",
      "Parameters": {
        "Parameters.$": "$.orchestration",
        "JobDefinition": "$MATSIM_jobDefinition",
        "JobName": "$MATSIM_jobName",
        "JobQueue": "$jobQueue",
        "ContainerOverrides": {
          "Command": [
            "$MATSIM_controller",
            "Ref::biteration_matsim_config_path"
          ]
        }
      },
      "Next": "ELARA",
      "Retry": [{
        "ErrorEquals": [ "States.TaskFailed" ],
        "IntervalSeconds": 5,
        "MaxAttempts": 2,
        "BackoffRate": 2.0
      }]
    },
    "ELARA": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "ResultPath": null,
      "Parameters": {
        "Parameters.$": "$.orchestration",
        "JobDefinition": "$ELARA_jobDefinition",
        "JobName": "$ELARA_jobName",
        "JobQueue": "$jobQueue",
        "Parameters.$": "$.orchestration",
        "ContainerOverrides": {
          "Command": [
            "run",
            "Ref::elara_config_path",
            "--path_override",
            "Ref::biteration_output_path"
          ]
        }
      },
      "Next": "ITERATOR",
      "Retry": [{
        "ErrorEquals": [ "States.TaskFailed" ],
        "IntervalSeconds": 5,
        "MaxAttempts": 2,
        "BackoffRate": 2.0
      }]
    },
    "ROLLYPOLLY_FINAL": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "Parameters.$": "$.orchestration",
        "JobDefinition": "$ROLLYPOLLY_FINAL_jobDefinition",
        "JobName": "$ROLLYPOLLY_FINAL_jobName",
        "JobQueue": "$jobQueue",
        "ContainerOverrides": {
          "Command": [
            "/rollypolly/roll/poll_file_post_slack.py",
            "-f", "Ref::biteration_output_path",
            "-j", "Final",
            "-w", "Ref::workflow",
            "-c", "Ref::channel",
            "-ar", "$AWS_CONFIG_default_region"
          ]
        }
      },
      "End": true
    }
  }


def autostep_config(
    sim_root: Path,
    seed_matsim_config_path: Path,
    index: str,
    iterations: str,
    step: str,
    biteration_matsim_config_path: str,
    overrides: tuple
    ) -> None:
    """
    Step a config for bitsim based on arguments and an overrides map.
    Note that index will have already been incremented by a step.
    Note that MATSim configs use paths relative to config location.
    """

    # force the input types as required
    if isinstance(sim_root, str):
        sim_root = Path(sim_root)
    if isinstance(seed_matsim_config_path, str):
        sim_root = Path(seed_matsim_config_path)
    if not isinstance(index, str):
        index = int(index)
    if not isinstance(iterations, str):
        iterations = int(iterations)
    if not isinstance(step, str):
        step = int(step)
    if isinstance(biteration_matsim_config_path, str):
        biteration_matsim_config_path = Path(biteration_matsim_config_path)

    logging.info(f"Loading seed config from: {seed_matsim_config_path}")
    config = BaseConfig(seed_matsim_config_path)
    set_default_behaviours(config)

    first_iteration = index - step
    last_iteration = index
    new_write_path = sim_root / str(last_iteration)

    set_write_path(config=config, new_write_path=new_write_path)
    set_iterations(config=config, first_iteration=first_iteration, last_iteration=last_iteration)
    find_and_set_overrides(config=config, overrides=overrides)

    if not index == 0:  # if first iteration - don't update input paths
        previous_root = sim_root / str(first_iteration)
        auto_set_input_paths(config=config, root=previous_root)

    logging.info(f"Writing config to: {biteration_matsim_config_path}")
    try:
        biteration_matsim_config_path.parent.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.error(f"Folder for {biteration_matsim_config_path} is already there")
    else: 
        logging.info(f"Creating dir for {biteration_matsim_config_path}")
    config.write(biteration_matsim_config_path)

    logging.info(f"Autostep complete")


def construct_override_map_from_tuple(overrides: tuple) -> dict:
    override_map = {}
    for i in range(0, len(overrides), 2):
        override_map[overrides[i]] = overrides[i+1]
    return override_map


def set_default_behaviours(config: BaseConfig, overrides: dict):
    """
    Set common behaviours in config.
    """
    logging.info(f"Setting common behaviour overrides.")
    outputDirectory = config['controler']['outputDirectory'] 
    config['controler']['outputDirectory'] = "deleteDirectoryIfExists"
    logging.info(f"Changing: {outputDirectory} to: 'deleteDirectoryIfExists'")

    writeEventsInterval = config['controler']['writeEventsInterval'] 
    config['controler']['writeEventsInterval'] = "0"
    logging.info(f"Changing: {writeEventsInterval} to: '0'")

    writePlansInterval = config['controler']['writePlansInterval'] 
    config['controler']['writePlansInterval'] = "0"
    logging.info(f"Changing: {writePlansInterval} to: '0'")

    if "fractionOfIterationsToDisableInnovation" not in overrides:
        fraction = config['strategy'].get('fractionOfIterationsToDisableInnovation')
        default = str(DEFAULT_FRACTION_OF_ITERATIONS_TO_DISABLE_INNOVATION)
        config['strategy']['fractionOfIterationsToDisableInnovation'] = default
        logging.info(f"Changing fractionOfIterationsToDisableInnovation: {fraction} to: {default}")


def set_write_path(config: BaseConfig, new_write_path: Path) -> None:
    """
    Note that 'outputDirectory' == '$next_matsim_dir' from overrides
    """
    logging.info(f"Write path override to config")
    old_write_path = Path(config['controler']['outputDirectory'])
    config['controler']['outputDirectory'] = str(new_write_path)
    logging.info(f"Write file path override: {str(old_write_path)} to: {str(new_write_path)}")


def auto_set_input_paths(config: BaseConfig, root: Path) -> None:
    """
    Change input config path value for <>File names parameters, eg inputNetworkFile.
    Note that MATSim configs use paths relative to config location.
    :param config: Config
    :param root: Path
    """

    logging.info(f"Input path overrides to config")
    for module, param, default in [
        ("network", "inputNetworkFile", DEFAULT_NETWORK_NAME),
        ("plans", "inputPlansFile", DEFAULT_PLANS_NAME),
        ("transit", "transitScheduleFile", DEFAULT_TRANSITSCHEDULE_NAME),
        ("transit", "vehiclesFile", DEFAULT_TRANSITVEHICLES_NAME),
        ]:
        prev_path = config[module][param]
        new_path = root / default
        logging.info(f"Input ({param}) file path override: {str(prev_path)} to: {str(new_path)}")
        config[module][param] = str(new_path)


def set_iterations(config: BaseConfig, first_iteration: int, last_iteration: int) -> None:
    """
    Set config firstIteration and lastIteration.
    """
    logging.info(f"Step overrides to config")
    old_firstIteration = config['controler']['firstIteration'] 
    config['controler']['firstIteration'] = str(first_iteration)
    logging.info(f"firstIteration (step) override: {old_firstIteration} to: {first_iteration}")
    old_lastIteration = config['controler']['lastIteration'] 
    config['controler']['lastIteration'] = str(last_iteration)
    logging.info(f"lastIteration (step) override: {old_lastIteration} to: {last_iteration}")


def find_and_set_overrides(config: BaseConfig, overrides: dict) -> None:
    """
    Set mutations (for example from a random or grid search) based on
    mc addresses in the overrides. For example given:
    {
        'planCalcScore/scoringParameters:default/performing': '10',
        'planCalcScore/scoringParameters:default/activityParams:work/openingTime': '07:00:00',
        'planCalcScore/scoringParameters:default/modeParams:car/monetaryDistanceRate': '-0,00001',
        'planCalcScore/scoringParameters:*/modeParams:car/monetaryDistanceRate': '-0,00001',
        'strategy/fractionOfIterationsToDisableInnovation': '0',
        'strategy/strategysettings:default/weight': '0'
    }
    """
    for k, v in overrides.items():
        params = config.find(k)
        for param in params:
            if isinstance(param, Param):
                old_value = param.value
                param.value = v
                logging.info(f"Override {param.ident}: {old_value} to: {v}")
