from typing import Any, Dict, List, Optional, Union

import glob
import json
import os
import sys

from bom.configuration import configtree, constants, environment


def fallback(high_precedence: Dict[str, Any], lower_precedence: Dict[str, Any]) -> None:
    for key, value in lower_precedence.items():
        if key not in high_precedence:
            high_precedence[key] = value
        else:
            if isinstance(value, dict):
                fallback(high_precedence[key], lower_precedence[key])
            else:
                pass


def interpolate_env_var(  # pylint: disable=too-many-return-statements
    value: str,
) -> Optional[str]:
    match = constants.ENV_VAR_RE.match(value)
    if not match:
        return value

    env_var = match.group(2)
    condition = match.group(3)
    default = match.group(4)

    if condition is None:
        return os.getenv(env_var)

    if condition == ":-":
        return os.getenv(env_var) or default

    if condition == ":?":
        found_var = os.getenv(env_var)
        if not found_var:
            raise ValueError(f"{value} is unset or empty. Msg -> {default}.")

        return found_var

    if condition == "?":
        found_var = os.getenv(env_var)
        if found_var is None:
            raise ValueError(f"{value} is unset. Msg -> {default}.")

        return found_var

    if condition == "-":
        found_var = os.getenv(env_var)
        if found_var is None:
            return default

        return found_var

    raise ValueError(f"{value} is an invalid environment variable.")


def decoder_hook(obj: Any) -> Any:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = interpolate_env_var(value)

    return obj


class CustomJsonDecoder(json.JSONDecoder):
    def __init__(self, **kwargs) -> None:  # type: ignore
        super().__init__(object_hook=decoder_hook, **kwargs)


def load_from_fileiter(file_iter: List[str], deduped_filepaths: Dict[str, Any]) -> None:
    for filepath in file_iter:
        if filepath not in deduped_filepaths:
            deduped_filepaths[filepath] = None


def load(
    *,
    env: Optional[Union[str, environment.Environment]] = None,
    config_dir: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> configtree.ConfigTree:
    """
    Load configuration files from local filesystem. Download any cloud
    storage configurations to filesystem first.

    In order of priority from highest to lowest priority:

    1. Command line
    2. Local path override
    3. Local path env
    4. Local path
    5. System path env
    6. System path
    """

    if not kwargs:
        kwargs = {}

    env = environment.get_env()

    if config_dir is None:
        config_dir = os.getenv("CONFIG_DIR", os.getcwd())

    deduped_filepaths: Dict[str, Any] = {}

    load_from_fileiter(
        glob.glob(
            "{config_dir}{sep}**{sep}{filename}".format(
                config_dir=config_dir,
                sep=os.sep,
                filename=constants.FILENAME_TEMPLATE.format(
                    specifier=constants.OVERRIDE
                ),
            ),
            recursive=True,
        ),
        deduped_filepaths,
    )
    load_from_fileiter(
        glob.glob(
            "{config_dir}{sep}**{sep}{filename}".format(
                config_dir=config_dir,
                sep=os.sep,
                filename=constants.FILENAME_TEMPLATE.format(specifier=env.name),
            ),
            recursive=True,
        ),
        deduped_filepaths,
    )
    load_from_fileiter(
        glob.glob(
            "{config_dir}{sep}**{sep}{filename}".format(
                config_dir=config_dir,
                sep=os.sep,
                filename=constants.BASE_FILENAME,
            ),
            recursive=True,
        ),
        deduped_filepaths,
    )

    for filepath in sys.path:
        if not filepath:
            # skip root
            continue

        load_from_fileiter(
            glob.glob(
                "{path}{sep}**{sep}{filename}".format(
                    path=filepath,
                    sep=os.sep,
                    filename=constants.FILENAME_TEMPLATE.format(specifier=env.name),
                ),
                recursive=True,
            ),
            deduped_filepaths,
        )
        load_from_fileiter(
            glob.glob(
                "{path}{sep}**{sep}{filename}".format(
                    path=filepath,
                    sep=os.sep,
                    filename=constants.FILENAME_TEMPLATE.format(
                        specifier=constants.BASE_FILENAME
                    ),
                ),
                recursive=True,
            ),
            deduped_filepaths,
        )

    base = kwargs
    for source in deduped_filepaths:
        with open(source, "r", encoding="UTF-8") as jfile:
            data = json.load(jfile)

        fallback(base, data)

    return configtree.ConfigTree.from_dict(env=env, conf=base)
