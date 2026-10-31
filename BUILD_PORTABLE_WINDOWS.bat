@echo off
setlocal EnableExtensions DisableDelayedExpansion
pushd "%~dp0" || (echo ERROR: Cannot open the build folder. & pause & exit /b 1)
title Auronui Dispatch Fix v0.5.1 - Build Windows Portable EXE
echo.
echo ============================================================
echo   AURONUI DISPATCH FIX v0.5.1 BETA
 echo   Build the portable Windows release
 echo ============================================================
echo.
echo  This builds the tool on YOUR Windows PC.
echo  Python is required only on this PC to BUILD the EXE.
echo  Players who use the finished ZIP will not need Python.
echo.

rem Prefer the Windows Python launcher, fall back to the python command.
where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if errorlevel 1 goto no_python
set "PYTHON_CMD=python"
goto python_ready
:use_py
set "PYTHON_CMD=py -3"
:python_ready
%PYTHON_CMD% --version
if errorlevel 1 goto fail

echo.
echo [1/4] Installing the build dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt "pyinstaller>=6.14,<7"
if errorlevel 1 goto fail

echo.
echo [2/4] Running source tests...
%PYTHON_CMD% -m unittest discover -s tests -v
if errorlevel 1 goto fail

echo.
echo [3/4] Building and checking AuronuiDispatchFix.exe...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --console --name AuronuiDispatchFix --hidden-import lz4.block auronui_reset.py
if errorlevel 1 goto fail
if not exist "dist\AuronuiDispatchFix.exe" goto fail
%PYTHON_CMD% "tools\smoke_test_portable.py" "dist\AuronuiDispatchFix.exe"
if errorlevel 1 goto fail

echo.
echo [4/4] Packaging one-folder release ZIP...
%PYTHON_CMD% "tools\package_portable.py" --exe "dist\AuronuiDispatchFix.exe" --output "release\Auronui_Dispatch_Fix_v0.5.1_portable_beta.zip"
if errorlevel 1 goto fail

echo.
echo ============================================================
echo   SUCCESS. THE BUILD COMPLETED.
echo.
echo   Your player download is here:
echo   release\Auronui_Dispatch_Fix_v0.5.1_portable_beta.zip
echo.
echo   It contains AuronuiDispatchFix.exe and five BAT files.
echo   The ZIP extracts into ONE folder.
echo   Test the EXE on a copied save before public release.
echo ============================================================
echo.
pause
popd
exit /b 0

:no_python
echo ERROR: Python was not found on this build PC.
echo Install Python 3.11 or newer, then rerun this builder.
goto fail
:fail
echo.
echo BUILD FAILED. Read the error above. No portable ZIP was published.
echo Your original save files are untouched by this build script.
echo.
pause
popd
exit /b 1
