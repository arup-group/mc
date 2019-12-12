import numpy as np
from typing import Tuple

from mc.base import Base, BaseConfig, Param


def triangle(lower=0, centre=20.0, upper=100.0, digits=1):
    """
    Sample from triangle distribution.
    :param lower: float
    :param centre: float
    :param upper: float
    :param digits: int
    :return: str
    """
    return str(round(np.random.triangular(lower, centre, upper), digits))


def normal(mu=0.0, sigma=1.0, upper_conf=None, lower=float('-inf'), upper=float('inf'), digits=1):
    """
    Sample from a normal distribution of mean mu and var sigma. If upper_conf is given this
    replaces sigma assuming that the upper_conf is 3 standard deviations from the mean. ie that
    sigma = (upper_conf - mu) / 3. This corresponds to a single sided ~95% confidence interval.
    Samples are taken until one is found within lower and upper bounds.
    Digits is the number of decimal places rounded to.
    :param mu: float
    :param sigma: float
    :param upper_conf: float
    :param lower: float
    :param upper: float
    :param digits: int
    :return: str
    """
    if upper_conf:
        sigma = (upper_conf - mu) / 3
    while True:
        s = np.random.normal(mu, sigma)
        if (s >= lower) and (s <= upper):
            return str(round(s, digits))


def exponential(beta=1.0, scale=1.0, base=0.0, lower=float('-inf'), upper=float('inf'), digits=1):
    """
    Sample from a exponential distribution of beta. Sample can be rescaled and rebased as required.
    Samples are taken until one is found within lower and upper bounds.
    Digits is the number of decimal places rounded to.
    :param beta: float
    :param scale: float
    :param base: float
    :param lower: float
    :param upper: float
    :param digits: int
    :return: str
    """
    while True:
        s = scale * (np.random.exponential(1/beta) + base)
        if (s >= lower) and (s <= upper):
            return str(round(s, digits))


DISTRIBUTION_MAP = {
    'triangle': triangle,
    'normal': normal,
    'exponential': exponential
}


def mutate(param: Param, mutator_params: dict):

        distribution_key = mutator_params.get('distribution')
        if not distribution_key:
            raise IOError(f"Cannot find distribution key in mutator config: {mutator_params}")
        del mutator_params['distribution']

        distribution = DISTRIBUTION_MAP.get(distribution_key)
        if not distribution:
            raise KeyError(
                f"Unknown mutate distribution key found: {distribution_key}, "
                f"use: {DISTRIBUTION_MAP}"
            )

        param.value = distribution(**mutator_params)


def yield_pairs(master: Base, slave: Base) -> Tuple[Param, Param]:
    """
    Traverses through master config yielding param objects with matching slave param object.
    If slave object is unavailable, raises a KeyError.
    Supports key suffix ":*" for parametersets, used to match all slave paramsets with same name.
    This is used for matching scoring sets for all subpopulations for example.
    :param master: BaseConfig
    :param slave: BaseConfig
    :return: yield Tuple(Param, Param)
    """
    if master.params:
        for p, mutate_param in master.params.items():

            if p not in slave.params:
                raise KeyError(f"param '{p}' not found in target config")

            yield mutate_param, slave.params[p]

    if master.modules:
        for m, mutate_module in master.modules.items():

            if m not in slave.modules:
                raise KeyError(f"module '{m}' not found in target config")

            yield from yield_pairs(mutate_module, slave.modules[m])

    if master.parametersets:
        for ps, mutate_paramset in master.parametersets.items():

            if ps.split(':')[-1] == '*':  # need to iterate through all slave paramsets
                for cps, config_parameterset in slave.parametersets.items():
                    if ps.split(':')[0] == cps.split(':')[0]:
                        yield from yield_pairs(mutate_paramset, config_parameterset)

            else:
                if ps not in slave.parametersets:
                    raise KeyError(f"parameterset '{ps}' not found in target config")

                yield from yield_pairs(mutate_paramset, slave.parametersets[ps])


def find_and_mutate(config: BaseConfig, mutate_config: BaseConfig):

    """
    Mutates config params as per the mutate config distributions.
    :param config: BaseConfig
    :param mutate_config: BaseConfig
    :return: None
    """

    for mutate_param, config_param in yield_pairs(mutate_config, config):
        mutate(config_param, mutate_param)
