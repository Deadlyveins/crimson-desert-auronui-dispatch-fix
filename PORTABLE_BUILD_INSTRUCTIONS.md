# Build the portable Windows executable (v0.5.1 Beta)

**This source ZIP contains the build kit, not a compiled EXE.** To create the version for players, you can run the build on Windows or use GitHub Actions.

## Build on your Windows PC

1. Extract this repository ZIP into its own folder.
2. Double-click `BUILD_PORTABLE_WINDOWS.bat`.
3. The builder installs its dependencies, runs tests, compiles `AuronuiDispatchFix.exe`, and packages the portable release.
4. If successful, find `release\Auronui_Dispatch_Fix_v0.5.1_portable_beta.zip`.
5. Extract the **player ZIP** and test the included `FIX_AURONUI.bat` and fallback launchers against COPIES of saves. Verify the game behavior before publishing.

Python 3.11+ is required only on the **build machine**. Players who use the resulting ZIP with the EXE do not need Python.

## Build with GitHub Actions

Commit the updated repository files to GitHub, including the hidden `.github/workflows/build-windows-portable.yml` path. On GitHub open **Actions > Build portable Windows executable > Run workflow**. Download the generated artifact, extract it, and publish the **inner** `Auronui_Dispatch_Fix_v0.5.1_portable_beta.zip` as the release asset after testing.

The build's smoke test checks EXE startup and rejection of an invalid sample. It does **not** verify repairs in Crimson Desert.

All ZIPs produced by the packaging script extract into one named folder. The repository/source ZIP also uses a single top-level folder.
