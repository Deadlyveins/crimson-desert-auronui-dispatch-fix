@echo off
setlocal DisableDelayedExpansion
pushd "%~dp0" || exit /b 1
title Crimson Desert Auronui Dispatch Fix v0.5.1 Beta - Combined Repair (recommended)
echo.
echo ======================================================
echo  CRIMSON DESERT - AURONUI DISPATCH FIX v0.5.1 Beta
 echo  Combined Repair (recommended)
echo ======================================================
echo.
echo  EXPERIMENTAL. Back up your ENTIRE save directory.
echo  The original input save will NOT be overwritten.
echo  Only use this on the BROKEN Auronui Island dispatch.
echo  First try the quest as Kliff before editing any saves.
echo  This applies BOTH known repair stages in one operation.
echo  A new output save and backup are created. Original is untouched.
echo  For an unknown numeric profile, type UNTESTED to opt in.
echo  The tool CANNOT detect whether the quest is broken.
echo.
set "SAVE_PATH=%~1"
if not defined SAVE_PATH set /p "SAVE_PATH=Enter full path to a COPY of save.save: "
set "SAVE_PATH=%SAVE_PATH:"=%"
if not defined SAVE_PATH goto no_save
if not exist "%SAVE_PATH%" goto missing_save

echo.
echo Input: "%SAVE_PATH%"
echo.
rem Prefer the portable executable if it is included.
if exist "%~dp0AuronuiDispatchFix.exe" goto use_exe
rem Keep the original Python workflow available to developers.
if not exist "%~dp0auronui_reset.py" goto missing_tool
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
%PYTHON_CMD% "%~dp0auronui_reset.py" "%SAVE_PATH%" --stage auto
set "RESULT=%ERRORLEVEL%"
goto finish
:use_exe
"%~dp0AuronuiDispatchFix.exe" "%SAVE_PATH%" --stage auto
set "RESULT=%ERRORLEVEL%"
goto finish
:no_save
echo ERROR: No save path provided.
set "RESULT=1"
goto finish
:missing_save
echo ERROR: The save file was not found: "%SAVE_PATH%"
set "RESULT=1"
goto finish
:missing_tool
echo ERROR: AuronuiDispatchFix.exe and auronui_reset.py are both missing.
set "RESULT=1"
goto finish
:missing_python
echo ERROR: Portable AuronuiDispatchFix.exe is missing.
echo You can download the portable release to avoid installing Python.
echo Alternatively install Python 3.11 or newer.
set "RESULT=1"
goto finish
:missing_deps
echo ERROR: Python libraries are missing.
echo In this folder, run: %PYTHON_CMD% -m pip install -r requirements.txt
echo Or use the prebuilt portable release, which needs no Python.
set "RESULT=1"
goto finish
:finish
echo.
if not "%RESULT%"=="0" echo Operation did NOT complete successfully. Exit code: %RESULT%
pause
popd
exit /b %RESULT%
