from typing import Any, Dict, List

import pytest

from bom.configuration import configtree


@pytest.mark.parametrize(
    "key,expected",
    [
        ("hello", ["hello"]),
        ("hello.there", ["hello", "there"]),
        (".there", ["", "there"]),
        (".there.", ["", "there", ""]),
        (".'foo.bar\".bye.", ["", "'foo", 'bar"', "bye", ""]),
        ("", [""]),
        ("..", ["", "", ""]),
        ("foo'bar", ["foo'bar"]),
        ('host."1.0.0.1".name', ["host", "1.0.0.1", "name"]),
    ],
)
def test_parse_key(key: str, expected: List[str]) -> None:
    assert expected == configtree.parse_key(key)


@pytest.mark.parametrize(
    "key",
    [
        (None,),
        (True,),
        (4,),
    ],
)
def test_parse_key_raises_key_error(key: Any) -> None:
    with pytest.raises(KeyError):
        configtree.parse_key(key)


def test_configtree_from_dict() -> None:
    env = "dev"
    base_conf = {
        "version": "0.1.0",
        "database": {
            "pass.word": "password",
            "user": "user",
            "ports": {
                "value": "5432",
                "other": ["1", "2", "3"],
            },
        },
        "logging": {
            "host": "example.com",
            "port": "8000",
        },
    }
    conf = configtree.ConfigTree.from_dict(env=env, conf=base_conf)
    assert '"pass.word"' in conf.to_dict()["database"]


def test_env() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={})
    assert conf.env.name == env


@pytest.mark.parametrize(
    "key,value,default,expected",
    [
        ("foo", "foo", "bar", "bar"),
    ],
)
def test_get(key: str, value: str, default: str, expected: str) -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": value})
    assert expected == conf.get(key, default=default)


def test_get_string() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": 1234})
    assert "1234" == conf.get_string("base")


def test_get_integer() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": "1234"})
    assert 1234 == conf.get_integer("base")


def test_get_float() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": "1234"})
    assert 1234.0 == conf.get_float("base")


def test_get_bool() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": "1234"})
    assert conf.get_bool("base")


def test_nested_get() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(env=env, conf={"base": {"nested": "1234"}})
    assert "1234" == conf.get("base.nested")


@pytest.mark.parametrize(
    "key,conf",
    [
        ("hello.there", {"here": {"foo": "1234"}}),
        ("hello", {"bye": "1234"}),
    ],
)
def test_key_not_found(key: str, conf: Dict[str, Any]) -> None:
    with pytest.raises(KeyError):
        env = "dev"
        conftree = configtree.ConfigTree.from_dict(env=env, conf=conf)
        conftree.get(key)


def test_to_dict() -> None:
    env = "dev"
    conf = configtree.ConfigTree.from_dict(
        env=env, conf={"base": {"nested": {"nested": {"nested": "1234"}}}}
    )
    val = conf.get("base")
    if not val:
        assert 0

    assert "1234" == val.to_dict()["nested"]["nested"]["nested"]
