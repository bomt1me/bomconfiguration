from typing import Any, Dict

import json
import os
import tempfile
import unittest.mock

import pytest

from bom.configuration import utils


@pytest.mark.parametrize(
    "high,low,expected",
    [
        (
            {"a": {"b": {"c": "d"}}},
            {"a": {"b": {"c": "e", "f": "g"}}},
            {"a": {"b": {"c": "d", "f": "g"}}},
        )
    ],
)
def test_fallback(
    high: Dict[str, Any], low: Dict[str, Any], expected: Dict[str, Any]
) -> None:
    utils.fallback(high, low)
    assert expected == high


@pytest.mark.parametrize(
    "env,value,expected",
    [
        ({}, "", ""),
        ({"HELLO": "foo"}, "HELLO", "HELLO"),
        ({"HELLO": "foo"}, "$HELLO", "foo"),
        ({"HELLO": "foo"}, "$$HELLO", "$$HELLO"),
        ({"HELLO": "foo"}, "${HELLO}", "foo"),
        ({"HELLO": ""}, "${HELLO-foo}", ""),
        ({}, "${HELLO-foo}", "foo"),
        ({"HELLO": ""}, "${HELLO:-foo}", "foo"),
        ({"HELLO": ""}, "${HELLO?foo}", ""),
        ({"HELLO": "bar"}, "${HELLO:?foo}", "bar"),
    ],
)
def test_interpolate_env_var(env: Dict[str, Any], value: str, expected: str) -> None:
    with unittest.mock.patch.dict(os.environ, env):
        assert expected == utils.interpolate_env_var(value)


@pytest.mark.parametrize(
    "env,value,err_msg",
    [
        ({}, "${HELLO?msg}", "msg."),
        ({"HELLO": ""}, "${HELLO:?msg}", "msg."),
    ],
)
def test_interpolate_env_var_raises_error(
    env: Dict[str, Any], value: str, err_msg: str
) -> None:
    with unittest.mock.patch.dict(os.environ, env):
        with pytest.raises(ValueError) as err:
            utils.interpolate_env_var(value)

    assert err.value.args[0].endswith(err_msg)


@pytest.mark.parametrize(
    "env,obj,expected",
    [
        (
            {"PASSWORD": "password"},
            {"name": "db", "password": "${PASSWORD}"},
            {"name": "db", "password": "password"},
        ),
        (
            {"PASSWORD": "password"},
            "hello",
            "hello",
        ),
    ],
)
def test_decoder_hook(
    env: Dict[str, Any], obj: Dict[str, Any], expected: Dict[str, Any]
) -> None:
    with unittest.mock.patch.dict(os.environ, env):
        assert expected == utils.decoder_hook(obj)


@pytest.mark.parametrize(
    "env,json_str,expected",
    [
        (
            {"PASSWORD": "password"},
            json.dumps(
                {
                    "database": {"name": "db", "password": "${PASSWORD}"},
                    "url": "https://localhost:8000/api",
                }
            ),
            {
                "database": {"name": "db", "password": "password"},
                "url": "https://localhost:8000/api",
            },
        ),
        (
            {"PASSWORD": "password"},
            '"hello"',
            "hello",
        ),
    ],
)
def test_customer_json_decoder(
    env: Dict[str, Any], json_str: str, expected: Dict[str, Any]
) -> None:
    with unittest.mock.patch.dict(os.environ, env):
        assert expected == json.loads(json_str, cls=utils.CustomJsonDecoder)


def test_load() -> None:
    expected_conf = {"a": "b"}

    with unittest.mock.patch.dict(os.environ, {"ENV": "dev"}):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(
                os.path.join(tmpdir, "bom.conf.json"), "w", encoding="UTF-8"
            ) as _file:
                _file.write(json.dumps(expected_conf))

            conf = utils.load(config_dir=tmpdir)

    assert expected_conf == conf.to_dict()
