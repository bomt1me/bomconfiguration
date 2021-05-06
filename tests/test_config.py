import os
import unittest.mock

import pytest

import bom.configuration as config


class TestGetEnv:
    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_none_and_no_env_then_error() -> None:
        with pytest.raises(ValueError):
            config.get_env()

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_str_and_no_env_then_good() -> None:
        env = "dev"
        assert env == config.get_env("dev")

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "integration"}, clear=True)
    def test_given_str_and_env_then_str() -> None:
        env = "dev"
        assert env == config.get_env("dev")

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "dev"}, clear=True)
    def test_given_none_and_env_then_env() -> None:
        assert config.get_env() == "dev"


class TestConfig:
    @classmethod
    def teardown_class(cls) -> None:
        config.Config._registry.clear()

    @staticmethod
    def setup_method() -> None:
        config.Config._registry.clear()

    @staticmethod
    def test_given_none_when_from_dict_then_empty_config() -> None:
        assert {} == config.Config.from_dict(None).get_registry()[0]
        assert len(config.Config.get_registry()) == 1

    @staticmethod
    def test_given_specs_when_from_dict_then_spec_in_config() -> None:
        specs = {"foo": "bar"}
        config.Config.from_dict(specs)
        assert specs == config.Config.get_registry()[0]
        assert len(config.Config.get_registry()) == 1

    @staticmethod
    def test_given_config_without_key_when_get_with_default_then_default_is_obtained() -> None:
        conf = config.Config.from_dict(None)
        assert conf.get_or_default("hello", 1234) == 1234

    @staticmethod
    def test_given_config_with_key_when_get_with_default_then_value_is_obtained() -> None:
        conf = config.Config.from_dict({"hello": -1234})
        assert -1234 == conf.get_or_default("hello", 1234)


class TestLoad:
    @classmethod
    def teardown_class(cls) -> None:
        config.Config._registry.clear()

    @staticmethod
    def setup_method() -> None:
        config.Config._registry.clear()

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "dev"}, clear=True)
    def test_given_two_configs_when_load_then_override_works() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load()
        assert b_conf["password"] == app.get("password")

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "dev"}, clear=True)
    def test_given_two_configs_when_load_with_app_config_then_override_works() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        c_conf = {"password": "app_password"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert c_conf["password"] == app.get("password")

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_no_configs_when_load_then_error() -> None:
        with pytest.raises(ValueError):
            config.load()


class TestConfigDumper:
    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "dev"}, clear=True)
    def test_given_configs_and_password_when_dump_then_password_hidden() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        c_conf = {"password": "app_password"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert config.ConfigDumper.sanitize(app)["password"] == "..."

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {"ENV": "dev"}, clear=True)
    def test_given_configs_with_nested_dict_and_password_when_dump_then_nested_is_hidden() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": {"value": 5432}, "password": "override"}
        c_conf = {"password": "app_password"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert config.ConfigDumper.sanitize(app)["port"] == "..."


class TestAppConfig:
    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_two_configs_with_env_and_no_env_var_when_load_with_app_config_then_env_found() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        c_conf = {"password": "app_password", "ENV": "dev"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert app.env == "dev"

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_two_configs_when_load_with_app_name_then_app_name() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        c_conf = {"password": "app_password", "ENV": "dev", "app_name": "cool app"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert app.name == "cool app"

    @staticmethod
    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_given_two_configs_when_load_with_app_version_then_app_version() -> None:
        a_conf = {"host": "localhost", "password": "password"}
        b_conf = {"port": 5432, "password": "override"}
        c_conf = {"password": "app_password", "ENV": "dev", "app_name": "cool app", "app_version": "1.0.0"}
        config.Config(a_conf)
        config.Config(b_conf)
        app = config.load(c_conf)
        assert app.version == "1.0.0"
