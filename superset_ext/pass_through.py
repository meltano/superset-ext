"""Passthrough shim for Superset extension."""

import sys

import structlog
from meltano.edk.logging import pass_through_logging_config

from superset_ext.extension import Superset


def pass_through_cli() -> None:
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = Superset()
    ext.pass_through_invoker(
        structlog.getLogger("superset_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else []
    )
