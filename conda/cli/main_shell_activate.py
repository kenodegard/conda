# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""CLI implementation for `conda init`.

Prepares the user's profile for running conda, and sets up the conda shell interface.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from ..deprecations import deprecated

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction
    from typing import Any

log = getLogger(__name__)


def configure_parser(
    sub_parsers: _SubParsersAction,
    *,
    plus_json: bool,
    **kwargs,
) -> ArgumentParser:
    from ..common.constants import NULL

    p = sub_parsers.add_parser("activate")

    defaults: dict[str, Any] = {}
    if plus_json:
        defaults["json"] = True
        defaults["func"] = "conda.cli.main_shell_activate.execute_plus_json"
    else:
        p.add_argument(
            "--json",
            action="store_true",
            default=NULL,
            help="Report all output as json. Suitable for using conda programmatically.",
        )
        defaults["func"] = "conda.cli.main_shell_activate.execute"

    stacking = p.add_mutually_exclusive_group()
    stacking.add_argument("--stack", dest="stack", action="store_true", default=NULL)
    stacking.add_argument(
        "--no-stack", dest="stack", action="store_false", default=NULL
    )

    p.add_argument("env_name_or_prefix", action="store")

    p.set_defaults(**defaults)

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    from ..activate import get_json_formatter
    from ..base.context import context
    from ..common.constants import NULL

    if context.json:
        activator = get_json_formatter(args.activator)()
    else:
        activator = args.activator()

    if args.stack is not NULL:
        activator.stack = args.stack
    else:
        activator.stack = context.auto_stack and context.shlvl <= context.auto_stack

    activator.env_name_or_prefix = args.env_name_or_prefix

    print(activator.activate(), end="")
    return 0


@deprecated(
    "25.3", "25.9", addendum="Use `conda shell.SHELL activate ENV --json` instead."
)
def execute_plus_json(args: Namespace, parser: ArgumentParser) -> int:
    return execute(args, parser)
