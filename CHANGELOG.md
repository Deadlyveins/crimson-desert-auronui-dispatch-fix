# Changelog

## v0.5.1 Beta (October 31, 2026)

- Added the recommended **combined repair** (`FIX_AURONUI.bat`). It applies Stage 1 and Stage 2 in one operation, without an intermediate in-game save.
- Kept the original four launchers for the separate two-stage fallback method.
- Expanded metadata recognition beyond specific previously observed combinations, while keeping operation and layout validation. New combinations require explicit `UNTESTED` confirmation.
- Added combined-repair regression tests and included all five launchers in the portable Windows packaging process.
- Preserved separate output files, backups, and post-write integrity verification.
- The combined repair has been confirmed to restart a dispatch in-game. It is not yet verified for every save variation or for full quest completion in every case.

## v0.5.0 Beta (October 31, 2026)

- Began recognizing structurally compatible metadata variations without requiring an individual profile definition for each.
- Added extra confirmation for unobserved metadata combinations.
- Kept validation for the two observed Auronui record layouts.

## v0.4.9 and earlier

- Experimental compatibility improvements for player-observed metadata combinations including `(3,3,3)`, `(4,4,4)`, and `(4,4,5)`.
- Established the original two-stage repair procedure.
