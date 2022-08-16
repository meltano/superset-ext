"""Random utilities that will probably graduate to be part of the
meltano extension sdk."""
from __future__ import annotations

import os


def trim_prefix(prefix: str, key: str) -> str:
    """Return a key without the given prefix.

    Args:
        prefix: The prefix to remove from the key.
        key: The key to check, and trim if needed.
    Returns:
        The cleaned key.
    """
    if key.startswith(prefix):
        return key[len(prefix) :]
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
