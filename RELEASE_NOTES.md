# Crimson Desert: Auronui Island Dispatch Fix

### v0.5.1 Beta | Windows / Steam

An unofficial community tool for players whose Auronui Island pioneering dispatch gets stuck at 100%, shows "Awaiting Completion", or refuses to send three Greymanes.

**This update makes the repair simpler.** You can now attempt both repair stages together, without loading the game between them.

## What's new in v0.5.1?

- **One-step repair:** Run `FIX_AURONUI.bat` to apply both repair stages to a copy of your save.
- **No intermediate game save:** The combined repair does not require opening Crimson Desert between stages.
- **Original two-stage repair retained:** All four previous BAT files are still included as a fallback.
- **Broader save compatibility:** The tool can recognize additional metadata combinations when the rest of the Auronui dispatch data matches a supported structure. New combinations require you to type `UNTESTED` before proceeding.
- **Portable Windows option:** The prebuilt release can include `AuronuiDispatchFix.exe`, so players do not need to install Python. Make sure you download the **portable ZIP** rather than the source/build files.
- **Backups and checks:** The tool creates a separate repaired save and backup, leaving the supplied input file unchanged.

## How to use the one-step fix

1. **Back up your entire Crimson Desert save folder.** Do not rely on Steam Cloud alone.
2. While on Auronui Island as Kliff, make a new manual save. Close the game completely.
3. Copy `save.save` somewhere safe to work on it. Do not use your only original.
4. Extract the **portable** release ZIP and run `FIX_AURONUI.bat` on your copied save.
5. Follow the prompts. Type `UNTESTED` first if the tool warns that your metadata combination has not been verified, then type `FIX` to approve the repair.
6. Put a copy of the newly generated `_AURONUI_COMBINED_*.save` file in a separate test slot and rename it to `save.save`.
7. Load it in Crimson Desert as Kliff. Confirm that you can send three Greymanes, resources are consumed, and the construction timer starts.

If the combined repair fails, use the original Stage 1 and Stage 2 launchers as described in `README.md`. **Do not apply the fallback Stage 2 directly to Stage 1 output:** for that manual method, you must load Stage 1 in-game and make a fresh in-game save first.

## Testing and limitations

We have confirmed an in-game restart using the combined approach, and several players have reported successful repairs with the earlier two-stage approach. Some community reports also confirm full quest completion. **This does not mean every save or every new metadata combination has been tested.**

The tool only targets the Auronui Island dispatch. It cannot detect whether a quest is actually broken and does not repair other islands or unrelated missions. A technically valid save or a visually reset pier is not enough to confirm success. Test the actual dispatch and eventual quest completion.

**Do not use this tool on a healthy save.** Keep your original backup and use a separate test slot.

If you encounter an error, please open a GitHub Issue with your game version, the error message, the repair method you used, and what happened in-game. Do not publicly post personal save files or account information.

This is an experimental, unofficial, open-source community project. It is not affiliated with Pearl Abyss. Distributed under the MIT License, as-is and without warranty.
