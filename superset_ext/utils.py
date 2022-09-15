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
    with open(config_path, "w") as config_file:
        config_file.write("\n".join(config_script_lines))
    return True
