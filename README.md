# Master of Ceremonies

Tools for making MATSim configuration less painful.

Generate default configs, cookie-cut new configs, diff and debug existing configs from the 
command line. Also load and interact with configs for as dictionary like python3 objects with built-in
key and value assurance.

Got a `config.xml` that you love? Let me know and get it added to the CLI generator so that it's always available.

## Contents
* [Installation](#markdown-header-installation)
* [Usage](#markdown-header-usage)
* [Command Line](#markdown-header-command-line)
* [Programming Interface](#markdown-header-programming-interface)
* [Tests](#markdown-header-tests)
* [Contact](#markdown-header-contacts)
* [Todo](#markdown-header-todo)

## Installation
Clone or download the repository from the [downloads section](https://bitbucket.org/arupdigital/MC/downloads/). Once available locally, navigate to the folder and run:
```
pip3 install -e .
pip3 install pytest
cd mc
pytest
```

## Usage
- Command Line Interface
- Python Package

## Command Line
The CLI commands are pretty explorable via help, start with `mc --help`:

```bash
Usage: mc [OPTIONS] COMMAND [ARGS]...

  Command line interface for MC.

Options:
  --help  Show this message and exit.

Commands:
  build    Build a config with defined sub-pops, modes & activities.
  convert  Read an existing config and write as xml or json.
  debug    Debug a config.
  diff     Simple diff two configs.
  gen      Generate a template config: empty|default|test.
  print    Print a config to terminal.
```

## Programming Interface
 ```
>>> from mc import build
>>> from pathlib import Path
```
To facilitate a beautiful future where humans never need edit xml and machines start to
 explore MATSim simulation config parameter spaces themselves, mc makes a dictionary-like `mc.build.Config`
  object available. `Config` objects can read and write to MATSim valid `.xml` input (and `.json`).

 ```
>>> config = build.Config(path=Path('default.xml'))
>>> config.write(path=Path('temp.xml'))
```
 `Config` objects consist of nested `Modules`, `ParamSets` and `Params`. All of which will behave
  like a nested set of dicts. For example supporting getting and setting methods:

 ```
 # get and print module contents:
>>> config['plans'].print()

module {'name': 'plans'}
    param {'name': 'inputPlansFile', 'value': 'test_inputs/population.xml'}
    param {'name': 'inputPersonAttributesFile', 'value': 'test_inputs/attributes.xml'}
    param {'name': 'subpopulationAttributeName', 'value': 'subpopulation'}
```
 ```
 # set and print a single param:
>>> config['plans']['inputPlansFile'] = 'test_inputs/new_population.xml'
>>> print(config['plans']['inputPlansFile'])

test_inputs/new_population.xml
```

Nested setting is allowed, for example for an empty `Config` a new module, paramset and param
 can be set together:
 ```
>>> empty_config = build.Config()
>>> empty_config['global']['coordinateSystem'] = 'EPSG:27700'
INFO creating new empty module: global
>>> empty_config.print()

module {'name': 'global'}
    param {'name': 'coordinateSystem', 'value': 'EPSG:27700'}
```
...providing that all keys and values are valid:
```
>>> empty_config = build.Config()
>>> empty_config['NotAModule']['coordinateSystem'] = 'EPSG:27700'
...
KeyError: "key:'NotAModule' not found in modules"
```
```
>>> empty_config['global']['coordinateSystem'] = 2700
INFO creating new empty module: global
...
ValueError: Please use value of either type ParamSet, Param or str
```
MATSim configurations include parametersets which look like lists. We therefore suffix
ParamSet keys using `:<uid>` where the uid is most usefully the appropriate parameterset
subpopulation, mode or activity:
```
>>> empty_config.write(path=Path('temp.xml'))
>>> empty_config['planCalcScore']['scoringParameters:high_income']['modeParams:car']['monetaryDistanceRate'] = '-0.0001'
INFO creating new empty module: planCalcScore
INFO creating new empty parameterset: scoringParameters:high_income
INFO creating new empty parameterset: modeParams:car
```
When writing to `.xml` these suffixes are ignored, writing a clean usable config. When reading in
an existing config, these suffixes are automatically generated.
WARNING: Not specifying a suffix will generally be assumed as using `:default`.

Nested objects can be explicitly accessed via the parent attributes, ie `.modules.values()`, 
`.parametersets.values()`, `params.values()`. Valid keys (ignoring suffixes) for nestable
objects via `.valid_keys`.


## Tests
It's broken? Yes there are some tests via `pytest` (`pip2 install pytest`), although coverage is "variable". 


## Contact
fred.shone@arup.com


## Further Work
* Add more and better debugging
* Populate with some more default configurations
* Add detailed value validation, for example acceptable integer ranges
* Add further debugging by comparing config to other inputs such as transit schedules...
* MC use to support batch config building using a tabular data, but not any more.
The code is still stashed in `old`