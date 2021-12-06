# Master of Ceremonies

Interfaces for making MATSim configuration less painful.

Modify, generate, diff and debug configs from the command line.

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

MC requires python3.5 or above.

```{bash}
git@github.com:arup-group/mc.git
cd mc
virtualenv -p python3.7 venv
source venv/bin/activate
pip3 install -e .
pytest
```

Although we recomment using a virtual environment as shown above (`virtualenv...` & `source...`), mc requirements are minimal so you may get away with your default environment.

## Usage

MC has a Command Line Interface (CLI), but also a useful pythonic API for bespoke applications.

The CLI provides a number of features, introduced below. These include some general purpose functionality such as `diff`, as well as some bespoke features required for other tooling, such as `paramreplace`, `step` and `autostep`.

We are also interested in maintaining a `debug` command to catch common config mistakes. If you have a feature in mind, such as debugging of a common config mistake please add it to the project issues.

## Command Line

The CLI commands are pretty explorable via help, start with `mc --help`:

```{bash}
Usage: mc [OPTIONS] COMMAND [ARGS]...

  Command line interface for MC.

Options:
  --help  Show this message and exit.

Commands:
  autostep      Read config, apply overrides and write out.
  build         Build a config with defined sub-pops, modes & activities.
  convert       Read an existing config and write as xml or json.
  debug         Debug a config.
  diff          Simple diff two configs.
  fill          Read a wildcarded config, apply overrides and write.
  find          Find and print config components to terminal.
  gen           Generate a template config: empty|default|test.
  matchreplace  Read wildcarded config, apply overrides and write.
  paramreplace  Read config, apply overrides and write out.
  print         Print a config to terminal.
  step          Read config, apply overrides and write out.
```

### Print Example

(from mc root)

```{bash}
❯ mc print tests/test_data/test_config.xml
```

```{bash}
module {'name': 'global'}
   param {'name': 'coordinateSystem', 'value': 'EPSG:27700'}
   param {'name': 'insistingOnDeprecatedConfigVersion', 'value': 'true'}
   param {'name': 'numberOfThreads', 'value': '32'}
   param {'name': 'randomSeed', 'value': '4711'}
 module {'name': 'network'}
   param {'name': 'inputCRS', 'value': 'null'}
   param {'name': 'inputChangeEventsFile', 'value': 'null'}
   param {'name': 'inputNetworkFile', 'value': '~/test/network.xml'}
   param {'name': 'laneDefinitionsFile', 'value': 'null'}
   param {'name': 'timeVariantNetwork', 'value': 'false'}
   ...
```

### Diff Example

(from mc root)

```{bash}
❯ mc diff tests/test_data/test_config.xml tests/test_data/test_config_v12.xml
```

```{bash}
- param@plans: insistingOnUsingDeprecatedPersonAttributeFile
- param@plans: inputPersonAttributesFile
+/- param@strategy: fractionOfIterationsToDisableInnovation: 0.95 -> 0.9
```

### Find Example

(from mc root)

```{bash}
❯ mc find tests/test_data/test_config.xml coordinateSystem
```

```{bash}
param {'name': 'coordinateSystem', 'value': 'EPSG:27700'}
```

You can read about more complex addressing in [Find](##find).

## Programming Interface

```{python}
from mc import build
```

To facilitate a beautiful future where humans never need edit xml and machines start to explore MATSim simulation config parameter spaces themselves, mc makes a dictionary-like `mc.build.Config` object available. `Config` objects can read and write to MATSim `.xml` config format (and `.json` just in case).

```{python}
config = build.Config(path='tests/test_data/test_config.xml')
config.write(path='temp.json')
config2 = build.Config(path='temp.json')
config == config2
```

```{python}
True
```

### Setting and Getting

`Config` objects consist of nested `Modules`, `ParamSets` and `Params` (just like a MATSim xml formatted config). All of which will behave like a nested set of dicts. For example supporting getting and setting methods:

```{python}
# get and print module contents:
config['plans'].print()
```

```{python}
module {'name': 'plans'}
    param {'name': 'inputPlansFile', 'value': 'test_inputs/population.xml'}
    param {'name': 'inputPersonAttributesFile', 'value': 'test_inputs/attributes.xml'}
    param {'name': 'subpopulationAttributeName', 'value': 'subpopulation'}
```

```{python}
 # set and print a single param:
config['plans']['inputPlansFile'] = 'test_inputs/new_population.xml'
print(config['plans']['inputPlansFile'])
```

```{python}
test_inputs/new_population.xml
```

### Nested Setting and Getting

Nested setting is allowed, for example for an empty `Config` a new module, paramset and param
 can be set together:

```{python}
empty_config = build.Config()
empty_config['global']['coordinateSystem'] = 'EPSG:27700'
...
empty_config.print()
```

```{python}
module {'name': 'global'}
    param {'name': 'coordinateSystem', 'value': 'EPSG:27700'}
```

### Validation of Keys and Values

Setting requires that keys are valid:

```{python}
empty_config = build.Config()
empty_config['NotAModule']['coordinateSystem'] = 'EPSG:27700'
```

```{python}
...
KeyError: "key:'NotAModule' not found in modules"
```

...and that values are valid:

```{python}
empty_config['global']['coordinateSystem'] = {"crs": "27700"}

```

```{python}
INFO creating new empty module: global
ValueError: Please use value of either type ParamSet, Param or str
```

Nested objects can be explicitly accessed via the parent attributes, ie `.modules.values()`, `.parametersets.values()`, `params.values()`. Valid keys (ignoring suffixes) for nestable
objects via `.valid_keys`. Note that valid keys and values are hardcoded in `mc.valid`.

### Unique Parameterset Keys

MATSim configurations include parametersets for which the unique identification (such as the mode or subpopulation) is contained as a parameter. So that we can provide unique keys for the parameterset, we therefore suffix ParamSet keys as `<paramset_name>:<uid>` where `uid` is the appropriate parameterset
subpopulation, mode or activity:

```{python}
empty_config.write(path=Path('temp.xml'))
empty_config['planCalcScore']['scoringParameters:high_income']['modeParams:car']['monetaryDistanceRate'] = '-0.0001'
```

```{python}
INFO creating new empty module: planCalcScore
INFO creating new empty parameterset: scoringParameters:high_income
INFO creating new empty parameterset: modeParams:car
```

In this case we have created a scoring parameterset for the `high_income` subpopulation and a mode parameterset for `car`.

When writing to `.xml` these suffixes are ignored, writing a clean usable config. When reading in
an existing config, these suffixes are automatically generated.

**WARNING: Not specifying a suffix will generally be assumed as using `<paramset_name>:default`.**

## Find

Both the CLI and API support searches for config components using an addressing system. The addressing system uses a string format with `/` to denote a nested parameterset or parameter. This allows changes to be easilly passed as commands via common web interfaces for example.

```{python}
config = build.Config(path='tests/test_data/test_config.xml')
search = config.find("plans/inputPlansFile")
for i in search:
  i.print()
```

```{python}
param {'name': 'inputPlansFile', 'value': '~/test/population.xml.gz'}
```

Find is returning a list because it supports partial addresses which result in multiple finds:

```{python}
search = config.find("modeParams:car/monetaryDistanceRate")
for i in search:
  i.print()
```

```{python}
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg subpopulation A
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg subpopulation B
```

Addresses can omit components, for example if we want to look at all `monetaryDistanceRates` for the default subpopulation (ie from `scoringParameters:default`):

```{python}
search = config.find("scoringParameters:default/monetaryDistanceRate")
# this is equivalent to "*/scoringParameters:default/*/monetaryDistanceRate"
for i in search:
  i.print()
```

```{python}
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg walk
param {'name': 'monetaryDistanceRate', 'value': '-0.0'}  # eg bike
param {'name': 'monetaryDistanceRate', 'value': '-0.001'}  # eg pt
param {'name': 'monetaryDistanceRate', 'value': '-0.0001'}  # eg car
```

Or more simply we can get all `monetaryDistanceRates`:

```{python}
search = config.find("monetaryDistanceRate")
# this is equivalent to "*/*/*/monetaryDistanceRate"
# this is equivalnet to "*/scoringParameters:*/modeParams:*/monetaryDistanceRate"
for i in search:
  i.print()
```

```{python}
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

### Find and Set

Note that the `find` method is returning a reference to the found config objects, which can then be set:

```{python}
config.find("plans/inputPlansFile")[0] = "NEW/PATH"
```

## Validation

MC has a built-in representation of a valid config structure, specifically the viable names of modules, parametersets and parameters. When reading in an existing config or adding new components, MC will throw validation errors if the valid config structure is not maintained.

```{python}
empty_config = build.Config()
empty_config['NotAModule']['coordinateSystem'] = 'EPSG:27700'
```

```{python}
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
* Update default configurations
* Print a high level summary to terminal (scaling/subpops, modes etc)
* Add detailed value validation, for example acceptable integer ranges
* Add further debugging by comparing config to other inputs such as transit schedules
