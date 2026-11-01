# A non-Unity route

**Architecture guidance, not an implemented port.** The reusable part is Blender art plus the product design. A new engine still needs its own movement, physics, camera, UI, audio, focus effect and service integration.

## Blender + Codex + Godot

Godot is a reasonable first alternative for a small team wanting an editor, scene system, scripting and a browser-export path. Prefer explicit glTF 2.0/GLB exports from Blender for a reproducible asset handoff. Godot also imports `.blend` by calling installed Blender, but explicit exports avoid an unnoticed local dependency. [Official format/import documentation](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html).

Suggested migration sequence:

1. Export the café and boy as GLB assets in a new folder; include UVs, PBR textures, skinning and baked actions. Reopen the files and measure scale/axes.
2. Create a separate Godot project. Use inherited scene wrappers for imported art so reimport does not erase gameplay additions.
3. Add a `CharacterBody3D` controller, simplified static collision and an animation state machine for idle/walk. Reimplement camera-relative arrows and follow/orbit, rather than expecting Unity C# or CharacterController settings to transfer.
4. Add a quiet UI for timer/intention and future board interactions. Keep service/network contracts independent from the render engine.
5. Rebuild lighting/materials and an appropriate focus treatment. Do not assume Unity's URP Volume or Blender shaders survive import.
6. Profile an exported scene in the target browser before moving the entire map.

For Godot 4 web targets, current official documentation calls for the Compatibility renderer and WebGL 2.0; it also records a C# web-export limitation. Use GDScript for this proposed browser route and recheck the selected release's constraints. Single-threaded export is a useful starting point when avoiding the additional hosting requirements of threaded exports. [Official web export guide](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html).

Codex can author project files/scripts and run Godot's CLI. Example command shapes after a project/preset exists:

```bash
godot --headless --path /absolute/godot-project --editor --import
godot --headless --path /absolute/godot-project --export-release Web /absolute/output/index.html
```

The export templates, named preset and destination directory must exist. Verify flags against `godot --help`. [Official CLI guide](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).

## Blender + Codex + Babylon.js

For a browser-first product where the team prefers TypeScript and conventional web UI, Babylon.js is another option. Export GLB art, load it into the scene, bind baked animation groups, implement the avatar/camera loop and use a physics integration such as Babylon's Havok plugin where required. Havok initialization and its WASM asset deployment are part of that setup. [Official Havok integration](https://doc.babylonjs.com/features/featuresDeepDive/physics/havokPlugin/).

This route can make HTML forms, timers and public project cards easier to compose with web UI, but the team owns more integration work. Physics, navigation, asset streaming, accessibility and real-time presence still need deliberate implementation and tests. Keep dependencies and production-hosted assets pinned; do not treat a learning CDN example as a finished release pipeline.

## What transfers and what must be rebuilt

Meshes, UVs, textures, skeletons, baked clips, scale conventions and design references can transfer after validation. Unity scenes/prefabs, C# gameplay, Animator Controllers, Humanoid Avatar settings, URP materials/Volumes and Pipeline automation do not transfer directly. Exact visual parity and smooth retargeting need inspection.

Blender authors the art; it does not replace the runtime engine here. Creating a custom renderer/game engine is possible software work but is a separate, much larger project than porting this café. Start with a single validated scene and controller before deciding to migrate Doro. Neither recommendation implies a tested Godot or Babylon build is present.
