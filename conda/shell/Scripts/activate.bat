:: Copyright (C) 2012 Anaconda, Inc
:: SPDX-License-Identifier: BSD-3-Clause
:: Test first character and last character of %1 to see if first character is a "
::   but the last character isn't.
:: This was a bug as described in https://github.com/ContinuumIO/menuinst/issues/60
:: When Anaconda Prompt has the form
::   %windir%\system32\cmd.exe "/K" "C:\Users\builder\Miniconda3\Scripts\activate.bat" "C:\Users\builder\Miniconda3"
:: Rather than the correct
::    %windir%\system32\cmd.exe /K ""C:\Users\builder\Miniconda3\Scripts\activate.bat" "C:\Users\builder\Miniconda3""
:: this solution taken from https://stackoverflow.com/a/31359867
@SET "_ARG=%1"
@SET _FIRST=%_ARG:~0,1%
@SET _LAST=%_ARG:~-1%
@SET _FIRST=%_FIRST:"=+%
@SET _LAST=%_LAST:"=+%
@SET _ARG=

@IF [%_FIRST%]==[+] @IF NOT [%_LAST%]==[+] @(
    @CALL "%~dp0..\condabin\conda.bat" activate
    @GOTO :CLEANUP
)

:: This may work if there are spaces in anything in %*
@CALL "%~dp0..\condabin\conda.bat" activate %*

:CLEANUP
@SET _FIRST=
@SET _LAST=
