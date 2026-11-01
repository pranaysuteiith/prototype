# Codex + Blender

## Direct local CLI route

[Official Codex CLI documentation](https://learn.chatgpt.com/docs/codex/cli) describes installation/sign-in and running Codex inside a project directory. Start it in the cloned repository with `codex`; it can inspect files and run installed local tools. Keep local account/config files outside Git.

Install Blender from [blender.org](https://www.blender.org/download/), then verify its actual executable. On the authoring Mac:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --version
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python Tools/blender_probe.py
```

The probe only prints version/scene information from a separate factory-startup process. It does not open or save the Doro master. It is included to verify that Codex's shell can execute Blender, not to demonstrate asset quality. [Blender command-line reference](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html).

For inspection of an existing source, pass its path explicitly and use a read-only script. For modeling, work on a copy or an isolated process and save into a new output folder. A useful starting prompt is:

> Read the repository README and Blender source guide. Identify the file and scene before changes. Back it up, preserve existing objects, and create a separately named collection. Use Blender Python to make the requested geometry, inspect renders and deformations, and save/export actual files. Report measured counts and unresolved problems; do not stop at a script.

## Optional Blender MCP route

The historical workflow also used a live Blender MCP connection. This repo does not distribute a Blender MCP server/add-on. Install a connector from its maintainer's documented source, enable its Blender add-on/server, and configure that connector in the Codex surface you use. Its launch command, transport and port depend on the connector; do not copy an invented universal port.

The [official MCP configuration guide](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) documents CLI and desktop configuration. A STDIO configuration has the general shape `codex mcp add blender -- <your-installed-server-command>`; replace the placeholder with the connector's documented command. Use `codex mcp list` or the client's MCP UI to verify it, then ask for read-only version/project/scene information before executing modeling code.

A server being configured does not prove Blender is connected. A successful geometry script does not prove the result resembles a reference. Prefer direct CLI work when a live connector is unavailable; do not expose a local control server publicly just to make it reachable.

## Files and execution boundaries

- `Blender/Environment/doro-style.blend`: environment source.
- `Blender/Environment/Scripts/`: six staged historical environment generators.
- `Blender/FemaleCharacter/`: earlier female source/rig/actions and scripts.
- `Characters/Boy_GreenSweater/Blender/Boy_GreenSweater.blend`: reusable boy.
- `Characters/Boy_GreenSweater/Work/`: boy creation, rendering, UV/export and audit scripts.

The historical generators contain absolute authoring-Mac paths. Update their input/output constants in a working copy before replaying. Environment `build_scene.py` clears the active scene after saving a backup; run bootstrap work only in an isolated process, never against a finished live scene. Scripts reconstruct authored geometry and may overwrite their configured exports.

## Model, rig, inspect, export

Use Z-up and a consistent meter scale in Blender. Name collections/parts, preserve a symmetrical T-pose as rest pose, bind deforming geometry and keep appropriate accessories rigid to Head. Check shoulders/elbows/hips/knees, sole contact, topology, UVs and weight normalization.

Generate sharp turnarounds and pose previews. Fix visible gaps/intersections, not just exceptions. Export selected assets with meshes, skeleton and intended animation takes, no unrelated café helpers or unnecessary leaf bones. Reopen the exported file before calling it done, then validate its rig in the target engine. Blender-specific node graphs, constraints and procedural effects need baking or replacement.

The present source records actual checks; see [VERIFICATION.md](VERIFICATION.md) and the character audit JSONs. They do not establish every third-party animation or every extreme pose.
