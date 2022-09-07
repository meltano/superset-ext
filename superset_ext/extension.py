"""Meltano Superset extension."""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

from superset_ext.utils import load_config_from_env

log = structlog.get_logger("superset_extension")


class Superset(ExtensionBase):
    """Extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the extension."""
        self.superset_bin = "superset"  # verify this is the correct name
        self.env_prefix = "SUPERSET_"
        self.env_config = load_config_from_env(self.env_prefix, trimmed=True)
        self.env_config["PATH"] = os.environ.get("PATH", "")
        if not self.env_config.get("FLASK_APP"):
            self.env_config["FLASK_APP"] = "superset"
        self.superset_invoker = Invoker(self.superset_bin, env=os.environ.copy())

    def _write_config(self, force: bool = False) -> None:
        config_path = self.env_config["SUPERSET_CONFIG_PATH"]
        if os.path.exists(config_path) and not force:
            log.info(
                "superset config already exists, skipping initialization",
                config_path=config_path,
            )
            return
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        config_script_lines = [
            "import sys",
            "module = sys.modules[__name__]",
            f"config = {self.env_config!r}",
            "for key, value in config.items():",
            "    if key.isupper():",
            "        setattr(module, key, value)",
        ]
        with open(config_path, "w") as config_file:
            config_file.write("\n".join(config_script_lines))
        log.info("initialized superset config", config_path=config_path)

    def initialize(self, force: bool = False) -> None:
        """Initialize the superset extension.

        This will create the superset config file if it doesn't exist,
        and will run `superset db upgrade`.

        Args:
            force: Whether to force initialization - rewrite the config file.
        """
        self._write_config(force=force)
        self.superset_invoker.run("db", "upgrade")
        log.info("Superset initialized, don't forget to configure an admin user")

    def invoke(self, command_name: str | None, *command_args: Any) -> None:
        """Invoke the underlying cli, that is being wrapped by this extension.

        Args:
            command_name: The name of the command to invoke.
            command_args: The arguments to pass to the command.
        """
        try:
            self.superset_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"superset {command_name}", err, "Superset invocation failed"
            )
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        """Describe the extension.

        Returns:
            The extension description
        """
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="superset_extension", description="extension commands"
                ),
                models.InvokerCommand(
                    name="superset_invoker", description="pass through invoker"
                ),
            ]
        )
