# Playable boy in the café map

Saved scene: `Assets/Scenes/GetStarted_Scene.unity`.

Click Unity's Game view while Play mode is running. Use the four arrow keys to walk relative to the camera. The boy turns toward movement, transitions between Idle and Walk, follows gravity, steps onto curbs and collides with the imported road, café and terrace geometry. Walk speed is 1.25 world units/second. Diagonal input is normalized.

The existing Doro camera follows the player horizontally. WASD still pans, Q/E rotates, middle/right dragging pans and the wheel zooms. Arrow keys are reserved for the boy in this scene. The original camera component keeps `useArrowKeys = true` as its default for other scenes.

Scene hierarchy: `Doro Playable Boy` contains the player and dedicated walking colliders. The boy's visual remains an instance of the reusable character prefab. Existing map objects, the dancing girl and original gameplay objects are retained.

The camera renders layer 31, so character renderers use that existing layer. Walking physics use layer 28 (`DoroWalking`), and the CharacterController excludes other layers. This avoids the retained tutorial Ground collider, whose top is above the café map. Existing focus colliders remain triggers. The added collision meshes use streets, terrace and café geometry; simplified obstacle colliders cover other buildings, cars, people and tree trunks. Decorative foliage is not individually collidable. Four invisible boundary boxes keep the player inside the map.

Backup before adding the player: `GetStarted_BeforePlayableBoy.unity` in this folder. To revert, stop Play mode, remove the new `Doro Playable Boy` root and restore the camera from the backup, or restore the backed-up scene file. The old scene's camera settings have no follow target and retain arrow-key panning. No source Blender assets were modified.

Implementation: `Assets/DoroPainted/Scripts/DoroBoyWalker.cs`, plus the optional arrow-input and follow-target fields in `DoroPanZoom.cs`.

`play-test.json` records synthetic Input System arrow-key events exercised in actual Unity Play mode, walk/idle state checks, grounding, following, map boundary blocking and runtime error capture. `Unity_PlayableBoy.png` in the character Previews folder is rendered by the map camera.

The updated map was subsequently rebuilt for WebGL and published as version 2 at https://doro-quiet-cafe.shrewdmoss10.chatgpt.site. The existing public audience and URL were preserved. See Docs/Validation/2026-10-28-browser-deployment-v2.json in the repository root for deployment evidence. The Unity project had not been committed at that historical checkpoint; it is included in the later GitHub source import.
