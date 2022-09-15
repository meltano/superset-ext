import os

from superset_ext.utils import load_config_from_env, trim_prefix


def test_trim_prefix() -> None:
    assert trim_prefix("foo_", "foo_bar") == "bar"
    assert trim_prefix("foo_", "bar") == "bar"


def test_load_config_from_env() -> None:
    os.environ["FOO_BAR"] = "bar"
    os.environ["FOO_BAZ"] = "baz"
    assert load_config_from_env("foo_", trimmed=True) == {"bar": "bar", "baz": "baz"}
    assert load_config_from_env("foo_") == {"FOO_BAR": "bar", "FOO_BAZ": "baz"}
