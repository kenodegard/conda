# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Powershell activator implementation."""

import sys
from pathlib import Path
from textwrap import dedent

from ... import CONDA_PACKAGE_ROOT, CONDA_SOURCE_ROOT
from ...activate import _Activator, path_identity
from ...base.constants import on_win
from ...base.context import context
from .. import CondaShell, hookimpl


class PowerShellActivator(_Activator):
    pathsep_join = ";".join if on_win else ":".join
    sep = "\\" if on_win else "/"
    path_conversion = staticmethod(path_identity)
    script_extension = ".ps1"
    tempfile_extension = None  # output to stdout
    command_join = "\n"

    unset_var_tmpl = '$Env:%s = ""'
    export_var_tmpl = '$Env:%s = "%s"'
    set_var_tmpl = '$Env:%s = "%s"'
    run_script_tmpl = '. "%s"'

    hook_source_path = Path(
        CONDA_PACKAGE_ROOT,
        "shell",
        "condabin",
        "conda-hook.ps1",
    )

    def _hook_preamble(self) -> str:
        if context.dev:
            return dedent(
                f"""
                $Env:PYTHONPATH = "{CONDA_SOURCE_ROOT}"
                $Env:CONDA_EXE = "{sys.executable}"
                $Env:_CE_M = "-m"
                $Env:_CE_CONDA = "conda"
                $Env:_CONDA_ROOT = "{CONDA_PACKAGE_ROOT}"
                $Env:_CONDA_EXE = "{context.conda_exe}"
                $CondaModuleArgs = @{{ChangePs1 = ${context.changeps1}}}
                """
            ).strip()
        else:
            return dedent(
                f"""
                $Env:CONDA_EXE = "{context.conda_exe}"
                $Env:_CE_M = ""
                $Env:_CE_CONDA = ""
                $Env:_CONDA_ROOT = "{context.conda_prefix}"
                $Env:_CONDA_EXE = "{context.conda_exe}"
                $CondaModuleArgs = @{{ChangePs1 = ${context.changeps1}}}
                """
            ).strip()

    def _hook_postamble(self) -> str:
        return "Remove-Variable CondaModuleArgs"


@hookimpl
def conda_shells():
    yield CondaShell(
        name="powershell",
        activator=PowerShellActivator,
    )
