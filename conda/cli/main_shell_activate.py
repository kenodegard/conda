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
    sub_parsers: _SubParsersAction,
    *,
    plus_json: bool,
    **kwargs,
) -> ArgumentParser:
    from ..common.constants import NULL

    p = sub_parsers.add_parser("activate")

    defaults = {}
    if plus_json:
        defaults["json"] = True
    else:
        p.add_argument(
            "--json",
            action="store_true",
            default=NULL,
            help="Report all output as json. Suitable for using conda programmatically.",
        )

    stacking = p.add_mutually_exclusive_group()
    stacking.add_argument("--stack", dest="stack", action="store_true", default=NULL)
    stacking.add_argument(
        "--no-stack", dest="stack", action="store_false", default=NULL
    )

    p.add_argument("env_name_or_prefix", action="store")

    p.set_defaults(func="conda.cli.main_shell_activate.execute", **defaults)

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    from ..base.context import context
    from ..common.constants import NULL

    activator = args.activator()

    activator.json = context.json
    if args.stack is not NULL:
        activator.stack = args.stack
    else:
        activator.stack = context.auto_stack and context.shlvl <= context.auto_stack

    activator.env_name_or_prefix = args.env_name_or_prefix

    print(activator.activate(), end="")
    return 0
