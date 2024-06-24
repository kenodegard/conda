# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""CLI implementation for `conda init`.

Prepares the user's profile for running conda, and sets up the conda shell interface.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction

log = getLogger(__name__)


def configure_parser(sub_parsers: _SubParsersAction, **kwargs) -> ArgumentParser:
    from ..base.context import context
    from . import (
        main_shell_activate,
        main_shell_commands,
        main_shell_deactivate,
        main_shell_hook,
        main_shell_reactivate,
    )

    for shell, plugin in context.plugin_manager.get_shells().items():
        p = sub_parsers.add_parser(
            f"zhell.{shell}",
            help="...",
            description="...",
            epilog="...",
            **kwargs,
        )

        shell_parsers = p.add_subparsers()

        # with --json support (defaults to json=False)
        main_shell_activate.configure_parser(shell_parsers, json_arg=True)
        main_shell_deactivate.configure_parser(shell_parsers, json_arg=True)
        main_shell_reactivate.configure_parser(shell_parsers, json_arg=True)
        main_shell_hook.configure_parser(shell_parsers)
        main_shell_commands.configure_parser(shell_parsers)

        p.set_defaults(
            func="conda.cli.main_shell.execute", shell=shell, activator=plugin.activator
        )

        # old school shell.posix+json
        old_p = sub_parsers.add_parser(
            f"zhell.{shell}+json",
            help="...",
            description="...",
            epilog="...",
            **kwargs,
        )

        old_parsers = old_p.add_subparsers()

        # without --json support (defaults to json=True)
        main_shell_activate.configure_parser(old_parsers, json_arg=False)
        main_shell_deactivate.configure_parser(old_parsers, json_arg=False)
        main_shell_reactivate.configure_parser(old_parsers, json_arg=False)
        main_shell_hook.configure_parser(old_parsers)
        main_shell_commands.configure_parser(old_parsers)

        old_p.set_defaults(
            func="conda.cli.main_shell.execute", shell=shell, activator=plugin.activator
        )

    return None


def execute(args: Namespace, parser: ArgumentParser) -> int:
    print("...")
    return 0
