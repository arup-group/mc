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