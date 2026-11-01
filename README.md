# Game Doro

**A calm virtual café for builders doing deep work together.**

Doro is being designed for developers, vibe coders, founders and productivity workers building a technical project or business. The goal is to combine time blocking, quiet co-working, accountability and visible progress in a welcoming miniature café.

**Current release: a playable single-player 3D café prototype.** You can walk the green-sweater character, explore the neighborhood, orbit the camera and listen to park ambience. Focus timers, shared live rooms, coin/XP rewards and the public showcase board are **product designs documented here, not implemented services**.

[Play the published prototype](https://doro-quiet-cafe.shrewdmoss10.chatgpt.site) · [Game Doro documentation](Docs/Game-Doro.md) · [Feature status](Docs/FEATURE_STATUS.md)

![Doro café prototype](Docs/Doro-Project-History/images/published-v2.jpg)

## Play

Click **Enter the café**, then click the game canvas.

- Arrow keys: walk the boy; he turns, walks and returns to idle.
- WASD: pan the camera. Q/E: rotate the view.
- Middle/right drag: pan. Mouse wheel: zoom.
- M: mute ambience. B or **Soft focus**: toggle blur.

Desktop keyboard/mouse is the tested interface. The current game does not synchronize players across browsers.

## Open the source project

Install Git LFS before cloning; otherwise art files will be small pointer files.

```bash
git clone https://github.com/pranaysuteiith/prototype.git
cd prototype
git lfs install
git lfs pull
python3 Tools/check_repository.py
```

Open this repository root in **Unity Hub → Add project from disk**, using **Unity 6000.6.7f1** and its WebGL build module. Open `Assets/Scenes/GetStarted_Scene.unity`, let imports/compilation finish, and enter Play mode. Unity regenerates `Library/` locally. See [setup](Docs/SETUP.md).

## Documentation

- [Game Doro: the ten-point product and implementation guide](Docs/Game-Doro.md)
- [Time blocks, accountability, coins/XP and the social board](Docs/PRODUCT_MECHANICS.md)
- [Current features, gaps and roadmap](Docs/FEATURE_STATUS.md)
- [Codex + Blender](Docs/CODEX_BLENDER.md) and [Codex + Unity](Docs/CODEX_UNITY.md)
- [A non-Unity route: Blender + Codex + Godot or Babylon.js](Docs/ALTERNATIVE_ENGINES.md)
- [Reference images → consistent style → 3D → physics and interactions](Docs/VISUAL_PIPELINE.md)
- [Tripo, Mixamo and manual rigging](Docs/CHARACTER_TOOLS.md)
- [Code, important files and Git workflow](Docs/REPOSITORY_GUIDE.md)
- [Build and deployment](Docs/BUILD_AND_DEPLOY.md), [verification](Docs/VERIFICATION.md), [history](Docs/Doro-Project-History/README.md)
- [Contributing](CONTRIBUTING.md) and [asset/source notices](THIRD_PARTY_NOTICES.md)

## What is in this repository?

`Assets/`, `Packages/` and `ProjectSettings/` form the Unity project. `Blender/` holds the environment master, earlier female rig and their build scripts. `Characters/Boy_GreenSweater/` holds the reusable boy and its audits. `AgentScripts/` contains historical Editor automation. `Sites/doro-cafe/` contains the browser shell source. `Tools/` contains portable repository/build helpers.

Binary art uses Git LFS. Caches, duplicate backups, credentials, compiled browser game files and deployment archives are excluded. The browser shell therefore needs a fresh WebGL build before it can serve a local game. A GitHub push does **not** update the live website automatically.

## Provenance and limits

The current map and rigs were authored through Blender Python/CLI/MCP, then integrated and tested using Unity CLI. Generated images supplied visual references; they were not automatically converted into finished game geometry. The rigging-tool and alternative-engine guides are recommendations for future work, not claims that this repository used Tripo or already contains a Godot/Babylon port.

Historical tests cover camera controls, focus, audio, animation and character locomotion; they are not a guarantee of mobile performance or every possible pose. See [verification boundaries](Docs/VERIFICATION.md). No blanket license is assigned to third-party assets; see the notices.
