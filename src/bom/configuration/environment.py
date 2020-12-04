""" environment.py """


import dataclasses
import os
from typing import Union


@dataclasses.dataclass
class Environment:
    """ Environment """

    env: str


ENVIRONMENTS = {"dev": Environment(env="dev")}


def get_env(
    environment: Union[str, Environment, None]  # pylint: disable=unsubscriptable-object
) -> Environment:
    """ get_env """

    if isinstance(environment, str) and environment in ENVIRONMENTS:
        return ENVIRONMENTS[environment]

    if isinstance(environment, Environment):
        return environment

    config_var = os.getenv("ENV")

    if isinstance(config_var, str) and config_var in ENVIRONMENTS:
        return ENVIRONMENTS[config_var]

    raise ValueError(
        "You must define an environment."
        " Please pass a valid environment or use"
        " the environment variable `ENV`."
    )
