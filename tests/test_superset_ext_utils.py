import os

import structlog

from superset_ext.utils import load_config_from_env, trim_prefix, write_config


def test_trim_prefix() -> None:
    assert trim_prefix("foo_", "foo_bar") == "bar"
    assert trim_prefix("foo_", "bar") == "bar"


def test_load_config_from_env() -> None:
    os.environ["FOO_BAR"] = "bar"
    os.environ["FOO_BAZ"] = "baz"
    assert load_config_from_env("FOO_", trimmed=True) == {"BAR": "bar", "BAZ": "baz"}
    assert load_config_from_env("FOO_") == {"FOO_BAR": "bar", "FOO_BAZ": "baz"}


def test_write_config(tmp_path) -> None:
    log = structlog.get_logger()
    config = {"foo": "bar", "baz": "qux"}
    config_path = tmp_path / "superset_config.py"
    assert write_config(log, config_path, config) is True
    assert config_path.exists() is True

    assert write_config(log, config_path, config, force=True) is True
    assert write_config(log, config_path, config) is False
