# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from typing import TYPE_CHECKING

from conda.plugins.hookspec import hookimpl
from conda.plugins.types import CondaInfoComponent

from . import conda_build

if TYPE_CHECKING:
    from collections.abc import Iterable


@hookimpl
def conda_info_components() -> Iterable[CondaInfoComponent]:
    yield CondaInfoComponent(
        name="conda_build_version",
        print=lambda context: conda_build.get_conda_build_version(),
        json=lambda context: {
            "conda_build_version": conda_build.get_conda_build_version()
        },
    )
