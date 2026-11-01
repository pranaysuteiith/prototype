# Repository and important files

Repository: https://github.com/pranaysuteiith/prototype · default branch: `main` · visibility: public.

## The runnable Unity project

- `Assets/Scenes/GetStarted_Scene.unity`: saved café map, existing starter objects and playable boy integration.
- `Assets/DoroPainted/Models/DoroCrossroads.fbx`: normalized project-side environment export.
- `Assets/DoroPainted/Textures/` and `Materials/`: painted atlas/foliage and URP materials.
- `Assets/DoroPainted/Scripts/DoroBoyWalker.cs`: camera-relative arrows, rotation, gravity and walk/idle transitions.
- `Assets/DoroPainted/Scripts/DoroPanZoom.cs`: camera pan/orbit/zoom and optional player follow.
- `Assets/DoroPainted/Scripts/DoroCenterFocus.cs`: center ray, simplified subject hits, camera-forward depth and smooth DOF.
- `Assets/DoroPainted/Scripts/DoroViewLighting.cs`: temporary Doro-camera light/probe settings with restoration.
- `Assets/DoroPainted/Scripts/DoroAmbientSound.cs`: birds loop, delayed barks, mute/volume/blur messages.
- `Assets/DoroPainted/Characters/BoyGreenSweater/`: imported boy, materials, controller and reusable prefab.
- `Assets/DoroPainted/Characters/BellyDancer/`: supplied dancer and looping Animator Controller.
- `Assets/DoroPainted/Editor/DoroSceneSetup.cs`: setup reference; inspect its scene-creation behavior before running.
- `Packages/manifest.json` and `packages-lock.json`: package declarations and resolved versions.
- `ProjectSettings/ProjectVersion.txt`, `TagManager.asset`, `QualitySettings.asset`, `EditorBuildSettings.asset`: Editor version, layers, quality defaults and build scenes.

Keep all Unity `.meta` files: their GUIDs connect the scene, prefabs, scripts and assets.

## Blender and reusable character sources

- `Blender/Environment/doro-style.blend`: the environment master recovered from the original authoring workspace.
- `Blender/Environment/Scripts/`: build/detail/camera/refine/foliage/export scripts.
- `Blender/Environment/UnityExport/`: original supplied FBX/textures/scripts/manifest for comparison; its counts differ from the normalized Unity copy.
- `Blender/FemaleCharacter/Asset/`: earlier female Blender/FBX asset and renders; `Scripts/` holds its source workflow.
- `Blender/ConnectionProbe/`: early BlenderBalls transfer probe; not the final environment package.
- `Characters/Boy_GreenSweater/Blender/`, `Models/`, `Animations/`, `Textures/`, `Previews/`: reusable boy outputs and linked café copy.
- `Characters/Boy_GreenSweater/Work/`: creation/render/audit/export scripts.
- `Characters/Boy_GreenSweater/UnityMap/`: historical player integration and Play-mode checks.
- `AgentScripts/`: historical environment, camera/audio/dancer setup and checks; some assume an initial scene and original authoring paths.

Historical scripts and audit values retain provenance, including original absolute paths. They are not a portable bootstrap of the complete scene. The new helpers in `Tools/` use repository-relative inputs or explicit arguments.

## Browser and documentation

`Sites/doro-cafe/dist/index.html`, `app.js` and `style.css` are the shell. Its generated game directory and nested Sites Git metadata are excluded. `Tools/prepare_web_release.py` pairs this shell with a fresh WebGL build.

`Docs/Game-Doro.md` follows the owner's ten-point outline. `PRODUCT_MECHANICS.md` describes planned services. `FEATURE_STATUS.md` is the implementation boundary. `Doro-Project-History/` preserves the illustrated history, references and selected evidence. Full shared-chat text dumps and duplicate ZIPs are omitted from the public import; the report links to the shared source conversation.

`Docs/Validation/` contains selected historical checks and build/deployment evidence. `Docs/important-files.json` inventories executable/authoring source with paths and sizes. `Docs/repository-import.json` records what was included/excluded and the checks for this source import.

## Git workflow

```bash
git lfs pull
git switch -c feature/short-description
# edit, inspect and validate the relevant part
git add <changed-files>
git diff --cached --stat
git commit -m "Describe the concrete change"
git push -u origin feature/short-description
```

Open a pull request when collaborating. For a new binary format, add its LFS rule before staging assets. Keep scripts, scene YAML and `.meta` in ordinary Git; do not add build caches. Review files before pushing to this public repository. Use branches/checkpoints for scene experiments and keep the production publication workflow separate.

The live authoring folder and this Git checkout are separate copies. Future edits must be made in, or deliberately synchronized into, the checkout before committing. Do not assume the original Editor saves into the clone.
