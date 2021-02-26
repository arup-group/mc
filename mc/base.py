"""
Config classes:
- Base
- BaseConfig(Base)
- Module(Base)
- ParamSet(Base)
- Param(Base)

Note that Modules contain ParamSets and Params, Paramsets contain other Paramsets and Params.
In practice the maximum depth of Paramsets is 2.

Note that these classes are hard to split up at the moment due to inheritance and recursive
behaviour creating circular dependency...
"""

from lxml import etree as et
from lxml.etree import Element
from pathlib import Path
import json
from typing import Tuple
from mc.debug import BaseDebug
from mc.valid import VALID_MAP


class Base:
    """
    Base behaviours for configuration classes.
    - dict like methods
    - reading
    - writing
    - debugging and printing
    """

    class_type = ''
    ident = ''
    name = ''
    value = ''
    data = {}
    valid_keys = []
    valid_param_keys = []
    valid_paramset_keys = []
    modules = {}
    params = {}
    parametersets = {}

    # Dictionary like behaviours:

    def __getitem__(self, key):
        """
        Dict like behaviour - get nested config object.
        :param key: str
        :return: config object or value
        """
        raise NotImplementedError

    def get(self, key, default=None):
        """
        Dict like behaviour - get nested config object with default value for missing key.
        :param key: str
        :param default: str
        :return: config object or value
        """
        raise NotImplementedError

    def __delitem__(self, key):
        """
        Dict like behaviour - delete nested config object.
        :param key: str
        :return: None
        """
        if key in self.params:
            del self.params[key]
        else:
            del self.parametersets[key]

    def __setitem__(self, key, value):
        """
        Dict like behaviour - set nested config object.
        :param key: str
        :param value: config object or value
        """
        raise NotImplementedError

    def __iter__(self):
        """
        Dict like behaviour - iterate through nested config objects.
        :return: iterator
        """
        raise NotImplementedError

    def valid_param_key(self, key: str) -> bool:
        """
        Check for valid param key.
        :param key: str
        :return: bool
        """
        if key in self.valid_param_keys:
            return True
        return False

    def is_valid_param_key(self, key) -> None:
        """
        Raise KeyError if not valid param key.
        :param key: str
        """
        if not self.valid_param_key(key):
            raise KeyError(f"'{key}' is not a valid param key for this module")

    def valid_paramset_key(self, key) -> bool:
        """
        Check for valid parameterset key.
        :param key: str
        :return: bool
        """
        if get_paramset_type(key) in self.valid_paramset_keys:
            return True
        return False

    def is_valid_paramset_key(self, key) -> None:
        """
        Raise KeyError if not valid parameterset key.
        :param key: str
        """
        if not self.valid_paramset_key(key):
            raise KeyError(f"'{key}' is not a valid paramset key for this module")

    # Reading/building config from input:

    def build_from_xml(self, xml_object: Element):
        """
        Build config object from xml Element.
        :param xml_object: Element
        """

        for sub_object in xml_object:
            attributes = sub_object.attrib

            if sub_object.tag == "param":
                key = attributes["name"]
                value = attributes["value"]
                self.params[key] = Param(key, value)

            elif sub_object.tag == "module":
                key = attributes["name"]
                self.modules[key] = Module(key, xml_object=sub_object)

            elif sub_object.tag == "parameterset":
                _, key = build_paramset_key(sub_object)
                self.parametersets[key] = ParamSet(key, xml_object=sub_object)

            else:
                continue

    def build_from_json(self, json_object: dict) -> None:
        """
        Build config object from json object.
        :param json_object: dict
        """
        for key, value in json_object.items():

            if key == "params":
                for key2, value2 in value.items():
                    self.params[key2] = Param(key2, value2)
            elif key == "modules":
                for key2, module in value.items():
                    self.modules[key2] = Module(key2, json_object=module)
            elif key == "parametersets":
                for ps_name, paramset in value.items():
                    self.parametersets[ps_name] = ParamSet(ps_name, json_object=paramset)

    # Writing configuration to path

    def write(self, path: Path):
        """
        Write config to given path.
        :param path: pathlib.Path
        :return: None
        """
        if isinstance(path, str):
            path = Path(path)
        if xml_path(path):
            self.write_xml(path)
        elif json_path(path):
            self.write_json(path)
        else:
            raise NameError(f'Unknown data format for path: {path}')

    def write_xml(self, path):
        """
        Write config to given xml path.
        :param path: pathlib.Path
        :return: None
        """
        if isinstance(path, str):
            path = Path(path)
        root = self.build_xml()
        tree = et.tostring(root,
                           pretty_print=True,
                           xml_declaration=False,
                           encoding='UTF-8')
        with open(path, 'wb') as file:
            file.write(b'<?xml version="1.0" ?>\n')
            file.write(b'<!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">\n')
            file.write(tree)

    def write_json(self, path):
        """
        Write config to given json path.
        :param path: pathlib.Path
        :return: None
        """
        if isinstance(path, str):
            path = Path(path)
        data = self.build_json()
        with open(path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    def build_xml(self, top: str) -> Element:
        """
        Recursively build xml elements.
        :param top: str (name of parent)
        :return: Element
        """
        root = et.Element(top)
        dat, = self.data.items()
        root.set(*dat)

        if self.params:
            for param_name, param in self.params.items():
                elem = et.Element('param', name=param_name, value=param.value)
                root.append(elem)
        if self.parametersets:
            for _, paramset in self.parametersets.items():
                elem = paramset.build_xml('parameterset')
                root.append(elem)
        return root

    def build_json(self) -> dict:
        """
        Recursively build json style dict.
        :return: dict
        """
        builds = {}
        if self.params:
            build = {}
            for param_name, param in self.params.items():
                build[param_name] = param.value
            builds['params'] = build
        if self.parametersets:
            build = {}
            for ps_name, paramset in self.parametersets.items():
                build[ps_name] = paramset.build_json()
            builds['parametersets'] = build
        return builds

    # Debugging/printing:

    def print(self, i: int = 0) -> None:
        """
        Recursively print configuration objects.
        :param i: int, starting indentation level.
        """
        indent = "\t" * i
        print(indent, self.class_type, self.data)
        if self.class_type != "param":
            for _, param in self.params.items():
                param.print(i+1)
            for _, paramset in self.parametersets.items():
                paramset.print(i+1)

    def __str__(self) -> str:
        """
        Default string return.
        :return: str
        """
        return f"{self.class_type} (use .print() to print full contents)"

    def __eq__(self, other) -> bool:
        """
        Recursively look inside nested dict like structures for equality.
        :return: bool
        """
        if not isinstance(other, Base):
            raise NotImplementedError("__eq__ only implemented for comparison between same class")

        if not set(self.params) == set(other.params):
            return False
        for k, param in self.params.items():
            if not param == other.params[k]:
                return False

        if not set(self.parametersets) == set(other.parametersets):
            return False

        for k, paramset in self.parametersets.items():
            if not paramset == other.parametersets[k]:
                return False

        return True

    def diff(self, other, location: str = '', diffs: list = None) -> list:
        """
        Recursive method for comparing two config objects and adding diff messages to a existing
        list of
        diffs.
        :param other: config object (BaseConfig, Module, ParamSet, Param)
        :param location: stt
        :param diffs: list
        :return:
        """
        if diffs is None:
            diffs = []

        if not isinstance(other, Base):
            raise NotImplementedError("__eq__ only implemented for comparison between same base class")

        if self.class_type == "config":

            for k, module in self.modules.items():
                other_module = other.modules.get(k)
                if other_module:
                    module.diff(other.modules[k], self.ident, diffs)
                else:
                    diff = f"+ module@{self.ident}: {k}"
                    diffs.extend([diff])

            for k, other_module in other.modules.items():
                module = self.modules.get(k)
                if not module:
                    diff = f"- module@{self.ident}: {k}"
                    diffs.extend([diff])

        elif self.class_type == "param":
            if not self.value == other.value:
                diff = f"+/- param@{location}: {self.name}: {other.value} -> {self.value}"
                diffs.extend([diff])

        elif self.class_type in ['module', 'paramset']:

            for k, param in self.params.items():
                other_param = other.params.get(k)
                if other_param:
                    param.diff(other.params[k], self.ident, diffs)
                else:
                    diff = f"+ param@{self.ident}: {param.data}"
                    diffs.extend([diff])

            for k, other_param in other.params.items():
                param = self.params.get(k)
                if not param:
                    diff = f"- param@{self.ident}: {k}"
                    diffs.extend([diff])

            for k, paramset in self.parametersets.items():
                other_paramset = other.parametersets.get(k)
                if other_paramset:
                    paramset.diff(other.parametersets[k], self.ident, diffs)
                else:
                    diff = f"+ paramset@{self.ident}: {k}"
                    diffs.extend([diff])

            for k, other_paramset in other.parametersets.items():
                paramset = self.parametersets.get(k)
                if not paramset:
                    diff = f"- paramset@{self.ident}: {k}"
                    diffs.extend([diff])

        else:
            raise ValueError(f"Unrecognided class: {self.class_type}")

        return diffs


class BaseConfig(Base, BaseDebug):
    """
    Base Configuration class.
    """
    class_type = "config"

    def __init__(self, path: Path = None) -> None:
        """
        Base configuration object, containing dict of Modules.
        :param path: Path, optional
        """
        self.modules = {}
        self.ident = 'config'
        self.data = {'name': 'config'}
        self.valid_keys = list(VALID_MAP['modules'])

        if isinstance(path, str):
            path = Path(path)

        if path_exists(path):
            if xml_path(path):
                with path.open() as file:
                    root = et.parse(file).getroot()
                    self.build_from_xml(root)
            elif json_path(path):
                with path.open() as file:
                    data = json.load(file)
                    self.build_from_json(data)

    def print(self, i: int = 0) -> None:
        for module in self.modules.values():
            module.print(i)

    def __getitem__(self, key: str):
        if key in self.modules:
            return self.modules[key]

        # build and return new paramset if valid
        if self.valid_key(key):
            print(f"INFO creating new empty module: {key}")
            self.modules[key] = Module(name=key)
            return self.modules[key]

        raise KeyError(f"key:'{key}' not found in modules and not valid")

    def find(self, address: str) -> list:
        """
        Given a string address (refer to the README) recursively search for 
        list of matching config elements.

        Args:
            address (str): string formatted address

        Returns:
            list: found config elements
        """

        list_address = address.strip("/").split("/")
        
        if len(list_address) == 1:  # reached end of address
            address = list_address[0]
            if address in self.modules:
                return [self.modules[address]]
            # if address == "*":
            #     return list(self.modules.values())

        if list_address[0] in self.modules:
            found = list_address.pop(0)
            address = "/".join(list_address)
            search = [self.modules[found].find(address)]
            return [f for g in search for f in g]  # flatten

        if list_address[0] == "*":
            found = list_address.pop(0)
            address = "/".join(list_address)
            search = [m.find(address) for m in self.modules.values()]
            return [f for g in search for f in g]  # flatten

        address = "/".join(list_address)
        search = [m.find(address) for m in self.modules.values()]
        return [f for g in search for f in g]  # flatten

    def __delitem__(self, key):
        del self.modules[key]

    def __setitem__(self, key, value):
        if not isinstance(value, Module):
            raise ValueError("Invalid value: config dict must contain Modules")
        self.is_valid_key(key)
        self.modules[key] = value

    def get(self, key, default=None):
        return self.modules.get(key, default)

    def __iter__(self):
        return iter(self.modules)

    def __eq__(self, other):
        if not isinstance(other, BaseConfig):
            raise NotImplementedError("__eq__ only implemented for comparison between same class")

        if not set(self.modules) == set(other.modules):
            return False
        for k, module in self.modules.items():
            if not module == other.modules[k]:
                return False

        return True

    def build_json(self) -> dict:
        build = {}
        for name, module in self.modules.items():
            build[name] = module.build_json()
        return {"modules": build}

    def build_xml(self, top='config') -> Element:
        root = et.Element(top)
        for module in self.modules.values():
            elem = module.build_xml('module')
            root.append(elem)
        return root

    def valid_key(self, key: str) -> bool:
        """
        Check for valid key.
        :param key: str
        :return: bool
        """
        if key in self.valid_keys:
            return True
        return False

    def is_valid_key(self, key: str) -> None:
        """
        Raises KeyError if key is not valid.
        :param key: str
        """
        if not self.valid_key(key):
            raise KeyError(f"{key} is not a valid module key for configs")


class Module(Base):
    """
    Module class.
    """

    class_type = "module"

    def __init__(self, name, xml_object=None, json_object=None) -> None:
        """
        Module object contains nested parametersets and params.
        :param name: str
        :param xml_object:
        :param json_object:
        """
        self.name = name
        self.ident = self.name
        self.data = {'name': self.name}
        self.params = {}
        self.parametersets = {}

        self.valid_param_keys = list(VALID_MAP['modules'][name].get('params', []))
        self.valid_paramset_keys = [
            get_paramset_type(t) for t in list(VALID_MAP['modules'][name].get('parametersets', []))
        ]
        self.valid_keys = {'valid_params_keys': self.valid_param_keys,
                           'valid_paramset_keys': self.valid_paramset_keys}

        if xml_object is not None:
            self.build_from_xml(xml_object)
        elif json_object is not None:
            self.build_from_json(json_object)

    def __getitem__(self, key):
        if key in self.params:
            return self.params[key].value
        if key in self.parametersets:
            return self.parametersets[key]
        if key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]

        # try to collect list of paramsets
        collected = []
        for _, parameterset in self.parametersets.items():
            if parameterset.type == key:
                collected.append(parameterset)
        if collected:
            print("INFO returning list of collected parametersets")
            return collected

        # build and return new paramset if valid
        if self.valid_paramset_key(key):
            print(f"INFO creating new empty parameterset: {key}")
            self.parametersets[key] = ParamSet(ident=key)
            return self.parametersets[key]

        raise KeyError(f"key:'{key}' not found in params/sets and not valid")

    def find(self, address: str) -> list:
        """
        Given a string address (refer to the README) recursively search for 
        list of matching config elements.

        Args:
            address (str): string formatted address

        Returns:
            list: found config elements
        """

        list_address = address.strip("/").split("/")

        if len(list_address) == 1:  # reached end of address
            address = list_address[0]
            if address in self.params:
                return [self.params[address]]
            if address in self.parametersets:
                return [self.parametersets[address]]
            if address == "*":
                search = [ps.find(address) for ps in self.parametersets.values()]
                return [f for g in search for f in g]  # flatten
            if "*" in address:
                snaps = []
                for candidate in self.parametersets:
                    if specials_snap(candidate, address):
                        snaps.append(self.parametersets[candidate])
                return snaps

        if list_address[0] in self.parametersets:  # regular find recurse
            found = list_address.pop(0)
            address = "/".join(list_address)
            search = [self.parametersets[found].find(address)]
            return [f for g in search for f in g]  # flatten

        if list_address[0] == "*":
            found = list_address.pop(0)
            address = "/".join(list_address)
            search = [ps.find(address) for ps in self.parametersets.values()]
            return [f for g in search for f in g]  # flatten

        if "*" in list_address[0]:  # special find recurse
            snaps= []
            for candidate in self.parametersets:
                if specials_snap(candidate, list_address[0]):
                    snaps.append(self.parametersets[candidate])
            if snaps:
                found = list_address.pop(0)
                address = "/".join(list_address)
                search = [ps.find(address) for ps in snaps]
                return [f for g in search for f in g]  # flatten

        address = "/".join(list_address)  # recurse through everything
        search = [ps.find(address) for ps in self.parametersets.values()]
        return [f for g in search for f in g]  # flatten

    def get(self, key, default=None):
        if key in self.params:
            return self.params[key].value
        if key in self.parametersets:
            return self.parametersets[key]
        if key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]

        return default

    def __setitem__(self, key, value):
        if not isinstance(value, (str, ParamSet, Param)):
            raise ValueError(f"Please use value of either type ParamSet, Param or str")

        if isinstance(value, ParamSet):
            self.is_valid_paramset_key(key)
            self.parametersets[key] = value
        elif isinstance(value, Param):
            self.is_valid_param_key(key)
            self.params[key] = value
        else:
            self.is_valid_param_key(key)
            self.params[key] = Param(key, value)

    def __iter__(self):
        return iter(self.params)


class ParamSet(Base):
    """
    Parameterset class.
    """

    class_type = "paramset"

    def __init__(self, ident, xml_object=None, json_object=None) -> None:
        """
        Parameterset object, holding nested parametersets and params.
        :param ident: str
        :param xml_object: Element
        :param json_object: dict
        """
        self.ident = ident
        self.type = get_paramset_type(ident)
        self.data = {'type': self.type}
        self.params = {}
        self.parametersets = {}
        self.valid_param_keys = list(get_params_search(VALID_MAP, self.type))
        self.valid_paramset_keys = \
            [get_paramset_type(t) for t in list(get_paramsets_search(VALID_MAP, self.type))]
        self.valid_keys = {'valid_params_keys': self.valid_param_keys,
                           'valid_paramset_keys': self.valid_paramset_keys}

        if xml_object is not None:
            self.build_from_xml(xml_object)
        elif json_object is not None:
            self.build_from_json(json_object)

    def __getitem__(self, key):

        if key in self.params:
            return self.params[key].value
        if key in self.parametersets:
            return self.parametersets[key]
        if key + ":default" in self.parametersets:
            print("WARNING assuming '<parameterset>:default' required")
            return self.parametersets[key + ":default"]

        # try to collect list of paramsets
        collected = []
        for _, parameterset in self.parametersets.items():
            if parameterset.type == key:
                collected.append(parameterset)
        if collected:
            print("INFO returning list of collected parametersets")
            return collected

        # build and return new paramset if valid
        if self.valid_paramset_key(key):
            print(f"INFO creating new empty parameterset: {key}")
            self.parametersets[key] = ParamSet(ident=key)
            return self.parametersets[key]

        raise KeyError(f"key:'{key}' not found in params/sets and not valid")

    def find(self, address: str) -> list:
        """
        Given a string address (refer to the README) recursively search for 
        list of matching config elements.

        Args:
            address (str): string formatted address

        Returns:
            list: found config elements
        """

        list_address = address.strip("/").split("/")

        if len(list_address) == 1:  # end recursion as address is all used
            if address in self.params:
                return [self.params[address]]
            if address in self.parametersets:
                return [self.parametersets[address]]
            if address == "*":
                search = [ps.find(address) for ps in self.parametersets.values()]
                flatten = [f for g in search for f in g]  # flatten
                return flatten + list(self.params.values())
            if "*" in address:
                snaps = []
                for candidate in self.parametersets:
                    if specials_snap(candidate, address):
                        snaps.append(self.parametersets[candidate])
                return snaps

        if list_address[0] in self.parametersets:
            found = list_address.pop(0)
            address = "/".join(list_address)
            return self.parametersets[found].find(address)

        # not going to look through params as this isn't end of address

        if list_address[0] == "*":
            found = list_address.pop(0)
            address = "/".join(list_address)
            search = [ps.find(address) for ps in self.parametersets.values()]
            return [f for g in search for f in g]  # flatten

        if "*" in list_address[0]:  # special find recurse
            snaps= []
            for candidate in self.parametersets:
                if specials_snap(candidate, list_address[0]):
                    snaps.append(self.parametersets[candidate])
            if snaps:
                found = list_address.pop(0)
                address = "/".join(list_address)
                search = [m.find(address) for m in snaps]
                return [f for g in search for f in g]  # flatten

        address = "/".join(list_address)  # recurse through everything

        search = [m.find(address) for m in self.parametersets.values()]
        return [f for g in search for f in g]  # flatten
        
    def __setitem__(self, key, value):

        if not isinstance(value, (str, ParamSet, Param)):
            raise ValueError(f"Please use value of either type ParamSet, Param or str")
        if isinstance(value, ParamSet):
            self.is_valid_paramset_key(key)
            self.parametersets[key] = value
        elif isinstance(value, Param):
            self.is_valid_param_key(key)
            self.params[key] = value
        else:
            self.is_valid_param_key(key)
            self.params[key] = Param(key, value)

    def __iter__(self):
        return iter(self.params)

    def get(self, key, default=None):

        if key in self.params:
            return self.params[key].value
        if key in self.parametersets:
            return self.parametersets[key]
        if key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]

        return default


class Param(Base):
    """
    Param class.
    """

    class_type = "param"

    def __init__(self, name: str, value: str) -> None:
        """
        Parameter object.
        :param name: str
        :param value: str
        """
        self.ident = name
        self.name = name
        self.value = value
        self.data = {'name': self.name, 'value': self.value}
    
    def __str__(self) -> str:
        return super().__str__()

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        raise NotImplementedError('dict type delete not supported for params.')

    def __eq__(self, other):
        if not isinstance(other, Base):
            raise NotImplementedError("__eq__ only implemented for comparison between same class")

        if not self.value == other.value:
            return False

        return True


def specials_snap(a, b, divider=":", ignore="*"):
    """
    Special function to check for key matches with consideration of
    special character '*' that represents 'all'.
    Note that snaps will only be checked as far as the shorter string.
    """
    list_a = a.split(divider)
    list_b = b.split(divider)
    for a, b in zip(list_a, list_b):
        if not (a == ignore or b == ignore or a == b):
            return False
    return True


def path_exists(path: Path) -> bool:
    """
    Check if path exists.
    :param path: pathlib Path
    :return: bool
    """
    if path:
        if not isinstance(path, Path):
            raise TypeError('exists() function only implemented for pathlib Path objects.')
        if path.exists():
            return True
    return False


def xml_path(path: Path) -> bool:
    """
    Check if path has .xml suffix.
    :param path: pathlib Path
    :return: bool
    """
    if path and path.suffix == ".xml":
        return True
    return False


def json_path(path: Path) -> bool:
    """
    Check if path has .json suffix.
    :param path: pathlib Path
    :return: bool
    """
    if path and path.suffix == ".json":
        return True
    return False


def build_paramset_key(elem: et.Element) -> Tuple[str, str]:
    """
    Function to extract the appropriate suffix from a given parameterset xml element. Returns the
    element type (either for subpopulation, mode or activity) and new key. This key is used to
    provide unique keys for parametersets that are otherwise held as lists in xml.
    :param elem: et.Element (parameterset)
    :return: tuple(str, str)
    """
    paramset_type = elem.attrib["type"]

    if paramset_type == "activityParams":
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='activityType']")]
        key = paramset_type + ":" + name
        return paramset_type, key

    if paramset_type in ["modeParams", "teleportedModeParameters", "intermodalAccessEgress"]:
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='mode']")]
        key = paramset_type + ":" + name
        return paramset_type, key

    if paramset_type in ["scoringParameters"]:
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='subpopulation']")]
        key = paramset_type + ":" + name
        return paramset_type, key

    if paramset_type in ["strategysettings"]:
        subpop, = [p.attrib['value'] for p in elem.xpath("./param[@name='subpopulation']")]
        strategy, = [p.attrib['value'] for p in elem.xpath("./param[@name='strategyName']")]
        key = paramset_type + ":" + subpop + ":" + strategy
        return paramset_type, key

    if paramset_type in ["modeMapping"]:
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='passengerMode']")]
        key = paramset_type + ":" + name
        return paramset_type, key

    raise ValueError(f"unrecognised parameterset of type: {paramset_type} in xml")


def sets_diff(self: list, other: list, name: str, loc: str) -> list:
    """
    Function to compare the sets of two lists. Returns a list of diff strings containing name and
    location.
    :param self: list
    :param other: list
    :param name: str
    :param loc: str
    :return: list[str]
    """
    diffs = []
    self_extra = set(self) - set(other)
    if self_extra:
        diffs.append(f"+ {name}@{loc}: {list(self_extra)}")
    other_extra = set(other) - set(self)
    if other_extra:
        diffs.append(f"- {name}@{loc}: {list(other_extra)}")
    return diffs


def get_paramset_type(key: str) -> str:
    """
    Return parameterset type from unique key.
    :param key: str
    :return: str
    """
    return key.split(':')[0]


def get_params_search(dic: dict, target: str) -> dict:
    """
    Recursively search nested dictionary for target parameters.
    :param dic: dict
    :param target: str
    :return: dict
    """
    target = get_paramset_type(target)

    if target in dic:
        if 'params' in dic[target]:
            return dic[target]['params']
    for _, value in dic.items():
        if isinstance(value, dict):
            item = get_params_search(value, target)
            if item:
                return item
    return {}


def get_paramsets_search(dic: dict, target: str) -> dict:
    """
    Recursively search nested dictionary for target parametersets.
    :param dic: dict
    :param target: str
    :return: dict
    """
    target = get_paramset_type(target)

    if target in dic:
        if 'parametersets' in dic[target]:
            return dic[target]['parametersets']
    for _, value in dic.items():
        if isinstance(value, dict):
            item = get_paramsets_search(value, target)
            if item:
                return item
    return {}
