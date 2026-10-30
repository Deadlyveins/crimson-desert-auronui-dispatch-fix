@echo off
setlocal DisableDelayedExpansion
pushd "%~dp0"
title Crimson Desert - Auronui Fix v0.4.6-beta - Stage 2 - Check Only
echo.
echo =============================================================
echo  CRIMSON DESERT - AURONUI FIX v0.4.6-beta (EXPERIMENTAL)
echo  Stage 2 - Check Only
echo =============================================================
echo  The ORIGINAL input will NOT be overwritten.
echo  Make a full BACKUP of your save folder BEFORE any changes.
echo  WARNING: Stage 2 requires loading your Stage 1 output into
echo           the game, SAVING AGAIN IN-GAME, and fully exiting first.
echo  Stop if your dispatch already works or you skipped Stage 1.
echo.
set "SAVE_PATH=%~1"
if not defined SAVE_PATH set /p "SAVE_PATH=Enter full path to a COPY of save.save: "
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
%PYTHON_CMD% "%~dp0auronui_reset.py" "%SAVE_PATH%" --stage 2 --check
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" echo ERROR: Tool exited with code %RESULT%. Input was NOT overwritten.
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
echo ERROR: Python 3 not found. Install Python 3.11+ (64-bit).
set "RESULT=1"
goto finish
:missing_deps
echo ERROR: Required Python libraries missing. No save was modified.
echo Install from this folder using:
echo     %PYTHON_CMD% -m pip install -r requirements.txt
set "RESULT=1"
goto finish
:finish
echo.
pause
popd
exit /b %RESULT%
