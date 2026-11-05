# Repository instructions for GitHub Copilot coding agents

This repository contains «Последний сигнал», an original Android 2D side-scroller. Read `.github/TEAM_WORKFLOW.md`, the relevant specialist profile in `.github/agents/`, and the current open production issue before changing code.

## Non-negotiable project constraints
- Target Godot 4.7.2, Android ARM64, landscape orientation, and a 60 FPS target.
- Preserve the approved design: hard difficulty, one-hit combat, katana, side camera, branching story with four endings, protagonist НОЛЬ/07, and «Стазис» as a local 78 px-radius freeze field that deals no damage.
- Use original assets only. Katana ZERO is a high-level style reference; do not copy its sprites, animation frames, environments, UI, characters, music, or scenes.
- Keep backgrounds composed and readable. Avoid clutter, oversaturated palettes, noisy detail, or visual effects that obscure hazards.
- The protagonist should remain slightly smaller than earlier oversized drafts, with consistent proportions and a readable silhouette.
- Enemies must have distinct silhouettes, readable attack telegraphs, hit reactions, and defeat states.
- Cutscenes must be genuinely animated sequences, not static slides or dialogue-only panels.

## Required execution loop
1. Inspect the actual source tree and current behavior before editing. The game is restored by `python3 restore_source.py`; never assume the working tree contains the extracted project before running it.
2. Establish a small, playable vertical-slice target with explicit acceptance criteria before attempting broad rewrites.
3. Delegate design/art review, Godot implementation, and independent QA to the repository's custom agent profiles when the cloud-agent runtime supports sub-agent delegation. If delegation is unavailable, perform the roles sequentially and state that limitation.
4. Make focused changes. Preserve existing working behavior and keep the source archive intact.
5. Run `python3 restore_source.py`, `python3 tools/validate_project.py`, Python syntax checks for changed scripts, Godot headless import/parse, and Android ARM64 export when applicable.
6. Inspect the produced artifacts and relevant scenes/resources. Fix failures and repeat the checks after fixes.
7. Open a pull request with changed paths, screenshots/contact sheets where possible, test results, APK size, and known limitations. Never self-approve or merge without review.

## Size and release rules
- The 1–2 GB target refers to a measured installed game/content size only if the content genuinely requires it. Never inflate the APK with duplicate, empty, random, or unused data.
- Report APK/AAB download size, expansion/downloadable asset size, and installed footprint separately. If the complete game is smaller, report the real size.
- Do not claim 60 FPS, physical-device compatibility, completed chapters/endings, visual parity with a commercial game, or successful playtesting without corresponding evidence.
- A successful export or APK signature check is not a gameplay QA pass.

## Work safety and reporting
- Treat source assets and story decisions as user-owned project data. Avoid destructive rewrites and preserve the original archive.
- Do not add credentials, tokens, private signing keys, or secrets to commits, logs, or artifacts.
- Prefer additive changes and reversible commits. Do not force-push.
- Report blockers immediately; do not fabricate missing art or claim missing source materials were integrated.
- Work autonomously within the issue's scope, but leave the result in a reviewable PR.