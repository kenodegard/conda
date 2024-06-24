# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Register the built-in shells hook implementations."""

from . import cmd_exe, csh, fish, posix, powershell, xonsh

#: The list of shell plugins for easier registration with pluggy
plugins = [cmd_exe, csh, fish, posix, powershell, xonsh]
