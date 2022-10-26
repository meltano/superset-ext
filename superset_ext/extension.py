"""Meltano Superset extension."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

from superset_ext.utils import load_config_from_env, write_config

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
        default_db_path = ".meltano/utilities/superset/superset.db"
        self.env_config.get(
            "SQLALCHEMY_DATABASE_URI",
            f"sqlite:///{os.environ.get('MELTANO_PROJECT_ROOT')}/{default_db_path}",
        )
        self.superset_config = {
            k: v
            for (k, v) in self.env_config.items()
            if not k.upper().startswith("EXT_")
        }
        self.superset_invoker = Invoker(self.superset_bin, env=self.env_config)

    def _write_config(self, force: bool = False) -> bool:
        config_path = Path(
            self.env_config.get(
                "SUPERSET_CONFIG_PATH", "analyze/superset/superset_config.py"
            )
        ).resolve()
        return write_config(log, config_path, self.superset_config, force=force)

    def initialize(self, force: bool = False) -> None:
        """Initialize the superset extension.

        This will create the superset config file if it doesn't exist,
        and initialize the database and superset app.

        Args:
            force: Whether to force initialization - rewrite the config file.
        """
        if self._write_config(force=force):
            db_uri = urlparse(self.env_config.get("SQLALCHEMY_DATABASE_URI")).path
            os.makedirs(os.path.dirname(db_uri), exist_ok=True)
            try:
                log.info("Performing 'superset db upgrade'")
                self.superset_invoker.run("db", "upgrade", stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as err:
                log_subprocess_error(
                    "Superset db upgrade", err, "Superset initialization failed"
                )
                sys.exit(err.returncode)

            try:
                log.info("Performing 'superset init'")
                self.superset_invoker.run("init", stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as err:
                log_subprocess_error(
                    "Superset init", err, "Superset initialization failed"
                )
                sys.exit(err.returncode)

            try:
                log.info("Performing 'superset fab create-permissions'")
                self.superset_invoker.run(
                    "fab", "create-permissions", stdout=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as err:
                log_subprocess_error(
                    "Superset fab create-permissions",
                    err,
                    "Superset initialization failed",
                )
                sys.exit(err.returncode)

            log.info("Superset initialized, don't forget to configure an admin user!")
        else:
            log.info(
                "Superset already initialized, skipping. Rerun with --force to rewrite config."  # noqa: E501
            )

    def create_admin(
        self, username: str, first_name: str, last_name: str, email: str, password: str
    ) -> None:
        """Invoke the underlying superset cli and create an admin user.

        Args:
            username: The username of the admin user.
            first_name: The first name of the admin user.
            last_name: The last name of the admin user.
            email: The email of the admin user.
            password: The password of the admin user.
        """
        try:
            self.superset_invoker.run_and_log(
                None,
                [
                    "fab",
                    "create-admin",
                    f"--username={username}",
                    f"--firstname={first_name}",
                    f"--lastname={last_name}",
                    f"--email={email}",
                    f"--password={password}",
                ],
            )
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"superset add_user {username}", err, "Superset create-admin failed"
            )
            sys.exit(err.returncode)

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
                    name="superset_extension",
                    description="extension commands",
                    commands=[
                        "describe",
                        "invoke",
                        "pre_invoke",
                        "post_invoke",
                        "initialize",
                        "create-admin",
                    ],
                ),
                models.InvokerCommand(
                    name="superset_invoker", description="pass through invoker"
                ),
            ]
        )
