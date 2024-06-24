# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Xonsh activator implementation."""

from pathlib import Path

from ... import CONDA_PACKAGE_ROOT
from ...activate import _Activator, backslash_to_forwardslash, path_identity
from ...base.constants import on_win
from ...base.context import context
from .. import CondaShell, hookimpl


class XonshActivator(_Activator):
    pathsep_join = ";".join if on_win else ":".join
    sep = "/"
    path_conversion = staticmethod(
        backslash_to_forwardslash if on_win else path_identity
    )
    # 'scripts' really refer to de/activation scripts, not scripts in the language per se
    # xonsh can piggy-back activation scripts from other languages depending on the platform
    script_extension = ".bat" if on_win else ".sh"
    tempfile_extension = None  # output to stdout
    command_join = "\n"

    unset_var_tmpl = "del $%s"
    export_var_tmpl = "$%s = '%s'"
    # TODO: determine if different than export_var_tmpl
    set_var_tmpl = "$%s = '%s'"
    run_script_tmpl = (
        'source-cmd --suppress-skip-message "%s"'
        if on_win
        else 'source-bash --suppress-skip-message -n "%s"'
    )

    hook_source_path = Path(CONDA_PACKAGE_ROOT, "shell", "conda.xsh")

    def _hook_preamble(self) -> str:
        return f'$CONDA_EXE = "{self.path_conversion(context.conda_exe)}"'


@hookimpl
def conda_shells():
    yield CondaShell(
        name="xonsh",
        activator=XonshActivator,
    )
