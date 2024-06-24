# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Fish activator implementation."""

import sys
from pathlib import Path
from textwrap import dedent

from ... import CONDA_PACKAGE_ROOT
from ...activate import _Activator, native_path_to_unix
from ...base.constants import on_win
from ...base.context import context
from .. import CondaShell, hookimpl


class FishActivator(_Activator):
    pathsep_join = '" "'.join
    sep = "/"
    path_conversion = staticmethod(native_path_to_unix)
    script_extension = ".fish"
    tempfile_extension = None  # output to stdout
    command_join = ";\n"

    unset_var_tmpl = "set -e %s"
    export_var_tmpl = 'set -gx %s "%s"'
    set_var_tmpl = 'set -g %s "%s"'
    run_script_tmpl = 'source "%s"'

    hook_source_path = Path(
        CONDA_PACKAGE_ROOT,
        "shell",
        "etc",
        "fish",
        "conf.d",
        "conda.fish",
    )

    def _hook_preamble(self) -> str:
        if on_win:
            return dedent(
                f"""
                set -gx CONDA_EXE (cygpath "{context.conda_exe}")
                set _CONDA_ROOT (cygpath "{context.conda_prefix}")
                set _CONDA_EXE (cygpath "{context.conda_exe}")
                set -gx CONDA_PYTHON_EXE (cygpath "{sys.executable}")
                """
            ).strip()
        else:
            return dedent(
                f"""
                set -gx CONDA_EXE "{context.conda_exe}"
                set _CONDA_ROOT "{context.conda_prefix}"
                set _CONDA_EXE "{context.conda_exe}"
                set -gx CONDA_PYTHON_EXE "{sys.executable}"
                """
            ).strip()


@hookimpl
def conda_shells():
    yield CondaShell(
        name="fish",
        activator=FishActivator,
    )
