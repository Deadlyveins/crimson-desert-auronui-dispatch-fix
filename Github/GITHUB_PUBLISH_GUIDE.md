# Publish to GitHub (manual steps)

1. Go to https://github.com/new and create a **public** repo named `crimson-desert-auronui-dispatch-fix` (do not initialize with a README, license or gitignore: these are already included).
2. Extract `CrimsonDesert_Auronui_GitHub_Repo_v0.4.1-beta.zip` on your computer. Upload the **contents** as files in your repository, not the zip alone. Use **Add file → Upload files**, then commit changes.
3. Open **Releases → Draft a new release**. Create tag **`v0.4.1-beta`**, title **`v0.4.1-beta — Experimental Auronui Pioneer Dispatch Fix`**, tick **Set as a pre-release**.
4. Paste the text from `RELEASE_NOTES.md` as release notes. Attach `CrimsonDesert_Auronui_TwoStage_Fix_v0.4.1_BETA.zip` as a binary asset, then publish the prerelease.
5. Check the download is accessible without signing in. Copy the public release URL and SHA-256 checksum into `REDDIT_POST.md`, then publish the Reddit post.

Never upload `.save`, `.bak`, local path logs, personal account IDs, or private test data. Note that the in-game automated workflow hasn't been independently validated across players; keep the beta label.
