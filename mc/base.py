from lxml import etree as et
import os
import json
from mc.validation import BuildValidator
from mc.valid import valid_map


def is_xml(path):
    if path and path.exists() and path.suffix == ".xml":
        return True


def is_json(path):
    if path and path.exists() and path.suffix == ".json":
        return True


def build_param_set_name(elem):
    ps_type = elem.attrib["type"]

    if ps_type == "activityParams":
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='activityType']")]
        key = ps_type + ":" + name
        return ps_type, key

    elif ps_type in ["modeParams", "teleportedModeParameters"]:
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='mode']")]
        key = ps_type + ":" + name
        return ps_type, key

    elif ps_type in ["scoringParameters", "strategysettings"]:
        name, = [p.attrib['value'] for p in elem.xpath("./param[@name='subpopulation']")]
        key = ps_type + ":" + name
        return ps_type, key

    raise ValueError(f"unrecognised parameterset of type: {ps_type} in xml")


def diff(self, other, name, loc):
    diffs = []
    self_extra = set(self) - set(other)
    if self_extra:
        diffs.append(f"+ {name}@{loc}: {list(self_extra)}")
    other_extra = set(other) - set(self)
    if other_extra:
        diffs.append(f"- {name}@{loc}: {list(other_extra)}")
    return diffs


def get_paramset_type(key):
    return key.split(':')[0]


def get_params_search(d, target):

    target = get_paramset_type(target)

    if target in d:
        if 'params' in d[target]:
            return d[target]['params']
    for k, v in d.items():
        if isinstance(v, dict):
            item = get_params_search(v, target)
            if item:
                return item
    return []


def get_paramsets_search(d, target):

    target = get_paramset_type(target)

    if target in d:
        if 'parametersets' in d[target]:
            return d[target]['parametersets']
    for k, v in d.items():
        if isinstance(v, dict):
            item = get_paramsets_search(v, target)
            if item:
                return item
    return []


class BaseBuilder:

    def print(self, i):
        indent = "\t" * i
        print(indent, self.class_type, self.data)
        if self.class_type != "param":
            for param_name, param in self.params.items():
                param.print(i+1)
            for ps_name, paramset in self.parametersets.items():
                paramset.print(i+1)

    def build_from_xml(self, xml_object):
        """
        Build config object from xml object
        :param xml_object: xml object
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
                ps_type, key = build_param_set_name(sub_object)
                self.parametersets[key] = ParamSet(key, xml_object=sub_object)

            else:
                continue

    def build_from_json(self, json_object):
        """
        Build config object from json object
        :param json_object: json object
        """
        for k, v in json_object.items():

            if k == "params":
                for name, value in v.items():
                    self.params[name] = Param(name, value)
            elif k == "modules":
                for name, module in v.items():
                    self.modules[name] = Module(name, json_object=module)
            elif k == "parametersets":
                for ps_name, paramset in v.items():
                    type_set = ps_name.split(":")[0]
                    self.parametersets[ps_name] = ParamSet(ps_name, json_object=paramset)

    def build_elems(self, top):
        root = et.Element(top)
        d, = self.data.items()
        root.set(*d)

        if self.params:
            for param_name, param in self.params.items():
                c = et.Element('param', name=param_name, value=param.value)
                root.append(c)
        if self.parametersets:
            for ps_name, paramset in self.parametersets.items():
                c = paramset.build_elems('parameterset')
                root.append(c)
        return root

    def build_dicts(self):
        builds = {}
        if self.params:
            build = {}
            for param_name, param in self.params.items():
                build[param_name] = param.value
            builds['params'] = build
        if self.parametersets:
            build = {}
            for ps_name, paramset in self.parametersets.items():
                build[ps_name] = paramset.build_dicts()
            builds['parametersets'] = build
        return builds

    def __str__(self):
        return f"{self.class_type}, use .print() to print full output"

    def add_diffs(self, other, location='', diffs=[]):
        if not isinstance(other, BaseBuilder):
            raise NotImplemented("__eq__ only implemented for comparison between same base class")

        if self.class_type == "config":

            for k, module in self.modules.items():
                other_module = other.modules.get(k)
                if other_module:
                    module.add_diffs(other.modules[k], self.ident, diffs)
                else:
                    d = f"+ module@{self.ident}: {k}"
                    diffs.extend([d])

            for k, other_module in other.modules.items():
                module = self.modules.get(k)
                if not module:
                    d = f"- module@{self.ident}: {k}"
                    diffs.extend([d])

        elif self.class_type == "param":
            if not self.value == other.value:
                d = f"+/- param@{location}: {self.name}: {other.value} -> {self.value}"
                diffs.extend([d])

        elif self.class_type in ['module', 'paramset']:

            for k, param in self.params.items():
                other_param = other.params.get(k)
                if other_param:
                    param.add_diffs(other.params[k], self.ident, diffs)
                else:
                    d = f"+ param@{self.ident}: {param.data}"
                    diffs.extend([d])

            for k, other_param in other.params.items():
                param = self.params.get(k)
                if not param:
                    d = f"- param@{self.ident}: {k}"
                    diffs.extend([d])

            for k, paramset in self.parametersets.items():
                other_paramset = other.parametersets.get(k)
                if other_paramset:
                    paramset.add_diffs(other.parametersets[k], self.ident, diffs)
                else:
                    d = f"+ paramset@{self.ident}: {k}"
                    diffs.extend([d])

            for k, other_paramset in other.parametersets.items():
                paramset = self.parametersets.get(k)
                if not paramset:
                    d = f"- paramset@{self.ident}: {k}"
                    diffs.extend([d])

        else:
            raise ValueError(f"Unrecognided class: {self.class_type}")

        return diffs


class _Config(BaseBuilder, BuildValidator):

    class_type = "config"

    def __init__(self, path=None):
        self.modules = {}
        self.ident = 'config'
        self.data = {'name': 'config'}
        self.valid_keys = list(valid_map['modules'])

        if is_xml(path):
            with path.open() as f:
                root = et.parse(f).getroot()
                self.build_from_xml(root)
        elif is_json(path):
            with path.open() as f:
                data = json.load(f)
                self.build_from_json(data)

    def __getitem__(self, key):
        return self.modules[key]

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
        if not isinstance(other, _Config):
            raise NotImplemented("__eq__ only implemented for comparison between same class")

        if not set(self.modules) == set(other.modules):
            return False
        for k, module in self.modules.items():
            if not module == other.modules[k]:
                return False

        return True

    def diff(self, other):
        raise NotImplementedError

    def print(self):
        for module in self.modules.values():
            module.print(1)

    def write_xml(self, path):
        root = self.build_xml()
        tree = et.tostring(root,
                           pretty_print=True,
                           xml_declaration=False,
                           encoding='UTF-8')
        with open(path, 'wb') as f:
            f.write(b'<?xml version="1.0" ?>\n')
            f.write(b'<!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">\n')
            f.write(tree)

    def build_json(self):
        build = {}
        for name, module in self.modules.items():
            build[name] = module.build_dicts()
        return {"modules": build}

    def write_json(self, path):
        data = self.build_json()
        with open(path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    def build_xml(self):
        root = et.Element('config')
        for name, module in self.modules.items():
            c = module.build_elems('module')
            root.append(c)

        return root

    def build_elems(self, top):
        raise NotImplementedError

    def build_dicts(self):
        raise NotImplementedError

    def is_valid_key(self, key):
        if key not in self.valid_keys:
            raise KeyError(f"{key} is not a valid module key for configs")


class Module(BaseBuilder):

    class_type = "module"

    def __init__(self, name, xml_object=None, json_object=None):
        self.name = name
        self.ident = self.name
        self.data = {'name': self.name}
        self.params = {}
        self.parametersets = {}

        self.valid_param_keys = list(valid_map['modules'][name].get('params', []))
        self.valid_paramset_keys = [get_paramset_type(t) for t in list(valid_map['modules'][name].get('parametersets', []))]

        if xml_object is not None:
            self.build_from_xml(xml_object)
        elif json_object is not None:
            self.build_from_json(json_object)

    def __getitem__(self, key):
        if key in self.params:
            return self.params[key].value
        elif key in self.parametersets:
            return self.parametersets[key]
        elif key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]
        else:
            raise KeyError(f"key:'{key}' not found in params/sets")

    def get(self, key, default=None):
        if key in self.params:
            return self.params[key].value
        elif key in self.parametersets:
            return self.parametersets[key]
        elif key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]
        else:
            return default

    def __setitem__(self, key, value):
        if isinstance(value, ParamSet):
            self.is_valid_paramset_key(key)
            self.parametersets[key] = value
        elif isinstance(value, Param):
            self.is_valid_param_key(key)
            self.params[key] = value
        elif isinstance(value, str):
            self.is_valid_param_key(key)
            self.params[key] = Param(key, value)
        else:
            raise KeyError(f"key:'{key}' not found in params/sets and could not build new param from value:{value}")

    def __iter__(self):
        return iter(self.params)

    def __eq__(self, other):
        if not isinstance(other, BaseBuilder):
            raise NotImplemented("__eq__ only implemented for comparison between same class")

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

    def is_valid_param_key(self, key):
        if key not in self.valid_param_keys:
            raise KeyError(f"'{key}' is not a valid param key for this module")

    def is_valid_paramset_key(self, key):
        if get_paramset_type(key) not in self.valid_paramset_keys:
            raise KeyError(f"'{key}' is not a valid paramset key for this module")


class ParamSet(BaseBuilder):

    class_type = "paramset"

    def __init__(self, ident, xml_object=None, json_object=None):
        self.ident = ident
        self.type = get_paramset_type(ident)
        self.data = {'type': self.type}
        self.params = {}
        self.parametersets = {}
        self.valid_param_keys = list(get_params_search(valid_map, self.type))
        self.valid_paramset_keys = [get_paramset_type(t) for t in list(get_paramsets_search(valid_map, self.type))]

        if xml_object is not None:
            self.build_from_xml(xml_object)
        elif json_object is not None:
            self.build_from_json(json_object)

    def __getitem__(self, key):
        if key in self.params:
            return self.params[key].value
        elif key in self.parametersets:
            return self.parametersets[key]
        elif key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]
        else:
            collected = []
            for _, parameterset in self.parametersets.items():
                if parameterset.type == key:
                    collected.append(parameterset)
            if collected:
                return collected
            else:
                raise KeyError(f"key:'{key}' not found in params/sets")

    def __setitem__(self, key, value):
        if isinstance(value, ParamSet):
            self.is_valid_paramset_key(key)
            self.parametersets[key] = value
        elif isinstance(value, Param):
            self.is_valid_param_key(key)
            self.params[key] = value
        elif isinstance(value, str):
            self.is_valid_param_key(key)
            self.params[key] = Param(key, value)
        else:
            raise KeyError(f"key:'{key}' not found in params/sets and could not build new param from value:{value}")

    def __iter__(self):
        return iter(self.params)

    def get(self, key, default=None):
        if key in self.params:
            return self.params[key].value
        elif key in self.parametersets:
            return self.parametersets[key]
        elif key + ":default" in self.parametersets:
            print("WARNING assuming 'default' required")
            return self.parametersets[key + ":default"]
        else:
            return default

    def __eq__(self, other):
        if not isinstance(other, BaseBuilder):
            raise NotImplemented("__eq__ only implemented for comparison between same class")

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

    def is_valid_param_key(self, key):
        if key not in self.valid_param_keys:
            raise KeyError(f"'{key}' is not a valid param key for this module")

    def is_valid_paramset_key(self, key):
        if get_paramset_type(key) not in self.valid_paramset_keys:
            raise KeyError(f"'{key}' is not a valid paramset key for this module")


class Param(BaseBuilder):

    class_type = "param"

    def __init__(self, name, value):
        self.ident = name
        self.name = name
        self.value = value
        self.data = {'name': self.name, 'value': self.value}

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, other):
        if not isinstance(other, BaseBuilder):
            raise NotImplemented("__eq__ only implemented for comparison between same class")

        if not self.value == other.value:
            return False

        return True







