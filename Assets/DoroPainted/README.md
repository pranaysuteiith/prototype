# Doro Painted Café import

Imported on 26 October 2026 into `/Users/pranay/My project`, Unity 6000.6.7f1, existing URP PC pipeline. Active scene: `Assets/Scenes/GetStarted_Scene.unity`.

## Controls

Play: WASD or arrow keys pan; hold middle or right mouse and drag to pan; wheel dollies the camera; hold Q to orbit left or E to orbit right (60 degrees/second, adjustable with Rotation Speed in the camera Inspector). B toggles depth of field. The camera Inspector's `DoroCenterFocus.depthOfFieldEnabled` also disables blur for performance. Runtime focus uses the center ray, dedicated trigger proxies, camera-forward depth, exponential smoothing, and a ground-plane fallback.

Camera starts at (26, 29, 34), aimed at (-1.1, 2.2, -0.2), perspective vertical FOV 19.157 degrees. The camera renders layer 31 exclusively; existing starter-scene objects and scripts remain active but are excluded from this café view. No existing camera rig was present.

## Changes

- Kit copied directly into this directory. No finalized Unity package was needed.
- Original supplied FBX batches inconsistent UV layer names; neither simply using UV0 nor swapping UV channels preserves every surface. The project FBX was regenerated from the supplied blend, keeping each object's original active render UV values and normalizing their layer names before joining into 28 meshes. `AgentScripts/normalize_doro_export.py` records that correction. The original source folder and blend remain untouched.
- Source FBX reported 473,636 triangles. The normalized export from the saved blend imports as 472,140 triangles and 1,175,933 vertices in 28 meshes. This is a re-export, not a simplification pass.
- Seven URP Lit materials rebuilt and persistently remapped in the FBX importer: painted atlas, five used foliage swatches, warm emissive glazing. All six supplied foliage textures remain available. Textures retain full resolution, mipmaps, anisotropic filtering and uncompressed painted detail.
- Single scene root: `Doro Painted Cafe - Imported`. Dedicated camera, Volume, focus marker and 37 simple trigger boxes live under this root. Tree canopies and trunks have separate coarse proxies; café proxy follows its shell instead of enclosing the terrace furniture. No per-leaf or mesh colliders.
- Supplied Editor script adapted into `Doro/Import Into Current Scene`; it never creates an empty scene. Existing scene objects, scripts and render-pipeline assets are preserved.
- Bokeh DOF, aperture 1, artistic focal length 300 mm, smoothed runtime focus; SMAA; neutral tonemapping. Blur is deliberately a runtime effect, not painted into textures.
- Camera-scoped studio light/ambient adjustment restores the prior sun and ambient probe after rendering, including when disabled. Existing scene RenderSettings remain serialized unchanged. Native FBX orientation and positive unit root scale are retained; requested camera coordinates are honored. This composition and URP lighting differ from the Blender reference, whose art-directed f/0.045 blur is stronger than URP's standard Bokeh range.

## Verification

`DoroBackups/2026-10-26/play-verification.json` records 22 integration checks using actual queued Input System events and live physics in Play mode: all WASD/arrow directions, both mouse buttons, wheel zoom, focus on café/tree/furniture/road, convergence to camera-forward hit depth, ground fallback, B blur toggle, supported materials, simplified trigger colliders, advancing frames, existing pickup animation and collection via a temporary Player-tagged physics object. The temporary objects and collection are reverted when leaving Play mode. No active third-person player rig was present, so locomotion/respawn was not exercised.

`DoroBackups/2026-10-26/scene-preservation.json` compares all original serialized scene blocks against the pre-import backup. None were removed or changed except the SceneRoots list, which includes the new root. The original 32 GameObjects are preserved. Final Console checks report no errors or warnings.

ProfilerRecorder measured the Mac Editor at PC quality, 2070×1271 on Apple M2, over 180 frames each with blur on/off: 97.3 FPS / 10.23 ms main thread with blur, and 110.1 FPS / 9.03 ms without. Editor totals were 216 versus 211 draw calls. These measurements include Editor/Scene View overhead and shadow passes; they are not isolated player-build or mobile measurements. Render-thread timing was unavailable. Detailed counts and timings are in the verification JSON. The high vertex count, foliage geometry and Bokeh require device profiling and likely LOD/vertex reduction before calling this mobile-ready. Touch support is included in the supplied navigation script but was not tested on a touch device.

Unity Game View screenshots are in `VerificationScreenshots/Doro-final-play.png` (live screen capture) and `Doro-final-camera.png` (1600×900 camera render).

Q/E orbit was subsequently verified with eight additional Play-mode checks (left/right direction, pivot/radius/height preservation, center aim, simultaneous-key cancellation, pan, wheel zoom and autofocus after rotation). Results: `DoroBackups/2026-10-26/orbit-verification.json`.

## Undo or restore

Exit Play mode, then use **Doro → Remove Imported Cafe (Undoable)** and save. Alternatively delete the single `Doro Painted Cafe - Imported` root. This restores the original scene hierarchy; imported assets may remain for reuse. The menu removal participates in Unity Undo.

For a complete scene restore, the untouched pre-import scene copies are:

- `DoroBackups/2026-10-26/GetStarted_Scene.live-before.unity`
- `DoroBackups/2026-10-26/GetStarted_Scene.disk-before.unity`

With Unity out of Play mode, copy the chosen backup over `Assets/Scenes/GetStarted_Scene.unity` (keep the existing scene .meta), then reload that scene. Once the root has been removed, `Assets/DoroPainted` may also be removed to discard the imported kit and its screenshots. No commits or publishing were performed.


## Calm ambience and browser release

Added `DoroAmbientSound` to the import root: a seamless 59-second CC0 park/bird loop, four-second fade-in, and soft dog barks every 35–65 seconds (first bark after 18–28 seconds). M mutes; volumes and bark timing are adjustable in the Inspector. Credits are in `Audio/CREDITS.md`. The clips are included in the Unity scene.

`Sites/doro-cafe` is a separate public Site distribution, built from this existing scene as Unity WebGL. The page provides sound, volume, soft focus, fullscreen and a copy-link button. Browser audio may need a click inside the canvas after loading. WebGL settings use gzip decompression fallback (compatible with static hosting), 256 MB initial / 1024 MB maximum memory, and asset caching. The prior scene and settings were copied to `DoroBackups/2026-10-26/before-ambience-browser` before these changes. No Blender sources or Editor backups are uploaded to the public Site.

Public game: https://doro-quiet-cafe.shrewdmoss10.chatgpt.site . Version 1 published successfully; hosted WebGL rendering and sound toggle verified. Browser download is approximately 46 MB plus the page/poster. Original compilation returned 360 warnings (primarily existing Sentis/AI shader variants), with zero build errors. The browser reported a non-fatal URP FSR-upscaling shader warning while the scene and depth of field rendered correctly. Desktop browser tested; mobile remains unprofiled. Unity's local audio-device initialization problem was recovered with AudioSettings.Reset; the final fresh Play-mode check passed birds looping, bark playback, volume, mute, and decoded clip signal.
