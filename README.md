# Crimson Desert: Auronui Island Dispatch Fix

**Latest version: v0.4.6 Beta | Windows / Steam**

An unofficial, free, open-source tool that may help fix the stuck Auronui Island pioneering dispatch in **Crimson Desert: Charting the Unknown**.

**This is an experimental save-file repair tool. Back up your saves before using it.**

## What problem does it fix?

This tool is intended for players who are stuck on the Auronui Island pioneering mission. Common symptoms include:

- The dispatch reaches **100%**, but you cannot complete it.
- The mission says **"Awaiting Completion"**, but no completion option works.
- You select three Greymanes and confirm the dispatch, but nothing happens.
- No resources are used and no new construction timer starts.
- You cannot continue **"Signpost of the Great Ocean"**.

The tool attempts to get the dispatch working again. It does **not** automatically complete the quest or give rewards.

If your dispatch is working normally, **do not use this tool**.

## Before using the tool

Try these steps in the game first:

1. Switch to **Kliff** if you are playing as Damiane or Oongka, then try the dispatch again.
2. If possible, move any ship away from the Auronui Island pier.
3. Make sure your problem matches one of the symptoms above.

If nothing helps, you can try the repair tool.

## Download and installation

1. Go to the **Releases** section of this GitHub repository.
2. Download **`Auronui_Dispatch_Fix_v0.4.6_beta.zip`** and extract it.
3. Install **Python 3.11 or newer** if you do not already have it.
4. Open a terminal in the extracted folder and run:

```powershell
py -3 -m pip install -r requirements.txt
```

You only need to install the Python requirements once.

## Back up your saves

**Back up your entire save folder before making any changes.** Your Crimson Desert saves are normally under:

```text
%LOCALAPPDATA%\Pearl Abyss\CD\save\
```

The exact subfolder may differ. Keep the original files somewhere safe, outside the active save folder. **Use a separate manual save slot for testing.** Do not rely on Steam Cloud as your only backup.

Always **close the game completely** before copying or replacing save files. Give the tool a **copy** of `save.save`, not your only original.

## Step 1: Reset the dispatch

1. Go to **Auronui Island** as Kliff and create a fresh manual save.
2. Close Crimson Desert completely.
3. Make a copy of that save's `save.save` file.
4. Run **`Check_Stage1_ONLY.bat`** and select the copied file. You can drag the file onto the launcher or enter its full path when asked.
5. If the check passes and your dispatch really is broken, run **`Run_Stage1_Reset.bat`** on the same copy.
6. Type **`RESET`** when prompted.
7. The tool creates a new file with a name like `save_AURONUI_STAGE1_*.save`.
8. Put a copy of that new file into a **separate test save slot** and rename the copy to `save.save`.
9. Load the test save in the game as Kliff and try dispatching three Greymanes again.

**Look for a real restart:** Resources should be deducted and a new timer should begin. The pier looking reset is not enough to confirm success.

**If the dispatch works, stop here. You do not need Step 2.**

If Step 1 says the progress counter is already zero and creates no modified save, it has **not** repaired the issue.

## Step 2: Reactivate the dispatch (only if Step 1 did not work)

**Use this only if Step 1 created a modified save, you loaded it in the game, and the dispatch is still broken.**

1. Load the **modified Step 1 save** in Crimson Desert.
2. While still on Auronui Island, make a **new manual save inside the game**.
3. Wait for the save to finish, then close the game completely.
4. Make a copy of this **new in-game save**.
5. Run **`Check_Stage2_ONLY.bat`** on the new copy.
6. If the check passes and the dispatch is still broken, run **`Run_Stage2_Reactivate.bat`**.
7. Type **`REACTIVATE`** when prompted.
8. Put a copy of the generated Stage 2 save into a separate test slot, rename it to `save.save`, and load it as Kliff.
9. Try the dispatch again. Check whether resources are consumed, a timer begins, and the quest can eventually be completed.

**Important:** Step 2 must use the **new save made inside the game after loading Step 1**. Do not use your original broken save or the Stage 1 output file directly.

## What's new in v0.4.6 Beta?

- Support for two save formats found during testing.
- Improved compatibility with saves from different players.
- Better checks to avoid changing unrecognized saves.
- Separate launchers for checking and applying each repair stage.
- Clearer handling of saves where Step 1 has nothing to change.

A previously affected save was repaired manually and the quest was completed in-game. The automated tool has undergone additional testing, but **successful quest completion with v0.4.6 is not guaranteed for every player**.

See [CHANGELOG.md](CHANGELOG.md) for the release history.

## Known limitations

- This only targets the **Auronui Island pioneering dispatch**. It is not a general quest fixer.
- Some saves may not be supported, especially after future game updates.
- A successful tool message does not guarantee the mission works in-game.
- The tool cannot tell for certain whether your quest is broken.
- Step 2 cannot verify that you followed the in-game resave instructions.

## Feedback and bug reports

If you test the tool, please open a **GitHub Issue** and let us know whether:

- Step 1 passed and worked.
- Step 2 was needed.
- The dispatch actually restarted and its timer appeared.
- You eventually completed **"Signpost of the Great Ocean"**.

Include your game version and any error messages if possible. **Do not publicly share personal save files or account details.**

## Disclaimer and license

This is an unofficial community project and is **not affiliated with Pearl Abyss**. It is provided as-is under the **MIT License**, without warranty. Editing game saves carries risks, so keep your original backups.
