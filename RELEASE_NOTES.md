# v0.4.6 Beta

This experimental update improves the Auronui Island dispatch fix for Crimson Desert.

## What changed?

- Added support for the two save formats we have encountered so far.
- Improved compatibility with saves from different players.
- Removed progress-number restrictions that were incorrectly rejecting some affected saves.
- Added more checks to avoid modifying saves we do not recognize.
- Kept four separate Windows launchers, one check and one repair launcher for each stage.
- Stage 1 no longer produces a misleading repaired file when the relevant value is already zero.
- Stage 2 now requires an acknowledgement that you loaded the Stage 1 save, saved again inside the game, and exited before continuing.

## Does it work?

A previously affected save was repaired manually, and the related quest was completed in-game. Tests with additional save files have helped improve compatibility, but we cannot guarantee that the automated v0.4.6 Beta fix will work for every player.

The tool is intended only for the broken Auronui Island dispatch. It does not automatically detect a broken mission or complete the quest.

**Back up your full save directory before using it, and test on a separate save slot.**

## Installation and instructions

Download `Auronui_Dispatch_Fix_v0.4.6_beta.zip` from the GitHub Release and follow the steps in [README.md](README.md).

This is an unofficial community project and is not affiliated with Pearl Abyss.
