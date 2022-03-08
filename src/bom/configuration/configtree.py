from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from bom.configuration import constants, environment


def parse_key(key: str) -> List[str]:
    if not isinstance(key, str):
        raise KeyError("Invalid key. Please provide string.")

    if not key:
        return [""]

    path = []
    cur = ""
    index = 0
    while index < len(key):
        char = key[index]
        if char == constants.QUOTE_CHAR:
            try:
                next_index = key[index + 1 :].index(constants.QUOTE_CHAR) + index + 1
            except ValueError:
                cur += char
            else:
                cur = key[index + 1 : next_index]
                index = next_index
        elif char == constants.KEY_DELIMITER:
            path.append(cur)
            cur = ""
        else:
            cur += char

        index += 1

    path.append(cur)

    return path


class UndefinedKey:  # pylint: disable=too-few-public-methods
    pass


class ConfigTree:
    @classmethod
    def from_dict(
        cls,
        *,
        conf: Dict[str, Any],
        env: Optional[Union[str, environment.Environment]] = None,
    ) -> ConfigTree:
        keys_to_quote = []
        for key, value in conf.items():
            if constants.KEY_DELIMITER in key:
                keys_to_quote.append(key)

            if isinstance(value, dict):
                conf[key] = ConfigTree.from_dict(conf=value, env=env)

        for key in keys_to_quote:
            val = conf.pop(key)
            conf[constants.QUOTE_CHAR + key + constants.QUOTE_CHAR] = val

        return cls(conf, env)

    def __init__(
        self,
        conf: Dict[str, Any],
        env: Optional[Union[str, environment.Environment]] = None,
    ) -> None:
        self._config = conf
        self._env = env

        self.env  # pylint: disable=pointless-statement

    @property
    def env(self) -> environment.Environment:
        return environment.get_env(self._env)

    def get(
        self, key: str, *, default: Union[str, Type[UndefinedKey]] = UndefinedKey
    ) -> Optional[Any]:
        key_path = parse_key(key)

        conf = self._config.get(key_path[0], default)
        if len(key_path) > 1:
            if isinstance(conf, ConfigTree):
                conf = conf.get(
                    constants.KEY_DELIMITER.join(key_path[1:]),
                    default=default,
                )
            else:
                raise KeyError("Key not present in configuration.")

        if conf is UndefinedKey:
            raise KeyError("Key not present in configuration.")

        return conf

    def get_string(
        self, key: str, *, default: Union[str, Type[UndefinedKey]] = UndefinedKey
    ) -> Optional[str]:
        val = self.get(key=key, default=default)
        if val is None:
            return None

        return str(val)

    def get_integer(
        self, key: str, *, default: Union[str, Type[UndefinedKey]] = UndefinedKey
    ) -> Optional[int]:
        val = self.get(key=key, default=default)
        if val is None:
            return None

        return int(val)

    def get_float(
        self, key: str, *, default: Union[str, Type[UndefinedKey]] = UndefinedKey
    ) -> Optional[float]:
        val = self.get(key=key, default=default)
        if val is None:
            return None

        return float(val)

    def get_bool(
        self, key: str, *, default: Union[str, Type[UndefinedKey]] = UndefinedKey
    ) -> Optional[bool]:
        val = self.get(key=key, default=default)
        if val is None:
            return None

        return bool(val)

    def to_dict(self) -> Dict[str, Any]:
        conf = {}
        for key, value in self._config.items():
            if isinstance(value, ConfigTree):
                conf[key] = value.to_dict()
            else:
                conf[key] = value

        return conf
