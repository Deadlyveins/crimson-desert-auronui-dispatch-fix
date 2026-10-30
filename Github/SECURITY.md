# Security and save-data privacy

- **Back up your entire save directory to a different physical location or folder before testing.** A test slot alone is not a guaranteed backup, and Steam Cloud can synchronize mistakes.
- Work on a **copy** of `save.save`, never your only save. Close the game before swapping files.
- Do not upload saves to a public issue or Reddit post; they may contain identifying information.
- Treat an unexpected structural match/failure as a reason to stop, not a reason to bypass the checks.
- Inspect `auronui_reset.py` and `.bat` launchers before executing them. This tool does not implement networking; `pip` only retrieves dependencies when you explicitly install them.
- This is an independent research workaround. Unexpected save versions, partially repaired states or later patches may be incompatible.
- If you suspect a defect in the fixer, open a GitHub issue with non-sensitive error output and game version. Do not post private files publicly.
