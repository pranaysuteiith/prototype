# Contributing to Doro

Start with [setup](Docs/SETUP.md), [feature status](Docs/FEATURE_STATUS.md) and [the repository map](Docs/REPOSITORY_GUIDE.md). Use a branch for a focused change and explain its behavior, verification and limitations in the pull request.

Keep the calm builder-focused experience in view. Product features proposed in documentation should not be marked implemented until runtime code, persistence/network behavior where required, and acceptance checks exist. Update the status and mechanics docs with the change.

Preserve scene objects and existing camera/gameplay systems. Back up a working scene locally before a destructive authoring operation. Keep unrelated asset upgrades or generated churn out of a documentation change. Preserve `.meta` files; use LFS for art and regular Git for source/YAML.

Historical generators can clear scenes or write absolute paths. Inspect and adapt them in an isolated process. Prefer reproducible small tasks, sharp preview inspection and an explicit target project over blind setup-script replay.

Before submitting, run `python3 Tools/check_repository.py`, syntax checks for changed helpers, and the relevant Blender/Unity/browser checks for runtime changes. State what was actually tested. Never commit credentials, local account state, caches or compiled builds. Respect upstream source/asset notices; public GitHub visibility is not a blanket license.
