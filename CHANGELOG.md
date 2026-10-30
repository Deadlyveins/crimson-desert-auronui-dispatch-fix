# Changelog

## v0.4.6 Beta (October 30, 2026)

- Added support for two observed Auronui save layouts.
- Improved compatibility with player-specific save data.
- Removed overly restrictive progress checks that could reject affected saves.
- Added clearer safeguards for Step 2. It must be used only after loading the Step 1 save and making a new in-game save.
- Step 1 now avoids creating a misleading modified file when the target value is already zero.
- Kept four separate launchers: two checks and two repair actions.
- Kept save validation and verification of generated files.

**Status:** Experimental. A previously affected save was recovered through manual editing and the quest completed in-game. Compatibility testing has covered the two observed save layouts, but end-to-end results for this packaged beta are not confirmed for all affected saves.
