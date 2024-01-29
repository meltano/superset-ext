"""Utilities that will probably graduate to be part of the meltano extension sdk."""

from __future__ import annotations

import os
from pathlib import Path

import structlog


def trim_prefix(prefix: str, key: str) -> str:
    """Return a key without the given prefix.

    Args:
        prefix: The prefix to remove from the key.
        key: The key to check, and trim if needed.

    Returns:
        The cleaned key.
    """
    if key.startswith(prefix):
        return key[len(prefix) :]  # noqa: E203 - conflicts with black
    return key


def load_config_from_env(prefix: str, trimmed: bool = False) -> dict:
    """Return a dict of config options for a given prefix.

    Args:
        prefix: The prefix to use to filter the environment variables.
        trimmed: Whether to trim the prefix from the key.

    Returns:
        A dict of config options.
    """
    if trimmed:
        return {
            trim_prefix(prefix, key): value
            for key, value in os.environ.items()
            if key.startswith(prefix.upper())
        }
    return {
        key: value
        for key, value in os.environ.items()
        if key.startswith(prefix.upper())
    }


def prepared_env(prefix: str) -> dict[str, str]:
    """Prepare the environment for running superset.

    Args:
        prefix: The prefix to use when loading environment variables.

    Returns:
        Dict version of the prepared environment.
    """
    env_config = load_config_from_env(prefix, trimmed=True)
    env_config["PATH"] = os.environ.get("PATH", "")

    if not env_config.get("FLASK_APP"):
        env_config["FLASK_APP"] = "superset"

    default_home = (
        f"{os.environ.get('MELTANO_PROJECT_ROOT')}/.meltano/utilities/superset"
    )
    default_analyze_dir = f"{os.environ.get('MELTANO_PROJECT_ROOT')}/analyze/superset"

    # superset_home and superset_config_path are a special case
    # we need to preserve the superset prefix as its part of the config key
    env_config["SUPERSET_HOME"] = env_config.get("HOME", default_home)
    try:
        del env_config["HOME"]
    except KeyError:
        pass

    env_config["SUPERSET_CONFIG_PATH"] = env_config.get(
        "CONFIG_PATH", f"{default_analyze_dir}/superset_config.py"
    )
    try:
        del env_config["CONFIG_PATH"]
    except KeyError:
        pass

    if not env_config.get("SQLALCHEMY_DATABASE_URI"):
        env_config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{default_home}/superset.db"

    return env_config


def write_config(
    log: structlog.BoundLogger,
    config_path: Path,
    superset_config: dict,
    force: bool = False,
) -> bool:
    """Write a superset config file that initializes using the provided config dict.

    Args:
        log: The logger to use.
        config_path: The path to the config file.
        superset_config: The config dict to use.
        force: Whether to overwrite an existing config file.

    Returns:
        Whether a config file was written.
    """
    if config_path.exists() and not force:
        log.info(
            "Superset config already exists",
            config_path=config_path,
        )
        return False
    os.makedirs(config_path.parent, exist_ok=True)
    config_script_lines = [
        "import sys",
        "module = sys.modules[__name__]",
        f"config = {superset_config!r}",
        "for key, value in config.items():",
        "    if key.isupper():",
        "        setattr(module, key, value)",
        "",
        "# add any additional config here #",
        "",
    ]
    log.info(
        "Writing superset config",
        config_path=config_path,
    )
    with open(config_path, "w") as config_file:
        config_file.write("\n".join(config_script_lines))
    return True
