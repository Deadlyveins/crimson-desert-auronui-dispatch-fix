@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
title Crimson Desert Auronui Experimental v0.4.1
set "STAGE=%~1"
set "INPUT=%~2"
set "CHECK=%~3"
echo.
echo =============================================================
echo  CRIMSON DESERT - AURONUI EXPERIMENTAL TWO-STAGE FIX v0.4.1
 echo =============================================================
echo  Stage %STAGE%. Input will NEVER be overwritten.
echo.
if not "%STAGE%"=="1" if not "%STAGE%"=="2" (echo ERROR: Bad stage.& pause & exit /b 1)
where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (echo ERROR: Python 3 not found.& pause & exit /b 1)
    set "PY=python"
)
%PY% -c "import cryptography, lz4.block" >nul 2>nul
if errorlevel 1 (
    echo ERROR: Missing Python dependencies. No save was changed.
    echo Open Command Prompt and run:
    echo py -3 -m pip install cryptography lz4
    echo Then run this launcher again.
    pause
    exit /b 1
)
if not defined INPUT (
    echo.
    set /p "INPUT=Enter full path to a COPY of save.save: "
)
REM Explorer Copy as Path may include double quotes.
set "INPUT=%INPUT:"=%"
if not defined INPUT (echo ERROR: No path.& pause & exit /b 1)
if not exist "%INPUT%" (echo ERROR: File not found: "%INPUT%" & pause & exit /b 1)
echo.
echo Input: "%INPUT%"
if /I "%CHECK%"=="CHECK" (
    %PY% "%~dp0auronui_reset.py" "%INPUT%" --stage %STAGE% --check
) else (
    %PY% "%~dp0auronui_reset.py" "%INPUT%" --stage %STAGE%
)
echo.
pause
