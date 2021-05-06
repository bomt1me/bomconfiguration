"""Opinionated python configuration"""


from __future__ import annotations

from typing import Optional, Dict, Any, List

import logging
import os


_logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


ENVIRONMENTS = {"dev", "integration", "prod"}
SECRET_KEYS = {"password", "private"}


def get_env(environment: Optional[str] = None) -> str:
    """get_env

    This function is used to verify and retrieve an Environment. If no environment provided,
    the `ENV` environment variable is retrieved. To use this configuration, you must provided a valid
    environment.

    Arguments:
        environment (Optional[str]): Environment to verify if provided

    Returns:
        (str): Environment name
    """

    if isinstance(environment, str) and environment in ENVIRONMENTS:
        return environment

    config_var = os.getenv("ENV")

    if isinstance(config_var, str) and config_var in ENVIRONMENTS:
        return config_var

    raise ValueError(
        "You must define an environment. Please pass a valid environment or use the environment variable `ENV`."
    )


class ConfigMixin:
    """ConfigMixin

    Config specific helper methods.
    """

    config: Dict[str, Any]

    def get(self, key: str) -> Any:
        """get

        Get a key in the configuration. If not present, this will raise IndexError.

        Arguments:
            key (str): Key to search

        Returns:
            (Any): Value associated with key
        """

        return self.config[key]

    def get_or_default(self, key: str, default: Any) -> Any:
        """get_or_default

        Get a key in the configuration. If not present, this will return `default`.

        Arguments:
            key (str): Key to search
            default (Any): Default value to supply if key not present

        Returns:
            (Any): Value associated with key
        """

        return self.config.get(key, default)


class Config(ConfigMixin):
    """Config

    Config class for registering configurations. When you initialize this class, the config will be
    registered. Configs are stored in `_registry`.
    """

    _registry: List[Dict[str, Any]] = []

    @classmethod
    def from_dict(cls, config: Optional[Dict[str, Any]] = None) -> Config:
        """from_dict

        Class method Create config from dictionary.

        Arguments:
            config (Optional[Dict[str, Any]]): Dictionary used to initialize config.

        Returns:
            (cls): Returns a `Config` object
        """

        if config is None:
            config = {}
        return cls(config)

    @classmethod
    def get_registry(cls) -> List[Dict[str, Any]]:
        """get_registry

        Public method for obtaining all registered configurations.

        Returns:
            (List[Dict[str, Any]]): List of configurations
        """

        return cls._registry

    def __init__(self, config: Dict[str, Any]) -> None:
        """__init__

        Arguments:
            config (Dict[str, Any]): Specs for this configuration
        """

        self._registry.append(config)
        self.config = config


class AppConfig(ConfigMixin):
    """AppConfig

    Configuration object to use at the highest level (or application level).
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """__init__

        Arguments:
            config (Dict[str, Any]): Specs for configuration
        """

        self.config = config
        env = get_env(config.get("ENV", None))
        self.config["env"] = env

    @property
    def name(self) -> Optional[str]:
        """app_name

        Get the application name for this configuration.

        Returns:
            (Optional[str]): String name of application
        """

        return self.config.get("app_name")

    @property
    def version(self) -> Optional[str]:
        """app_version

        Get the application version for this configuration.

        Returns:
            (Optional[str]): String version (semantic) of application
        """

        return self.config.get("app_version")

    @property
    def env(self) -> str:
        """env

        Get the application environment for this configuration. If the environment is not set,
        an Exception will be raised.

        Returns:
            (str): Environment as a string
        """

        env = self.config.get("env")
        return get_env(env)


def load(
    app_config: Optional[Dict[str, Any]] = None,
) -> AppConfig:
    """load

    Entry point for loading a configuration. The `app_config` has
    higher precendence than the other configurations, so it will be placed on top of the
    other configurations. Only flat configurations are supported right now.

    Arguments:
        app_config (Optional[Dict[str, Any]]): Application configuration to apply

    Returns:
        (AppConfig): Application configuration object
    """

    if app_config is None:
        app_config = {}

    Config(app_config)

    config: Dict[str, Any] = {}
    registry = Config.get_registry()
    if registry and any(registry):
        for child in registry:
            config.update(**child)

    return AppConfig(config)


class ConfigDumper:
    """ConfigDumper

    Helper class for dumping configurations.
    """

    @classmethod
    def sanitize(cls, config: AppConfig) -> Dict[str, Any]:
        """sanitize

        Arguments:
            config (AppConfig): Config to sanitize

        Returns:
            clean (Dict[str, Any]): Sanitized configuration
        """

        clean = {}
        for key, value in config.config.items():
            if key in SECRET_KEYS:
                clean[key] = "..."
            elif isinstance(value, dict):
                clean[key] = "..."
            else:
                clean[key] = value
        return clean
