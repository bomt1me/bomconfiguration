""" manager.py """


import glob
import os
from pathlib import Path
import sys
from typing import Union, List

import pyhocon

from . import environment, config


def load(
    env: Union[str, None] = None,  # pylint: disable=unsubscriptable-object
    cwd: Union[str, None] = None,  # pylint: disable=unsubscriptable-object
    paths: Union[List[str], None] = None,  # pylint: disable=unsubscriptable-object
) -> config.Config:
    """ load """

    if env is None:
        env = os.getenv("ENV")

    if cwd is None:
        cwd = os.getenv("CONFIG_DIR", os.getcwd())

    env_found = environment.get_env(env)

    if paths is None:
        paths = sys.path

    confs = []

    confs += list(glob.glob("./**/application.conf", recursive=True))
    confs += list(glob.glob(f"./**/application.{env_found.env}.conf", recursive=True))
    for path in paths:
        confs += list(
            glob.glob(str(Path(path).absolute()) + "/**/reference.conf", recursive=True)
        )
    for path in paths:
        confs += list(
            glob.glob(
                str(Path(path).absolute()) + f"/**/reference.{env_found.env}.conf",
                recursive=True,
            )
        )

    found_confs = set()
    unique_confs = []
    for conf in confs:
        if conf not in found_confs:
            unique_confs.append(conf)
            found_confs.add(conf)

    complete_conf: Union[  # pylint: disable=unsubscriptable-object
        None, pyhocon.ConfigTree
    ] = None
    for conf in unique_confs:
        if complete_conf is None:
            complete_conf = pyhocon.ConfigFactory.parse_file(conf)
        else:
            new_conf = pyhocon.ConfigFactory.parse_file(conf)
            complete_conf = new_conf.with_fallback(complete_conf)

    if complete_conf is None:
        ret_conf = config.Config()
        ret_conf["env"] = env_found.env
        return ret_conf

    complete_conf["env"] = env_found.env
    return config.Config(complete_conf)
