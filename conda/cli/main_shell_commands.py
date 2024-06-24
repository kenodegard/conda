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
    p = sub_parsers.add_parser("commands")

    p.set_defaults(func="conda.cli.main_shell_commands.execute")

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    print("\n".join(get_commands()), end="")
    return 0


def get_commands() -> tuple[str, ...]:
    from .conda_argparse import find_builtin_commands, generate_parser
    from .find_commands import find_commands

    return tuple(
        sorted(find_builtin_commands(generate_parser()) + tuple(find_commands(True)))
    )
