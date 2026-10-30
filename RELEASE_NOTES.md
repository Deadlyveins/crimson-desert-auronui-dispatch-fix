# v0.4.1-beta — Experimental Auronui Pioneer dispatch repair

AURONUI DISPATCH FIX 0.4.1 - EXPERIMENTAL PUBLIC BETA (2026-10-30)
================================================================
SCOPE: Windows Steam save-file repair of ONE Auronui Island Pioneer mission
bug in Crimson Desert: Charting the Unknown.

Symptoms: dispatch reached 100% without an available Complete action;
or mission says to dispatch again, but dispatch confirmation fails.

METHOD: two-step experimental operation-state repair.
1) Stage 1 resets four progress bytes, recreating an earlier construction state.
2) If Stage 1 alone does not allow dispatch, load and RESAVE in-game on
   Auronui Island; Stage 2 adds the operation state + localized layout edits
   from the earlier effective manual Test A.

CRITICAL: BACK UP ENTIRE SAVE FOLDER before attempting. Disable Steam Cloud
sync while swapping files. Work only in a separate test save slot.
The script DOES NOT overwrite source files. Rename the output COPY to
exactly save.save before placing it in the test slot.

WHAT HAS BEEN VERIFIED:
- Original stuck save identified by known operation signature and counter.
- Manual two-stage repair allowed starting a dispatch, rebuilding the pier,
  reaching 100%, claiming completion and completing the faction quest.
- Automated Stage 1 and Stage 2 reproduce the intended manual payloads on
  the two reference saves; save container integrity roundtrips passed.
- A player observed the original stuck save remain stuck after an Oct 30
  hotfix; this does not prove that every hotfix fails to repair saves.

WHAT HAS NOT BEEN VERIFIED:
- Success on other players' saves or game builds.
- Fully automated end-to-end quest completion independently of the manual
  reference test; runtime results may vary.
- That a particular current hotfix universally does or does not resolve this.

REFUSALS ARE INTENTIONAL. Do not override guards if the save does not match.
PLEASE DO NOT UPLOAD OR SHARE SOMEONE ELSE'S PERSONAL SAVE FILE.
