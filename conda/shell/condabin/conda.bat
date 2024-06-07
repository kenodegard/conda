:: Copyright (C) 2012 Anaconda, Inc
:: SPDX-License-Identifier: BSD-3-Clause

@IF NOT DEFINED _CE_CONDA @(
  @SET _CE_M=
  @SET "CONDA_EXE=%~dp0..\Scripts\conda.exe"
)
@IF [%1]==[activate]   "%~dp0_conda_activate" %*
@IF [%1]==[deactivate] "%~dp0_conda_activate" %*

@CALL "%CONDA_EXE%" %_CE_M% %_CE_CONDA% %* || @EXIT /B %ERRORLEVEL%

@IF [%1]==[install]   "%~dp0_conda_activate" reactivate
@IF [%1]==[update]    "%~dp0_conda_activate" reactivate
@IF [%1]==[upgrade]   "%~dp0_conda_activate" reactivate
@IF [%1]==[remove]    "%~dp0_conda_activate" reactivate
@IF [%1]==[uninstall] "%~dp0_conda_activate" reactivate

@EXIT /B %ERRORLEVEL%
