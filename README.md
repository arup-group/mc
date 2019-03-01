# Master of Ceromonies - or MATSim Configs from a Schedule of Parameters 

Command Line tool for making a config or batch of configs from a schedule of parameters.

### Contents
* [Installation](#markdown-header-installation)
* [About](#markdown-header-about)
* [Command line reference](#markdown-header-command-line-reference)
* [Default format](#markdown-header-default-format)
* [Schedule format](#markdown-header-schedule-format)
* [Todo](#markdown-header-todo)

### Installation
Clone or download the repository from the [downloads section](https://bitbucket.org/arupdigital/MC/downloads/). Once available locally, navigate to the folder and run:
```
pip3 install -e .
mc --help
```

### About
MATSim models require careful setting of numerous parameters using a `config.xml` file. Specifically, MC creates batches of configs taking subpopulation `planCalcScore` and `strategy` parameters for all modes and activities from a csv formatted schedule in `inputs/`.
MC also takes a `default_config.xml` which provides the remaining params (such as for `global` and `mobsim`). A scheduled batch of output configs will therefore we a combination of **stable params** from **default** and *explorable params* from a *schedule*.
Note that the output config is entirely based on the available params in the default config. Schedules inputs are validated by the `params` module. This needs to be adjusted if new config modules are used (for exampe `changeSingleTripMode` vs `SubtourModeChoice`).
Output config naming convention is `<default_config_name>_test_<schedule_test_id>.xml`.

### Command line reference
```
Usage: mc [OPTIONS] SCHEDULE_PATH DEFAULT_PATH

  Command line tool for creating MATSim configs from defaults and test
  schedule. :param schedule_path: Parameter schedule file path :param
  default_path: Default parameter schedule file path

Options:
  --out_dir TEXT  output directory, default: "output/"
  --select TEXT   option to select single test for config
  -h, --help      Show this message and exit. 
```

### Default format
This utility uses a XML formatted default config as a structure for the output config. This input must therefore match the expected/required XML output.


### Schedule format
This utility uses a CSV formatted param schedule to input test parameters, this input should match the XML input and is also validated by the `params` module.

### Todo

**Priority**

* Refactor/simplify the element setting methods - they are confusing
* Make schedule input more robust (for example add functionality to cope with different replanning modules)
* Restrict or add simple warnings for parameters

**Nice to have**

* Complete build of config from scratch
