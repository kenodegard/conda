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

    p = sub_parsers.add_parser("deactivate")

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

    p.set_defaults(func="conda.cli.main_shell_deactivate.execute", **defaults)

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    from ..base.context import context

    activator = args.activator()

    activator.json = context.json

    print(activator.deactivate(), end="")
    return 0
