@echo off
setlocal DisableDelayedExpansion
pushd "%~dp0"
title Crimson Desert - Auronui Fix v0.4.1 - Stage 1 - Check Only
echo.
echo =============================================================
echo  CRIMSON DESERT - AURONUI FIX v0.4.1 BETA
echo  Stage 1 - Check Only
echo =============================================================
echo  Your input save will NOT be overwritten.
echo  BACK UP THE ENTIRE SAVE DIRECTORY before running modifications.
echo.
set "SAVE_PATH=%~1"
if not defined SAVE_PATH set /p "SAVE_PATH=Enter full path to a COPY of save.save: "
REM Windows Explorer's Copy as Path may insert surrounding quotation marks.
set "SAVE_PATH=%SAVE_PATH:"=%"
if not defined SAVE_PATH goto no_save
if not exist "%SAVE_PATH%" goto missing_save
if not exist "%~dp0auronui_reset.py" goto missing_script
where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if errorlevel 1 goto missing_python
set "PYTHON_CMD=python"
goto check_deps
:use_py
set "PYTHON_CMD=py -3"
:check_deps
%PYTHON_CMD% -c "import cryptography, lz4.block" >nul 2>nul
if errorlevel 1 goto missing_deps
echo Input: "%SAVE_PATH%"
echo.
%PYTHON_CMD% "%~dp0auronui_reset.py" "%SAVE_PATH%" --stage 1 --check
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo ERROR: Tool exited with code %RESULT%. No source file was overwritten.
goto finish
:no_save
echo ERROR: No save path provided.
set "RESULT=1"
goto finish
:missing_save
echo ERROR: Save not found: "%SAVE_PATH%"
set "RESULT=1"
goto finish
:missing_script
echo ERROR: Missing auronui_reset.py in this folder.
set "RESULT=1"
goto finish
:missing_python
echo ERROR: Python 3 is not installed or not available through py/python.
set "RESULT=1"
goto finish
:missing_deps
echo ERROR: Missing required Python libraries. No save was modified.
echo Install from this folder using:
echo     %PYTHON_CMD% -m pip install -r requirements.txt
set "RESULT=1"
goto finish
:finish
echo.
pause
popd
exit /b %RESULT%
