# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Cmd.exe activator implementation."""

from ...activate import _Activator, path_identity
from .. import CondaShell, hookimpl


class CmdExeActivator(_Activator):
    pathsep_join = ";".join
    sep = "\\"
    path_conversion = staticmethod(path_identity)
    script_extension = ".bat"
    tempfile_extension = None  # output to stdout
    command_join = "\n"

    unset_var_tmpl = "@SET %s="
    export_var_tmpl = '@SET "%s=%s"'
    # TODO: determine if different than export_var_tmpl
    set_var_tmpl = '@SET "%s=%s"'
    run_script_tmpl = '@CALL "%s"'

    hook_source_path = None

    def _hook_preamble(self) -> None:
        # TODO: cmd.exe doesn't get a hook function? Or do we need to do something different?
        #       Like, for cmd.exe only, put a special directory containing only conda.bat on PATH?
        pass


@hookimpl
def conda_shells():
    yield CondaShell(
        name="cmd.exe",
        activator=CmdExeActivator,
    )
