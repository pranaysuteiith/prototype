# GitHub source workflow

The Doro source checkout is prepared at `/Users/pranay/My project/GitHub/prototype` for [pranaysuteiith/prototype](https://github.com/pranaysuteiith/prototype). This replaces the earlier pre-installation checklist. The original Unity authoring folder remains separate.

GitHub CLI and Git LFS are installed and authenticated. Art assets are tracked with LFS; Unity caches, browser build distributions, duplicate backups and full shared-chat dumps are excluded. The original remote history is preserved.

Follow [setup](SETUP.md), the [repository guide](REPOSITORY_GUIDE.md) and [contribution workflow](../CONTRIBUTING.md). Run `python3 Tools/check_repository.py` from the checkout, inspect `git diff --cached --stat`, commit and push the intended branch. For binary changes, run `git lfs status` before committing. Do not force-push over another contributor's work.

A source push does not deploy the public website. Follow [build and deployment](BUILD_AND_DEPLOY.md) for that separate process. See [import evidence](repository-import.json) for the recorded source checks.
