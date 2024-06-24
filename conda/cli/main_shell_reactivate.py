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
    p = sub_parsers.add_parser("reactivate")

    defaults = {}
    if json_arg:
        p.add_argument("--json", action="store_true")
    else:
        defaults["json"] = True

    p.set_defaults(func="conda.cli.main_shell_reactivate.execute", **defaults)

    return p


def execute(args: Namespace, parser: ArgumentParser) -> int:
    print("...reactivate")
    print(args)
    return 0
