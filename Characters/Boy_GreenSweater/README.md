# Boy Green Sweater

A reusable, full 3D chibi character based on the user-approved `Stylised 3D Character Reference Sheet.png`. The unavailable original photograph was not used.

## Files

- `Blender/Boy_GreenSweater.blend`: editable, packed-texture master; symmetrical T-pose rest rig; studio scene and five actions.
- `Models/Boy_GreenSweater_Rigged.fbx`: complete model, rig and five animation takes, Y-up export, no generated leaf bones.
- `Animations/Boy_Idle.fbx`, `Boy_Walk.fbx`, `Boy_Run.fbx`, `Boy_Wave.fbx`, `Boy_Sit.fbx`: complete rig/model with one named animation take each.
- `Textures/`: reusable base-color and normal maps; face blush map.
- `Previews/Front.png`, `Back.png`, `Left.png`, `Right.png`, `Isometric.png`: orthographic studio views.
- `Previews/Walking.gif`: one-second in-place walking loop; 24 individual frames also available.
- `Previews/Idle.png`, `Wave.png`, `Sit.png`: additional pose previews.
- `Previews/Unity_*.png`: actual Unity camera renders captured during Play-mode animation tests.
- `Blender/Cafe_With_Boy_GreenSweater.blend`: café copy with a linked, looping-idle character instance near the terrace. Keep this file beside `Boy_GreenSweater.blend`; its character library path is relative.
- `Backups/Cafe_Before_Boy.blend`: backup taken from the live café before adding anything.

## Character

23,798 triangles, 12,095 vertices, 29 mesh objects and 22 bones. Height approximately 1.22 m, with feet at Z=0 and origin centered between the feet. Blender source faces -Y, Z-up. The café instance is scaled uniformly by 1.5 to suit the environment.

Armature: `ARM_Boy_GreenSweater`. Collection: `CHAR_Boy_GreenSweater`. Sunglasses frames and lenses are separate meshes. Head accessories follow the Head bone; the continuous sweater and trousers have blended skin weights. `CH_Cheeks` is an organizational control; cheek volume and blush are integrated into the head rather than separate raised patches.

## Actions at 24 fps

- `ANIM_Idle`: frames 1–73, 3 seconds, loops.
- `ANIM_Walk`: frames 1–25, 1 second, in place, loops.
- `ANIM_Run`: frames 1–19, 0.75 seconds, in place, loops.
- `ANIM_Wave`: frames 1–97, 4 seconds, returns to standing.
- `ANIM_Sit`: frames 1–73, 3 seconds, ends seated. Align the root and chair to the final seat height for the chosen furniture.

The master Blender file opens in the T-pose with no active action. Select its armature and choose an action in the Action Editor to preview. A second shared-mesh collection, `CHAR_Boy_GreenSweater_CafeIdle`, contains the looping idle rig used by the linked café instance.

## Unity

Imported and tested in `/Users/pranay/My project` using Unity 6000.6.7f1 and the project's existing URP pipeline.

Prefab: `Assets/DoroPainted/Characters/BoyGreenSweater/Boy_GreenSweater.prefab`.

The importer explicitly maps the humanoid bones. The Avatar is valid and human, with all checked major bones mapped. All five imported clips are Humanoid motion. URP materials use supplied texture maps, including normal maps and baked face blush. The prefab's Animator Controller defaults to Idle and contains a separate state for each clip. For example:

```csharp
animator.Play("ARM_Boy_GreenSweater|ANIM_Walk");
```

Root motion is disabled; move/turn the GameObject from gameplay code. This delivery is a character asset and animation controller, not a player movement implementation. The character was not permanently added to the existing Unity café scene. Play-mode test objects and lights were temporary and removed on exit.

## Validation

- Blender geometry: no nonmanifold edges in the audited meshes, no unweighted skinned vertices, normalized deformation weights, no negative object scales.
- Symmetrical horizontal-arm T-pose skeleton; head, shoulder, elbow, hip, knee, foot and torso rotation tests produced finite mesh deformations.
- Visual inspection of front, back, both sides, isometric, walking, waving and seated previews; face placement, hair coverage and foot placement corrected during inspection.
- Idle, Walk and Run start/end bone matrices match. Sampled shoe geometry across every animation frame stays above Z=0 within floating-point tolerance. This does not assert zero sliding under arbitrary retargeted animations.
- All six FBX files reimported successfully: 22 bones, 23,798 triangles, UVs and skin weights preserved; expected animation takes present.
- Unity Avatar validity and Humanoid motion checked; Idle, Walk, Run, Wave and Sit exercised in Play mode, with state advancement, bone motion and error capture. See `unity-play-validation.json`.
- All 1,633 pre-existing café objects retained their types, data names and transforms. Existing live project filepath and timeline frame preserved. Original source file was not overwritten; the updated café was saved separately.

Machine-readable evidence: `validation.json`, `animation-audit.json`, `fbx-validation.json`, `unity-validation.json`, `unity-play-validation.json`, `cafe-validation.json`, `asset-manifest.json`. Reproducible creation, rendering and validation scripts are under `Work/`.

## Limits

This is a stylized real-time interpretation of the reference. Curl forms, knit texture and shoe details are simplified; the renders show the actual fidelity. There are no facial blendshapes or individual finger bones. Extreme poses and third-party retargeted clips can need further weight tuning. The sitting pose needs placement adjustment for a specific chair. Device performance, mobile suitability and a browser build have not been profiled or validated for this new asset. No claim of complete production art approval is implied by the automated checks.

At the original asset handoff, nothing was committed or published. The later repository import includes these reusable sources; see ../../Docs/REPOSITORY_GUIDE.md.
