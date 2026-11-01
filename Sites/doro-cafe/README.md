> Repository source copy: compiled `dist/game` assets are excluded. Pair this shell with a fresh Unity WebGL build using [the portable staging helper](../../Tools/prepare_web_release.py). See [current build instructions](../../Docs/BUILD_AND_DEPLOY.md).

# Doro Café browser release

This folder contains only the public browser distribution and its hosting manifest. The Unity project and Blender source are kept outside this Site repository.

- `dist/index.html`, `style.css`, `app.js`: browser shell, entry/loading/error states, controls, volume, mute, blur, fullscreen and share-link action.
- `dist/game/`: Unity WebGL release built from the saved existing scene.
- `dist/build-config.json`: generated paths for the Unity loader, framework, WASM, and three scene-data chunks. The page reconstructs the exact compressed scene bytes in a temporary Blob URL to meet the hosting per-file limit. SHA-256 is recorded in the configuration.
- `dist/audio-credits.txt`: CC0 source credits.

The Unity scene's `DoroAmbientSound` component supplies the same park birdsong and occasional distant dog barks in the Editor and browser build. M toggles sound; B toggles depth of field. Browser autoplay restrictions may require clicking the game canvas after loading.

Controls: arrow keys walk the green-sweater boy, WASD pans, Q/E orbits, middle/right drag pans, wheel zooms. The camera follows the boy. Designed and tested for desktop browsers; mobile performance is not established.

The Site is public by the owner's request. No personal account data, source blend, Editor backups, or Unity source project are included in this repository.

The current release includes the rigged green-sweater boy with walking/idle animation and map collisions, the belly dancer, and the existing ambient birds and distant barks.

Browser compatibility: the existing mobile/WebGL URP preset uses linear upscaling and explicit depth texture support. Soft focus was visually checked on/off in the WebGL build. Unity still emits a non-blocking warning while creating an unused FSR material; the active linear upscaler and the depth-of-field effect render correctly. The build also retains package shader and future collider pre-baking warnings, with zero build errors. Desktop WebGL was checked; mobile is unverified.
