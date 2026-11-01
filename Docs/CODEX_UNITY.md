# Codex + Unity

## Install and open the right project

Follow [SETUP.md](SETUP.md) first: Git LFS assets, Unity 6000.6.7f1, packages and the saved map. Start Codex in the cloned repository. It can coordinate the installed Unity CLI; a separate Unity MCP server is optional, not required for the CLI route used here.

This project uses Unity Technologies' `unity` CLI and `com.unity.pipeline`, **not** an unrelated package with a similar name. The checked manifest includes Pipeline `0.9.1-exp.1`; historical CLI commands below were used with CLI `1.0.0-beta.13`. Consult live command discovery for your installed version. [Unity Technologies CLI guide](https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/SKILL.md).

Verify `unity --version`. If not installed, use Unity's official installation guidance; its documented macOS/Linux installer is `curl -fsSL https://unity.com/install.sh | bash`. Review installer instructions before running them. The existing checkout already declares Pipeline; for a new project, the documented package setup is `unity pipeline install --project-path /absolute/project`.

## Connect and discover

Open **this checkout** in Unity Hub and let imports/compilation finish. Replace the example project variable with your clone's root:

```bash
DORO_PROJECT="$(pwd)"
unity status --until-ready --project-path "$DORO_PROJECT"
unity command --project-path "$DORO_PROJECT" --query scene
unity command --project-path "$DORO_PROJECT" --query script
```

Use an explicit project path for subsequent operations, particularly if the original authoring project is also open. Do not borrow another checkout's running Editor. If Pipeline is unavailable, check Safe Mode/Console compile errors first. Commands and parameters can change between package versions, so inspect the connected Editor's command schema before calling it.

## Inspect before editing

Ask Codex to identify the active scene, camera, renderer/pipeline, hierarchy and existing gameplay. Save a scene copy before mutation. Work in `Assets/Scenes/GetStarted_Scene.unity`; keep the named Doro roots and preserve unrelated scene objects. Avoid “setup” code that silently creates a new empty scene.

The runtime scripts are `DoroBoyWalker`, `DoroPanZoom`, `DoroCenterFocus`, `DoroViewLighting` and `DoroAmbientSound`. Inspect those before creating a competing controller or camera system. The focus triggers and walking colliders have different roles/layers.

## Run Editor automation carefully

Historical examples use the Pipeline `script run` command to compile an external C# file in memory and execute its static entry point:

```bash
unity command script run --project-path "$DORO_PROJECT" --timeout 120 -- --file /absolute/path/to/editor-task.cs --entry ClassName.Method --timeout 110
```

This is a command shape, not a ready-to-run class. The scripts under `AgentScripts/` and character Work/UnityMap folders often contain absolute paths, create assets or assume an initial scene state. Read/update them before replaying. Do not run `SetupWalker.Setup` against a scene already containing the saved player just to open the game.

## What to validate

Check compilation and Console errors; imported UVs/material shaders; correct scale/forward direction; explicit Humanoid mapping and Avatar validity; animation loops and root motion; keyboard movement; gravity/curbs/obstacles; following/orbit/zoom; autofocus and blur toggle; ambient sound and preservation of original gameplay. Save the scene and assets after successful checks.

The original project needed UV-name consolidation before export, URP material rebuilding and layer-specific walking collision. Those fixes are already in this checkout. Tests/audits are historical evidence, not proof that arbitrary edits remain correct. See [VERIFICATION.md](VERIFICATION.md).

## Build versus publish

Use a saved scene and the matching WebGL module. Discover `build run`/`build status` for your CLI, queue the build, and wait for a successful BuildReport before packaging. A Git commit or a local Unity save does not update the public site. See [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md).
