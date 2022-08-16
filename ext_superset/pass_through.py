import sys

import structlog

from ext_superset.wrapper import Superset
from meltano_extension_sdk.logging import pass_through_logging_config


def pass_through_cli():
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = Superset()
    ext.pass_through_invoker(
        structlog.getLogger("superset_invoker"), *sys.argv[1:] if len(sys.argv) > 1 else []
    )
