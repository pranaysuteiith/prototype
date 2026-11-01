# Visual references → 3D → gameplay

## Establish a style contract

Keep a reference board and write down camera direction/projection, building proportions, character scale, palette, outline hierarchy, material roughness, lighting direction and focus behavior. Use named rules instead of “make it similar.” Doro's visual anchors are cream walls, green stripes, warm windows, timber, layered foliage and miniature proportions.

A reusable image prompt can state:

> Create a cohesive miniature café street using the supplied reference for visual style. Keep the camera and scale consistent. Show the cream café, green striped awning, warm windows, timber, trees, terrace furniture, bicycles and small vehicles. Produce a sharp scene reference and a separate focus study; keep details readable. Provide separate building turnarounds and uncluttered asset sheets. Characters need a full-body symmetrical T-pose, arms horizontal and palms down.

This is a reusable template, not a claim about the hidden exact prompt/settings of every historical generation. The recovered image conversation is linked in [the history](Doro-Project-History/README.md). Generated sheets are visual references, not dimensionally exact orthographic blueprints.

## Choose how to build geometry

For controlled style and reproducibility, model manually or through Blender Python: primitives, beveled architecture, custom curves/meshes, continuous clothing surfaces and organized collections. For a faster blockout, an image-to-3D tool such as Tripo is optional; inspect silhouette/topology before treating its output as final. An attractive reference does not itself provide a rig, UVs or collision.

Use one unit convention. The current Blender source is Z-up and uses meters; the characters face -Y. Place feet at the ground and the root between them. Create modifiers/instances only where their export behavior is understood. Preserve the editable authoring scene while evaluating copies for batching/export.

## Texture and material discipline

Keep base textures sharp. Doro uses a procedural painted atlas and separate leaf swatches to avoid pale atlas bleed in mipmaps. Keep a single consistent render UV channel before joining meshes; the original import needed that repair. Inspect normal-map color space and base-color tint, not just the material name.

Bake or replace shader graphs that cannot transfer. Recreate materials using the target engine's PBR inputs and inspect from several camera angles. Pink/missing materials are an import/configuration problem, not an art treatment. A Blender render and a runtime render need separate checks.

## Rig and animation handoff

Use a symmetrical T-pose as the rest pose. Test the oversized head, shoulders, elbows, hips and knees; correct weights after auto-rigging. Keep hair/glasses rigid to the head when appropriate. Validate idle/walk loops and soles, and keep locomotion clips in place if gameplay will move the root.

Export only the intended collection, with UVs, material textures, deformation bones and baked action ranges. Avoid unnecessary leaf bones and runtime-only reliance on Blender constraints. Reimport the file before engine integration; a successful export dialog is not validation.

## Engine environment, physics and interactions

Import into a named root in the existing scene and preserve its original systems. Rebuild camera/lighting/materials in the active pipeline. Use perspective or orthographic framing intentionally; Doro's final game uses a narrow perspective view, not a mathematically fixed isometric camera.

Separate the systems:

- Visible art renders the neighborhood.
- Walking collision blocks the controller and supplies ground/curbs.
- Focus triggers identify simplified subjects for depth of field.
- Interaction triggers identify seats, board, doors or work stations and open clear UI.

Do not use a giant tree-canopy box as a wall or put physical collision on every leaf. Test camera/render layers as well as physics layers; an otherwise valid imported character can be invisible to the map camera.

For a future board, define hover/focus/activate behavior and an accessible UI entry point. For a future seat, define approach/occupancy/cancel behavior and align the seated animation. These interactions are specifications until code and tests exist.

## Definition of done for an asset change

Inspect a sharp front/back/side/isometric view; measure scale/triangles; check UVs/materials; test rig poses/clips; reopen exports; inspect the target-engine render; test collisions/input and Console errors; save the scene/assets; record limitations. Profile the target build before claiming mobile readiness. Do not use heavy blur to conceal broken meshes or textures.
