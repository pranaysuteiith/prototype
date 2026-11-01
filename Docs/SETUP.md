# Setup and first run

## Get the repository and assets

Install Git and [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage). Authenticate to GitHub if you need to push.

```bash
git clone https://github.com/pranaysuteiith/prototype.git
cd prototype
git lfs install
git lfs pull
git lfs ls-files
python3 Tools/check_repository.py
```

Keep `.meta` files with Unity assets. A text file starting `version https://git-lfs.github.com/spec/v1` where an FBX/image should be means LFS content has not been downloaded. Unity may report broken assets until `git lfs pull` succeeds.

## Unity

Install Unity Hub and **Unity 6000.6.7f1**, the version in `ProjectSettings/ProjectVersion.txt`. Add WebGL Build Support if building for the browser. Add the cloned repository root as a project in Hub. Let packages, imports and compilation finish; do not open only the Assets subfolder.

Open `Assets/Scenes/GetStarted_Scene.unity`. Enter Play, click Game view and use arrows to walk. The prototype uses Unity's Input System and URP. Its manifest/lockfile record the package versions; do not upgrade them merely to open the project. Current custom features are listed in [FEATURE_STATUS.md](FEATURE_STATUS.md).

`Library`, `Logs`, `Temp` and local Editor settings are generated and ignored. Missing generated caches are expected. This initial import can take time and disk space; the source project was previously using roughly 4.5 GB for Library on its authoring Mac.

## Blender and Codex

Install an official Blender release and Codex locally. The boy was authored/checked using Blender 5.2.3 LTS. Use a compatible version and inspect changes when opening old assets. The local Blender executable on macOS commonly lives at `/Applications/Blender.app/Contents/MacOS/Blender`; locate your installation rather than assuming it on every OS.

See [Codex + Blender](CODEX_BLENDER.md) for a safe connection probe and [Codex + Unity](CODEX_UNITY.md) for the live Editor integration. The authoring Mac reported Codex CLI `0.164.0-alpha.11.1` and Unity CLI `1.0.0-beta.13`; these are observations, not portable minimum versions or promises of the newest release.

## Browser

The public prototype can be played immediately at https://doro-quiet-cafe.shrewdmoss10.chatgpt.site . Source-only checkouts do not include its large compiled data/WASM files. Build Unity WebGL and prepare a local distribution following [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) before serving the browser shell.

## Common issues

- Missing/pink assets: fetch LFS content, wait for imports, then inspect the material shader and actual pipeline. Do not switch the whole project pipeline as a shortcut.
- CLI cannot find the Editor: use an explicit cloned project path and check Safe Mode/compile errors. Do not target an Editor running a different checkout.
- Boy invisible: its visual renderers must be included by the map camera's layer mask; the current map uses layer 31 for visuals.
- Character floating: do not let the retained tutorial Ground collider replace the Doro walking layer. See `DoroBoyWalker` and the saved collision hierarchy.
- No browser audio: click the canvas after load and check mute/volume/browser permissions.
- Blender script points to the original Mac: inspect its `ROOT`/`OUT` constants. Historical generators are retained as source records and are not universally safe to rerun unchanged.
