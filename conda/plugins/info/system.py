# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from conda import CONDA_PACKAGE_ROOT
from conda.common.compat import find_commands, find_executable
from conda.common.path import get_user_site
from conda.plugins.hookspec import hookimpl
from conda.plugins.types import CondaInfoComponent

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any


PRETTY_NAME_MAP = {
    "site_dirs": "user site dirs",
    "conda_location": "conda location",
    "conda_build_version": "conda-build version",
}


def get_system_info() -> Iterable[str, Any]:
    yield "sys.version", sys.version
    yield "sys.prefix", sys.prefix
    yield "sys.executable", sys.executable
    yield "conda location", CONDA_PACKAGE_ROOT

    for cmd in sorted(set(find_commands() + ("build",))):
        yield f"conda-{cmd}", find_executable(f"conda-{cmd}")

    yield "site_dirs", get_user_site()

    yield "env_vars", get_env_vars()


def get_env_vars() -> dict[str, str]:
    env_var_keys = {
        "CIO_TEST",
        "CURL_CA_BUNDLE",
        "REQUESTS_CA_BUNDLE",
        "SSL_CERT_FILE",
        "LD_PRELOAD",
    }

    # add all relevant env vars, e.g. startswith('CONDA') or endswith('PATH')
    env_var_keys.update(v for v in os.environ if v.upper().startswith("CONDA"))
    env_var_keys.update(v for v in os.environ if v.upper().startswith("PYTHON"))
    env_var_keys.update(v for v in os.environ if v.upper().endswith("PATH"))
    env_var_keys.update(v for v in os.environ if v.upper().startswith("SUDO"))

    env_vars = {
        ev: os.getenv(ev, os.getenv(ev.lower(), "<not set>")) for ev in env_var_keys
    }

    proxy_keys = (v for v in os.environ if v.upper().endswith("PROXY"))
    env_vars.update({ev: "<set>" for ev in proxy_keys})

    return env_vars


@hookimpl
def conda_info_components() -> Iterable[CondaInfoComponent]:
    yield CondaInfoComponent(
        name="system",
        print=lambda context: get_system_info(),
        json=lambda context: {"system": get_system_info()},
    )
