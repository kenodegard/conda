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


def configure_parser(
    sub_parsers: _SubParsersAction, *, json_arg: bool, **kwargs
) -> ArgumentParser:
    p = sub_parsers.add_parser("activate")

    defaults = {}
    if json_arg:
        p.add_argument("--json", action="store_true")
    else:
        defaults["json"] = True

    stacking = p.add_mutually_exclusive_group()
    stacking.add_argument("--stack", dest="stack", action="store_true")
    stacking.add_argument("--no-stack", dest="stack", action="store_false")

    p.set_defaults(func="conda.cli.main_shell_activate.execute", **defaults)

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    print("...activate")
    print(args)
    return 0
