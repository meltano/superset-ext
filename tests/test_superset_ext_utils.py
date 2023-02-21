import os
from unittest import mock

import structlog

from superset_ext.utils import (
    load_config_from_env,
    prepared_env,
    trim_prefix,
    write_config,
)


def test_trim_prefix() -> None:
    assert trim_prefix("foo_", "foo_bar") == "bar"
    assert trim_prefix("foo_", "bar") == "bar"


def test_load_config_from_env() -> None:
    os.environ["FOO_BAR"] = "bar"
    os.environ["FOO_BAZ"] = "baz"
    assert load_config_from_env("FOO_", trimmed=True) == {"BAR": "bar", "BAZ": "baz"}
    assert load_config_from_env("FOO_") == {"FOO_BAR": "bar", "FOO_BAZ": "baz"}


def test_parsed_env(monkeypatch) -> None:
    monkeypatch.setenv("SUPERSET_CONFIG", "tests/fixtures/superset_config.py")
    monkeypatch.setenv("SUPERSET_HOME", "tests/fixtures")
    monkeypatch.setenv("SUPERSET_CONFIG_PATH", "tests/fixtures/superset_config.py")
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///tests/fixtures/superset.db"
    )
    monkeypatch.setenv("CANARY", "canary")

    # patch load_config_from_env to return a test dict
    monkeypatch.setattr(
        "superset_ext.utils.load_config_from_env", lambda x, y: {"CANARY": "canary"}
    )

    with mock.patch(
        "superset_ext.utils.load_config_from_env"
    ) as mock_load_config_from_env:
        mock_load_config_from_env.return_value = {
            "CANARY": "canary",
            "HOME": "tests/fixtures",
            "CONFIG_PATH": "tests/fixtures/superset_config.py",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///tests/fixtures/superset.db",
            "MELTANO_PROJECT_ROOT": "tests/",
            "SECRET_KEY": "secret",
        }
        env = prepared_env("SUPERSET_")
        assert env["CANARY"] == "canary"
        assert env["SUPERSET_HOME"] == "tests/fixtures"
        assert env["SUPERSET_CONFIG_PATH"] == "tests/fixtures/superset_config.py"
        assert env["SQLALCHEMY_DATABASE_URI"] == "sqlite:///tests/fixtures/superset.db"
        assert env["MELTANO_PROJECT_ROOT"] == "tests/"
        assert env["SECRET_KEY"] == "secret"


def test_write_config(tmp_path) -> None:
    log = structlog.get_logger()
    config = {"foo": "bar", "baz": "qux"}
    config_path = tmp_path / "superset_config.py"
    assert write_config(log, config_path, config) is True
    assert config_path.exists() is True

    assert write_config(log, config_path, config, force=True) is True
    assert write_config(log, config_path, config) is False
