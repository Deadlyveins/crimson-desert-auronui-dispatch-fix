# [Experimental PC fix] Auronui Island Pioneer dispatch stuck at 100% / Dispatch does nothing

I ran into a bug with the Auronui Island pioneering dispatch in *Crimson Desert: Charting the Unknown*. The mission reached 100% but couldn't be completed. Later the UI said to dispatch three Greymanes again, but Confirm did nothing — no resources were deducted, and no timer started.

An October 30 hotfix **did not repair my already-broken original save**. We investigated the save data and developed a **two-stage experimental Python workaround**. The *manual* recovery allowed the pier to be rebuilt and the quest **Signpost of the Great Ocean** to be completed. The automated scripts reproduce the known data modifications, but **they have not yet been independently validated on other players' saves**.

**IMPORTANT: BACK UP YOUR ENTIRE SAVE FOLDER outside the game's live folders and Steam Cloud before doing anything. This modifies save data and may damage progress. Use a separate test slot.**

**Quick instructions:**

1. Stand on Auronui Island. Make a fresh manual save in a **test slot**. Completely close the game.
2. Check the save with `Check_Stage1_ONLY.bat`. If rejected, **stop**. If accepted, run `Run_Stage1_Reset.bat` on a **copy**.
3. Rename a **copy** of the generated Stage 1 output file to exactly **`save.save`** (check Windows file extensions). Put it into your **test slot** and load it.
4. Try dispatching the Greymanes. **If resources are deducted and the timer runs, STOP. Don't apply Stage 2.**
5. **Only if Dispatch still does nothing:** Make another new **in-game save** from the partial reset state while on Auronui. Close the game. Run `Check_Stage2_ONLY.bat`, then (if accepted) `Run_Stage2_Reactivate.bat` on that **new save**.
6. Rename a copy of Stage 2 output to `save.save` in your test slot. Load it and verify the quest starts **and actually completes**.

Needs Windows, Python 3.11+ (3.13 tested), `cryptography` + `lz4`. The tool verifies known patterns and save integrity, keeps the source file unchanged, and creates separate backups/outputs. Source is included; no account data, player saves or copyrighted game assets are distributed. Read the full README and warnings before trying it.

**GitHub source + prerelease:** [ADD GITHUB REPO / RELEASE URL AFTER PUBLISHING]
**Download SHA-256:** `99e83e265638768be4b53a1ce0944428ba09abf41df8693eb6488f131585590b`

If you test it, please report game version, which stage you needed, and whether the quest finally completed. Please **do not upload your personal save file publicly**.

Unofficial community workaround, not a Pearl Abyss patch.
