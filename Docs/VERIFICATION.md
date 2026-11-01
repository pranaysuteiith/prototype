# Verification and limitations

## Historical runtime evidence

The illustrated [history](Doro-Project-History/README.md) and selected `Docs/Validation/` JSON files preserve the development checks. They cover environment material/UV repair; camera pan/orbit/zoom/focus; audio looping/mute/volume; dancer looping/root stability; boy topology, weights, FBX reopen and Humanoid mapping; all five authored actions; arrow movement, grounded walking, camera follow and boundary blocking; and local/production browser loading/rendering.

The early M2 Editor profile is a short historical sample of an earlier scene. It is not a browser/mobile or current-build performance promise. Runtime errors were not observed in the saved final checks, but non-blocking shader/future collider pre-baking warnings remained in the browser build.

## Checks for the GitHub source import

The source-import work does not add gameplay or rebuild the Unity game. It preserves the Assets/Packages/ProjectSettings file bytes and all Unity asset metadata, includes the original Blender authoring sources and adds documentation/portable helpers. Verification for this import includes:

- Asset/package/project-settings copy hash comparison.
- LFS configuration and local object integrity.
- No nested `.git`, generated Unity Library or compiled game distribution in the commit.
- Documentation relative-link and source-inventory checks.
- Python helper syntax and a non-destructive Blender CLI probe.
- Browser-shell JavaScript syntax.
- A controlled fixture check of WebGL staging/chunk reconstruction/WASM validation.
- Comparison of the pushed branch SHA with the local commit.

Results are recorded in `Docs/repository-import.json`. A fresh Unity import, a new browser deployment, multiplayer verification and mobile profiling are not performed by a source/documentation push. Open the cloned project and validate runtime changes when implementing new features.

## Product status

Time blocking, live builder presence, coins/XP spending and the public presentation board are specifications, not implemented code. Neither a valid rig nor generated documentation is evidence of those systems. See [FEATURE_STATUS.md](FEATURE_STATUS.md).
