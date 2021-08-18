# Master of Ceremonies

Tools for making MATSim configuration less painful.

Generate default configs, cookie-cut new configs, diff and debug existing configs from the 
command line. Also build and interact with configs as dictionary like python3 objects with built-in
key and value assurance.

Got a `config.xml` that you love? Let me know and get it added to the CLI generator so that it's always available.

## Contents

* [Installation](#installation)
* [Usage](#usage)
* [Command Line](#command-line)
* [Programming Interface](#programming-interface)
* [Find](#find)
* [Validation](#validation)
* [Updating MC for config changes](#updating-mc-for-config-changes)
* [Tests](#tests)
* [Contact](#contacts)
* [Todo](#todo)

## Installation

Clone or download the repository from the [downloads section](https://bitbucket.org/arupdigital/MC/downloads/). Once available locally, navigate to the folder and run:


Then (for a mac):

```
pip3 install -e .
cd mc
pytest
```

## Usage

- Command Line Interface
- Python Package

## Command Line

The CLI commands are pretty explorable via help, start with `mc --help`:

```
Usage: mc [OPTIONS] COMMAND [ARGS]...

  Command line interface for MC.

Options:
  --help  Show this message and exit.

Commands:
  build     Build a config with defined sub-pops, modes & activities.
  convert   Read an existing config and write as xml or json.
  diff      Simple diff two configs.
  fill      Read an existing wildcarded config, fill in the target variables...
  find      Find and print config components to terminal.
  gen       Generate a template config: empty|default|test.
  print     Print a config to terminal.
  step      Read an existing config, fill in the target variables and write...
  debug     Debug a config.
```

## Programming Interface

```
from mc import build
```

To facilitate a beautiful future where humans never need edit xml and machines start to explore MATSim simulation config parameter spaces themselves, mc makes a dictionary-like `mc.build.Config` object available. `Config` objects can read and write to MATSim `.xml` config format (and `.json` just in case).

```
config = build.Config(path='default.xml')
config.write(path='temp.json')
config2 = build.Config(path='temp.json')
config == config2
```
```
True
```

`Config` objects consist of nested `Modules`, `ParamSets` and `Params`. All of which will behave like a nested set of dicts. For example supporting getting and setting methods:

```
# get and print module contents:
config['plans'].print()
```
```
module {'name': 'plans'}
    param {'name': 'inputPlansFile', 'value': 'test_inputs/population.xml'}
    param {'name': 'inputPersonAttributesFile', 'value': 'test_inputs/attributes.xml'}
    param {'name': 'subpopulationAttributeName', 'value': 'subpopulation'}
```

```
 # set and print a single param:
config['plans']['inputPlansFile'] = 'test_inputs/new_population.xml'
print(config['plans']['inputPlansFile'])
```
```
test_inputs/new_population.xml
```

Nested setting is allowed, for example for an empty `Config` a new module, paramset and param
 can be set together:
 
```
empty_config = build.Config()
empty_config['global']['coordinateSystem'] = 'EPSG:27700'
...
empty_config.print()
```
```
module {'name': 'global'}
    param {'name': 'coordinateSystem', 'value': 'EPSG:27700'}
```

providing that all keys and values are valid:

```
empty_config = build.Config()
empty_config['NotAModule']['coordinateSystem'] = 'EPSG:27700'
```
```
...
KeyError: "key:'NotAModule' not found in modules"
```

```
empty_config['global']['coordinateSystem'] = 2700
INFO creating new empty module: global
```
```
...
ValueError: Please use value of either type ParamSet, Param or str
```

MATSim configurations include parametersets which look like lists. We therefore suffix
ParamSet keys using `:<uid>` where the uid is most usefully the appropriate parameterset
subpopulation, mode or activity:

```
empty_config.write(path=Path('temp.xml'))
empty_config['planCalcScore']['scoringParameters:high_income']['modeParams:car']['monetaryDistanceRate'] = '-0.0001'
```
```
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

## Find

Both the CLI and API support string searches for config components using an addressing system:

```
config['plans']['inputPlansFile'] = 'PATH'
search = config.find("plans/inputPlansFile")
for i in search:
  i.print()
```

```
param {'name': 'inputPlansFile', 'value': 'PATH'}
```

Find is returning a list because it supports partial addresses which result in multiple finds:

```
search = config.find("modeParams:car/monetaryDistanceRate")
for i in search:
  i.print()
```

```
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg subpopulation A
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg subpopulation B
```

Addresses can omit components, for example if we want to look at all `monetaryDistanceRates` for the default subpopulation (ie from `scoringParameters:default`):

```
search = config.find("scoringParameters:default/monetaryDistanceRate")
# this is equivalent to "*/scoringParameters:default/*/monetaryDistanceRate"
for i in search:
  i.print()
```

```
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg walk
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg bike
param {'name': 'monetaryDistanceRate', 'value': '-0.001'}  # eg pt
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg car
```

Or more simply we can get all `monetaryDistanceRates`:

```
search = config.find("monetaryDistanceRate")
# this is equivalent to "*/*/*/monetaryDistanceRate"
# this is equivalnet to "*/scoringParameters:*/modeParams:*/monetaryDistanceRate"
for i in search:
  i.print()
```

```
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg subpop A walk
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg subpop A bike
param {'name': 'monetaryDistanceRate', 'value': '-0.001'}  # subpop A eg pt
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # subpop A eg car
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg subpop B walk
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg subpop B bike
param {'name': 'monetaryDistanceRate', 'value': '-0.001'}  # eg subpop B pt
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg subpop B car
```

In the examples above, you can see that wildcarding with `*` can be used to return 'all' config elements. The `*` operator tells the find method to search all at a given level. As shown above, it is useful for returning all elements within a parameterset or explicitly describing levels to search.

## Validation

MC has a built-in representation of a valid config structure, specifically the viable names of modules, parametersets and parameters. When reading in an existing config or adding new components, MC will throw validation errors if the valid config structure is not maintained.

```
empty_config = build.Config()
empty_config['NotAModule']['coordinateSystem'] = 'EPSG:27700'
```
```
...
KeyError: "key:'NotAModule' not found in modules"
```

This system is useful for preventing typos, but has to be
[maintained and updated for changes to valid configs](#updating-mc-for-config-changes). The valid mapping is described in the `mc.valid` module.

## Updating MC for Config Changes
An example of how to update the validation mapping can be seen with the addition of a new `hermes` module:

```{xml}
  <module name="hermes" >
      <param name="endTime" value="32:00:00" />
      <param name="flowCapacityFactor" value="0.01" />
      <param name="mainMode" value="car" />
      ...
  </module>
```

In order to make this hermes module available to MC's validation, the following is added to `mc/valid.py`:

```{json}
  "hermes": {
      "params": {
            "mainMode": "car",
            "endTime": "36:00:00",
            "flowCapacityFactor": "0.01",
            ...
      }
  },
```

## Tests

```{bash}
    python -m pytest -vv tests
```

To generate XML & HTML coverage reports to `reports/coverage`:

```{bash}
    ./scripts/code-coverage.sh
```

## Contact

fred.shone@arup.com

## Further Work

* Add more and better debugging
* Populate with some more default configurations
* Add detailed value validation, for example acceptable integer ranges
* Add further debugging by comparing config to other inputs such as transit schedules...
* MC use to support batch config building using a tabular data, but not any more.
The code is still stashed in `old`
