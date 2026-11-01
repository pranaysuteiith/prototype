# Simple character generation and rigging tools

“Trip” is interpreted here as **Tripo AI**. The following are optional production routes, not an assertion that Tripo created Doro's existing boy. Tool interfaces/plans can change; official sources were checked on 1 November 2026.

## Tripo: blockout/generation and auto-rigging

Supply a clear full-body character reference with separated limbs. Tripo's documented rigging workflow selects a character, a skeleton type/preset, generates the rig, previews joint motion and exports a rigged/animated FBX. Treat that export as a starting asset; inspect weights and correct them in Blender where needed. Its documentation explicitly calls out shoulders/hips/fingers as areas to inspect and describes static hair geometry. [Official rigging guide](https://www.tripo3d.ai/product-doc/module-post-processing/rigging-animation).

Use a new asset version rather than overwriting the master. After generation, measure triangle count, remove unnecessary/internal geometry, check symmetry, UVs, silhouettes and limb separation. The desired chibi head and short limbs can need substantial cleanup. Do not accept a “game-ready” label as proof that the asset meets this project's budget or deforms correctly.

## Mixamo: humanoid rig and motion clips

Adobe's workflow uploads FBX/OBJ/ZIP for an unrigged character, places joint markers and generates a rig. For an already-rigged character, upload FBX and inspect the resulting mapping. Apply a motion, preview and download the animated model; embed media when textures are needed. [Official Adobe guide](https://helpx.adobe.com/creative-cloud/help/mixamo-rigging-animation.html).

Keep a clean original and use the same base skeleton/scale for related clips. Check in-place versus moving-root behavior, frame rate, clip boundaries, loop seams, foot contact and root drift after import. The Doro dancer's supplied FBX has a `mixamo.com` take, but the exact external upload/retarget steps were not recovered.

## Blender: authoring and corrections

Choose manual/programmatic Blender work when the silhouette, continuous clothing geometry, naming and exact rig conventions matter. The boy in this repo is a 22-bone humanoid-compatible Blender rig with Idle/Walk/Run/Wave/Sit. The earlier female asset has 38 bones and three actions. They are separate assets and should not be silently overwritten by an auto-rig conversion.

Use automatic weights only as a starting point. Correct joint influence, preserve rigid accessories and test representative poses. Avoid merging the outfit, glasses and head into an uninspectable mass just to reduce the object list.

## Handoff checklist

1. Keep an untouched source version and a T-pose rest asset.
2. Inspect geometry and UVs before rigging.
3. Inspect elbows/shoulders/hips/knees and head stability after rigging.
4. Sample the chosen motion, feet and loop endpoints.
5. Reopen FBX/GLB with textures/weights/clips intact.
6. Validate in the actual engine; Unity Humanoid requires a valid Avatar and anatomical mapping, not just named bones.
7. Record the tool/source, exported asset version and applicable usage terms. A tool subscription is not a substitute for recording asset provenance.

The current models have simplified real-time curl/knit/shoe details. The boy has no individual finger bones or facial blendshapes. Extreme poses and third-party motions need additional checks.
