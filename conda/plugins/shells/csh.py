# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Csh/Tcsh activator implementation."""

import os
import re
import sys
from pathlib import Path
from textwrap import dedent

from ... import CONDA_PACKAGE_ROOT
from ...activate import _Activator, native_path_to_unix
from ...base.constants import on_win
from ...base.context import context
from .. import CondaShell, hookimpl


class CshActivator(_Activator):
    pathsep_join = ":".join
    sep = "/"
    path_conversion = staticmethod(native_path_to_unix)
    script_extension = ".csh"
    tempfile_extension = None  # output to stdout
    command_join = ";\n"

    unset_var_tmpl = "unsetenv %s"
    export_var_tmpl = 'setenv %s "%s"'
    set_var_tmpl = "set %s='%s'"
    run_script_tmpl = 'source "%s"'

    hook_source_path = Path(
        CONDA_PACKAGE_ROOT,
        "shell",
        "etc",
        "profile.d",
        "conda.csh",
    )

    def _update_prompt(self, set_vars, conda_prompt_modifier):
        prompt = os.getenv("prompt", "")
        current_prompt_modifier = os.getenv("CONDA_PROMPT_MODIFIER")
        if current_prompt_modifier:
            prompt = re.sub(re.escape(current_prompt_modifier), r"", prompt)
        set_vars.update(
            {
                "prompt": conda_prompt_modifier + prompt,
            }
        )

    def _hook_preamble(self) -> str:
        if on_win:
            return dedent(
                f"""
                setenv CONDA_EXE `cygpath {context.conda_exe}`
                setenv _CONDA_ROOT `cygpath {context.conda_prefix}`
                setenv _CONDA_EXE `cygpath {context.conda_exe}`
                setenv CONDA_PYTHON_EXE `cygpath {sys.executable}`
                """
            ).strip()
        else:
            return dedent(
                f"""
                setenv CONDA_EXE "{context.conda_exe}"
                setenv _CONDA_ROOT "{context.conda_prefix}"
                setenv _CONDA_EXE "{context.conda_exe}"
                setenv CONDA_PYTHON_EXE "{sys.executable}"
                """
            ).strip()


@hookimpl
def conda_shells():
    yield CondaShell(
        name="csh",
        activator=CshActivator,
    )
    yield CondaShell(
        name="tcsh",
        activator=CshActivator,
    )
