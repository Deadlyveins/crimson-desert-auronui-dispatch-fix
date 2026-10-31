# Crimson Desert: Auronui Island Dispatch Fix

### v0.5.1 Beta | Windows / Steam | Experimental

An unofficial save-file repair tool for the **Auronui Island** pioneering dispatch that gets stuck at 100%, stays on "Awaiting Completion", or refuses to dispatch three Greymanes. It may also block "Signpost of the Great Ocean".

**Back up your entire save folder before using this tool. It is an experimental save editor, not an official patch.** The tool cannot determine whether your quest is actually broken.

## What's new

- **One-step repair:** `FIX_AURONUI.bat` applies both repairs to a copy of the save, without an in-game save between them.
- **Original four launchers are still available** if you need to try the old two-stage procedure.
- **More metadata combinations:** instead of adding individual combinations such as `(3,3,3)`, `(4,4,5)`, or `(3,4,5)` to the code, it examines the surrounding dispatch structure. New numeric combinations require an additional confirmation before changing anything.
- Backups, operation identification, structure checks, and save-integrity verification remain in place.

**Limitations:** This is **not** a universal quest or island fix. It targets one specific Auronui operation and only two recognized record layouts. Numeric combinations beyond the observed examples are experimental; matching a structure does not prove the repair will work in-game.

## Before you start

1. Try the dispatch as **Kliff** rather than Damiane or Oongka.
2. If possible, move any ship away from the Auronui pier.
3. Make a backup of the **entire** save directory, stored somewhere outside the active game folder. Steam Cloud alone is not a backup.
4. Make a fresh manual save at Auronui, close Crimson Desert completely, and copy that `save.save` to a working folder.

Saves are usually under `%LOCALAPPDATA%\Pearl Abyss\CD\save\` (the exact subfolder varies). **Never repair your only copy.**

## Installation

**Portable Windows version:** Download the *portable* release containing `AuronuiDispatchFix.exe`. Extract the ZIP to one folder. **Python is not needed.** Open `FIX_AURONUI.bat` in that folder.

**Source version:** Install Python 3.11 or newer, then open a terminal in the tool folder and run:

```powershell
py -3 -m pip install -r requirements.txt
```

The `.bat` files use the EXE when available and otherwise try the Python script. The **source/build-kit ZIP is not itself a compiled portable version**. To create an EXE, see `PORTABLE_BUILD_INSTRUCTIONS.md`.

## Recommended: One-step repair

1. Double-click `FIX_AURONUI.bat` or drag a **copy** of the original broken save onto it.
2. If prompted, paste the full save-file path, including the file name.
3. Read the result. If the save's metadata combination is new, you will be asked to type `UNTESTED` before continuing. This means the combination has **not** been verified in-game.
4. Type `FIX` to approve the repair. The program will create a backup and a **new** file with `_AURONUI_COMBINED_` in its name. Your input file is not overwritten.
5. Put a **copy of the new file** in a **separate test save slot**, rename that copy to `save.save`, then load it as Kliff.
6. Verify that you can assign three Greymanes, resources are consumed, the construction timer starts, and the mission eventually completes. A pier that merely looks reset is not sufficient.

If the tool refuses the save, **do not bypass its structural checks**. Report the error on GitHub. If the combined repair does not work in-game, restore your original broken backup and try the fallback below.

**Known limitation:** The progress value must change during Stage 1. If it is already `0.0`, the combined repair does not produce an output. This is not proof the quest is healthy.

## Fallback: Original two-stage repair

Use this on a **new copy of your original broken save** if the automatic repair does not work.

### Stage 1

1. Run `Check_Stage1_ONLY.bat` on the original broken save **copy**.
2. If the check passes, run `Run_Stage1_Reset.bat` on that copy. Type `RESET`.
3. Test the new `_AURONUI_STAGE1_` save in a separate slot. If the dispatch starts normally, stop.

### Stage 2, only if Stage 1 still does not work

1. **Load the Stage 1 output in Crimson Desert**, and make a **new manual save in-game** at Auronui.
2. Close the game and copy that **new in-game save** to your working folder.
3. Run `Check_Stage2_ONLY.bat`. If compatible, run `Run_Stage2_Reactivate.bat`, type `REACTIVATE`, and test the output in a separate slot.

**Do not use the original broken save or the raw Stage 1 output for this fallback Stage 2.** The tool asks you to acknowledge the in-game resave but cannot independently verify that it occurred. Do not apply the fallback over an already successfully repaired save.

When the construction finishes, a community tester reported that they completed the quest by boarding their ship, opening the dispatch menu, and pressing **Space**.

## Included launchers

| File | Purpose |
| --- | --- |
| `FIX_AURONUI.bat` | Recommended combined repair |
| `Check_Stage1_ONLY.bat` | Read-only Stage 1 check |
| `Run_Stage1_Reset.bat` | Original Stage 1 reset |
| `Check_Stage2_ONLY.bat` | Read-only Stage 2 check |
| `Run_Stage2_Reactivate.bat` | Original Stage 2 reactivation |

## Testing status

The combined method has restarted a dispatch in-game, and the v0.5.1 build has been reported working. Earlier versions also received successful independent community reports. Other save variations still need testing; a valid output file alone is not proof of in-game success.

## Feedback

If you test the tool, report your game version, whether you used the combined or two-stage method, the metadata numbers printed by the checker, whether the dispatch restarted, and whether the quest completed. **Do not publicly upload personal save files or account information.**

This free, MIT-licensed community tool is not affiliated with Pearl Abyss. It is offered as-is, without warranty.
