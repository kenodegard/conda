# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins.hookspec import hookimpl
from conda.plugins.types import CondaInfoComponent

from ...core.envs_manager import list_all_known_prefixes

if TYPE_CHECKING:
    from collections.abc import Iterable


@hookimpl
def conda_info_components() -> Iterable[CondaInfoComponent]:
    yield CondaInfoComponent(
        name="envs",
        print=lambda context: "\n".join(list_all_known_prefixes()),
        json=lambda context: {"envs": list_all_known_prefixes()},
    )
