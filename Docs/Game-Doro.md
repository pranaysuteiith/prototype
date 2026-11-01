# Game Doro Documentation

Product brief and engineering guide · 1 November 2026

Repository: [pranaysuteiith/prototype](https://github.com/pranaysuteiith/prototype). Published prototype: [Doro Café](https://doro-quiet-cafe.shrewdmoss10.chatgpt.site).

## 1) Introduction: what is Doro?

Doro is a calm, miniature virtual café where builders can settle into focused work. Its intended experience pairs a cozy, explorable space with a practical work loop: choose a goal, reserve a time block, work alongside others, finish with a short progress check-in and earn recognition.

The existing prototype supplies the setting: a cream café with a green striped awning, a crossroads, trees, terrace furniture, bicycles, small vehicles, static customers, a looping dancer and a playable green-sweater character. Camera orbit/pan/zoom, dynamic depth of field and birds/park/distant-bark ambience make the space feel welcoming.

**Implementation boundary:** the current release is an environment and movement prototype. It has no focus timer, account system, networked co-working room, reward wallet or live presentation board. The sections below describe the intended product alongside the existing foundation. See [feature status](FEATURE_STATUS.md).

## 2) Who is the game for?

Doro is for builders and productivity workers: software developers, designers, vibe coders, founders, independent makers and people building a technology project or business. They want the motivation of a shared workspace while retaining the quiet and autonomy needed for deep work.

Core needs are a clear work intention, a protected focus interval, visible but non-intrusive company, an honest record of completed work and a place to share what was built. The default atmosphere should support concentration rather than require constant chat, avatar micromanagement or competitive grinding.

Example journey: a builder arrives to work on a prototype, writes “finish the login flow,” starts a focus block at a café seat, sees that other builders are focusing too, and returns at the break to share a small outcome. That journey is the product target, not an already-working multiplayer demo.

## 3) Game mechanics: time blocking, deep work and accountability

The planned loop is **arrive → set an intention → choose a block → focus → check in → take a break or continue**. A builder should be able to choose the duration, see the remaining time, cancel or finish intentionally, and review recent blocks.

Real-time accountability means other authenticated builders are actually connected to a shared café room and their status updates are synchronized. Static café customers and the dancer do not fulfill this requirement. Proposed shared states include available, focusing, on break and presenting. During focus, messaging and movement prompts should stay quiet; conversation belongs at the user's chosen break.

The first timer milestone can be single-user, but should be labeled local-only. The shared version needs room membership, reconnect behavior, server timestamps and persistence. Being connected cannot prove that a person did productive work; completion and progress notes are self-reported. See [the mechanics and service design](PRODUCT_MECHANICS.md).

## 4) Completed blocks give coins and XP

The proposed reward rule is that an eligible completed focus block earns coins and XP. Together these form social currency: acknowledging effort, unlocking café expression and encouraging builders to return.

Suggested uses include buying a coffee for an avatar, decorating a desk, sending a supportive reaction, or earning a presentation/celebration opportunity. The spend catalog, reward rates and eligibility thresholds are design choices to validate. A possible first iteration spends coins while XP represents accumulated recognition; if XP is also spendable, it must have explicit debit rules. No exchange rate or economy is finalized in this repository.

Rewards should reinforce consistent work without making the café a leaderboard grind. Completion grants need an idempotent, server-owned ledger so reconnects or duplicate requests cannot mint rewards twice. The current prototype has no coin balance, XP balance or spending implementation. [Detailed design](PRODUCT_MECHANICS.md#rewards-and-social-currency).

## 5) A public social board for builders' presentations

The planned café board showcases projects and work in progress. A builder can publish a project title, short description, creator name, optional link, current milestone and an invitation such as “feedback welcome” or “demo at the next break.” Presentations can later have a scheduled slot and an optional join action.

An initial board should be a readable UI opened from a recognizable object in the café, with a list of project cards and a detail view. Text should remain UI data, not be baked into textures. Posting is opt-in: private focus intentions must not automatically appear on a public board. Editing/removal, safe links, reporting and moderation are part of a usable shared board.

The existing decorative coffee sign/sandwich board is not this feature. There is no public-post database or presentation scheduling backend yet. [Board design and acceptance criteria](PRODUCT_MECHANICS.md#builder-showcase-board).

## 6) Set up Codex + Blender and Codex + Unity

[Codex + Blender](CODEX_BLENDER.md) explains the direct CLI route, an optional MCP connection, a non-destructive probe, source-file organization, backups and visual/rig inspection. It uses the recovered environment and character scripts as examples while identifying historical absolute paths and scene-clearing bootstrap code.

[Codex + Unity](CODEX_UNITY.md) covers the pinned Editor version, the installed `com.unity.pipeline` package, explicit project targeting, live command discovery, compilation, scene preservation, material/Avatar checks and WebGL builds. [General setup](SETUP.md) covers cloning and fetching LFS assets first.

Codex is the agent coordinating local tools. Blender authors geometry/materials/rigs; Unity supplies the current runtime. A connected agent or a successful script is not proof that meshes, deformations or gameplay are correct: inspect renders, run Play-mode checks and save evidence.

## 7) If not Unity: Blender + Codex + another engine

Blender remains the authoring tool. For a non-Unity runtime, the recommended starting investigation is Godot with glTF/GLB assets and GDScript, especially if browser export is required. A browser-native Babylon.js application is another route for a web-focused team comfortable owning more UI/networking integration.

Codex can create the engine project, import assets, implement character movement, collisions, camera control, UI and service integration. It does not make Blender itself the production game runtime. Unity materials, C# components, Avatar configuration and scene files do not transfer automatically; only suitable assets and design rules can be reused. There is no port in this repository. [Migration guide](ALTERNATIVE_ENGINES.md).

## 8) Visual style → 3D → game environment, physics and interaction

Begin with a style reference, extract camera/palette/proportion/material rules, and generate consistent building turnarounds and T-pose character sheets. Then choose manual/procedural Blender modeling or an optional image-to-3D blockout tool. Both paths require topology, UV, scale and silhouette inspection.

Use Blender to build the café, vegetation, props and rigs; retain a reusable master and export only the intended collections. Keep painted textures sharp. Rebuild engine-compatible materials, lighting and runtime depth of field rather than treating a blurred image or a Blender shader graph as portable gameplay.

Add simplified collision and explicit interaction affordances in the engine. In this prototype, focus triggers and walking collision are distinct systems. The next social board, seats and work stations should similarly have clear trigger/UI behavior and acceptance tests. [Visual production guidelines and prompts](VISUAL_PIPELINE.md).

## 9) Simple tools for 3D generation and rigging

Assuming “trip” means **Tripo AI**, use Tripo as an optional accelerated character/blockout and auto-rigging route, Blender for cleanup and weight correction, and Mixamo for a convenient humanoid rig/motion workflow. Preserve an unmodified source before each conversion, and inspect shoulders, elbows, hips, knees, ground contact and oversized heads after every transfer.

A downloaded rigged FBX is not automatically a valid Unity Humanoid Avatar. Check mapping in Unity, and test the actual target engine. The supplied Belly Dance file has a `mixamo.com` take; the complete intermediate service workflow was not recovered. The existing green-sweater boy was constructed programmatically in Blender, not demonstrated as a Tripo generation. [Practical tool guide](CHARACTER_TOOLS.md).

## 10) Repository, usage and important files

Clone [this repository](https://github.com/pranaysuteiith/prototype) with Git LFS, then open its root in Unity Hub. `Assets/Scenes/GetStarted_Scene.unity` is the current map. The custom runtime code is in `Assets/DoroPainted/Scripts`; Blender sources are in `Blender/` and `Characters/Boy_GreenSweater/`; the browser shell is in `Sites/doro-cafe/`.

The [repository guide](REPOSITORY_GUIDE.md) maps the important files, authoring scripts, historical tests and code inventory. The [build guide](BUILD_AND_DEPLOY.md) explains the separate WebGL and hosting steps. [Verification](VERIFICATION.md) records what was checked, and [the history](Doro-Project-History/README.md) explains how the project evolved.

The repository intentionally excludes generated caches, duplicate backups and compiled distributions. Recreate them from source; a source push does not automatically deploy the game. [Contributing](../CONTRIBUTING.md) explains the branch/review workflow and when documentation/status must change.
