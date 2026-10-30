# Crimson Desert — Auronui Island Dispatch Fix

**Unofficial two-stage save-file workaround · v0.4.1-beta · Windows / Steam · Experimental**

> [!CAUTION]
> **BACK UP YOUR ENTIRE SAVE FOLDER OUTSIDE THE GAME AND STEAM CLOUD BEFORE YOU TRY THIS.**
> Keep an unmodified backup and any already-working save separate from your test slot.
> This tool edits save data and can break game progress. It is **not** a general quest fixer.

## What problem does this target?

The **Auronui Island Pioneer dispatch** in *Crimson Desert: Charting the Unknown* can become stuck after reaching **100%** with no usable **Complete Mission** action. Another symptom is the UI prompting you to dispatch three Greymanes again even though the operation appears complete; confirming **Dispatch** does nothing (no materials deducted and no countdown).

**Use this only if your symptoms match AND the read-only preflight check accepts your save.** A preflight pass indicates a matching known data pattern, **not** proof that your save needs modification.

## Status / evidence

- A two-stage **manual repair was successful on one player's save**, including dispatching the crew, rebuilding the pier, reaching 100%, claiming completion, and completing *Signpost of the Great Ocean*.
- The two automated stages have been checked against the successful reference modifications at the decrypted-payload level, and save integrity round-trips passed.
- **The automated two-stage process has not been independently validated across multiple players' saves.** This is a **beta**, not a guaranteed fix.
- On October 30, 2026, the tester observed that an October 30 game hotfix did not repair their **already-stuck unmodified save**. This says nothing about other saves or later fixes.
- Tested against **2.04.00-era** game saves; later updates are **unverified**.

## Prerequisites

- Windows / Steam edition of Crimson Desert.
- Python **3.11+** (Python **3.13** tested).
- Install Python requirements from the unzipped folder with `py -3 -m pip install -r requirements.txt`.
- Make a manual save while **physically on Auronui Island** and load your test save there. This reflects the successful workflow but is **not a proven technical necessity**.
- **Close the game completely** before running the tool or replacing any save.
- Consider temporarily disabling Steam Cloud for this game while testing. Be careful of sync conflicts when enabling it again.

## How to use (two stages)

**Stage 1: From a newly saved copy of an ORIGINAL broken save**

1. **Back up the entire save folder first**, outside Steam Cloud. Use a **test slot**, not your only save.
2. Go to Auronui Island, make a fresh manual save, and close Crimson Desert.
3. Run `Check_Stage1_ONLY.bat` and enter the full path to a **copy** of `save.save` (or drag it onto the batch file).
4. If the checker refuses it, **stop**. Do not disable the checks.
5. Run `Run_Stage1_Reset.bat` on that copied save. Type `RESET`.
6. The program creates a **backup** and a separate `*_AURONUI_STAGE1_*.save`. **It does not overwrite the input.**
7. Rename **a copy of the generated output** to exactly **`save.save`**, and put it in your **test slot**, replacing only that slot's save. Enable Windows' file extensions so it doesn't become `save.save.save`.
8. Load that test slot while on Auronui Island. The pier may partially or fully disappear as the dispatch resets.
9. Try dispatching the three Greymanes. **If the countdown starts and materials are deducted, STOP — do not run Stage 2.** Let the mission finish normally.

**Stage 2: ONLY if Stage 1 reset the visuals, but 'Dispatch' still does nothing**

10. Still on Auronui, **create another fresh in-game manual save** from the Stage 1 test state. **Close the game**.
11. Run `Check_Stage2_ONLY.bat` on a **copy of that NEW in-game save**. This is **not** the original save nor the raw Stage 1 output.
12. If accepted, run `Run_Stage2_Reactivate.bat`, and enter `REACTIVATE`.
13. Rename a copy of the generated Stage 2 output to exactly `save.save`; place it in the **test slot** and load it on Auronui Island.
14. Verify dispatch starts (resources deducted, timer starts), progresses, offers **Complete Mission**, **and completes successfully**.

> [!WARNING]
> Stage 2's structural checks cannot reliably distinguish **all** healthy active dispatches from broken ones. You must verify in-game that the Stage 1 dispatch confirmation does nothing before attempting Stage 2.

## What changes?

This is **not** a force-completion mod. It targets a known specific operation record in the save: faction node `1001022`, operation `0xE4BE83E8`, three assigned workers.

- **Stage 1:** Replaces the known stuck operation's **four-byte progress float** with `0`, to revert its construction state.
- **Stage 2 (only if needed):** Applies the observed **state `0x01`** and localized serialization-layout adjustments from the successful manual experiment to the **in-game re-saved partial-reset state**.

The script decrypts, edits and re-encrypts the save. It checks the original save integrity and validates the output by decrypting it again. It creates distinct backup/output files and is designed **not** to overwrite the source file.

## If anything fails

**Stop and restore your saved backup.** Do not repeatedly patch an incompatible file, bypass checks, or edit the only copy of your progress. Don't post personal save files publicly; they may contain account or character information.

## Security / privacy

The Python and batch source is readable and included in the repository. The script does **not** connect to a server or upload your files. Dependency installation through `pip` contacts the package index to download Python libraries. No game assets or personal save files are distributed. See [SECURITY.md](SECURITY.md).

## Reporting outcomes

Open an Issue with: game version, symptom, whether Stage 1/2 was used, preflight result, whether resources were deducted and a timer began, and whether the quest finished. **Do not attach personal save files or screenshots containing account IDs or local usernames.**

### Disclaimer

Unofficial fan project. Not affiliated with Pearl Abyss, Valve or Steam. Provided **as-is**, without warranty. Use at your own risk.
