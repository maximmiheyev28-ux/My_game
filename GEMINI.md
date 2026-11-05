# Gemini agent instructions — Последний сигнал

You are a coding agent working on an existing Godot 4.7.2 Android game.

Before changes:
- Read .github/copilot-instructions.md and .github/TEAM_WORKFLOW.md.
- Run python3 restore_source.py to reconstruct the working project from the preserved source archive.
- Inspect open production issues and actual project files; never infer missing content.

Priorities:
1. Fix reproducible gameplay and project defects.
2. Improve original HD pixel art, animation readability, enemy telegraphs/reactions, parallax and animated cinematic sequences.
3. Keep the composition readable, the hero slightly smaller than oversized drafts, and backgrounds restrained rather than cluttered.
4. Preserve the branching narrative, four endings, hard one-hit combat, katana and the local 78 px non-damaging «Стазис» field.

Rules:
- Do not copy Katana ZERO assets, scenes, music, characters or UI.
- Do not delete or overwrite .source or other original source material.
- Do not add fake, duplicate, empty or unused assets to inflate the game to 1–2 GB.
- Work in small, reviewable changes. Do not commit secrets.
- Run python3 tools/validate_project.py and relevant checks after changes.
- Report checks that were not possible. A successful APK export is not physical-device gameplay QA.
- Never merge your own pull request.
