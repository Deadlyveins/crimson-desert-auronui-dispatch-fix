# Save safety and privacy

This is an experimental tool that modifies Crimson Desert save files. Use it carefully.

- **Back up your entire save directory** outside the game folder before using the tool.
- Work with a copy of `save.save`, not your only original.
- Use a separate save slot when testing repaired files.
- Close the game completely before replacing any files.
- Do not rely on Steam Cloud as your only backup.
- Only use the repair if the Auronui dispatch is genuinely stuck.
- The **recommended combined repair** applies both edits directly. The **separate Stage 2 fallback** must only be used after you load the Stage 1 file, save again inside the game, and exit.
- A successful check or a visually reset pier does not guarantee the mission is fixed.
- A new metadata combination can pass read-only checks, but does not mean it is safe to patch. An untested combination requires typing `UNTESTED`. This is an explicit experimental opt-in, not a safety guarantee.
- Do not upload personal save files or account details to public GitHub Issues.

The tool does not overwrite the input save. For successful repairs it creates a separate output file and a timestamped backup. The script itself does not send your saves anywhere. Installing Python packages with `pip` is a separate step that may use the internet.

The project is unofficial, experimental, and provided without warranty.
