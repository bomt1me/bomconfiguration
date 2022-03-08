from typing import Optional, Union

import dataclasses
import os


@dataclasses.dataclass
class Environment:
    name: str


ENVIRONMENTS = {
    "dev": Environment(name="dev"),
    "qa": Environment(name="qa"),
    "prod": Environment(name="prod"),
}


def get_env(env: Optional[Union[str, Environment]] = None) -> Environment:
    if env is None:
        env = os.getenv("ENV")

    if isinstance(env, Environment):
        return env

    if env not in ENVIRONMENTS:
        raise ValueError("`ENV` environment variable must be specified.")

    return ENVIRONMENTS[env]
