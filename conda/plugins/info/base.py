# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from conda.plugins.hookspec import hookimpl
from conda.plugins.types import CondaInfoComponent

if TYPE_CHECKING:
    from typing import Any

    from conda.base.context import Context


def print_base_info(context: Context) -> str:
    return str(context.root_prefix)


def json_base_info(context: Context) -> dict[str, Any]:
    return {"base": str(context.root_prefix)}


@hookimpl
def conda_info_components() -> Iterable[CondaInfoComponent]:
    yield CondaInfoComponent(
        name="base",
        print=print_base_info,
        json=json_base_info,
    )
