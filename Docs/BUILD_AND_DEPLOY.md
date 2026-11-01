# Build and deployment

The repository contains the editable Unity project and browser shell source, not compiled browser distributions. GitHub source publication and the existing public website are separate operations.

## Unity WebGL build

Install the matching WebGL module, open this checkout and save the scene/assets. Discover commands on the installed CLI before using this historical command shape:

```bash
DORO_PROJECT="$(pwd)"
unity command --project-path "$DORO_PROJECT" --query 'build run'
unity command build run --project-path "$DORO_PROJECT" --json -- --target WebGL --outputPath BuildArtifacts/DoroWebGL --scenes '["Assets/Scenes/GetStarted_Scene.unity"]' --confirm true
unity command build status --project-path "$DORO_PROJECT" --json
```

The build is asynchronous. Wait for a completed successful BuildReport, not just “queued.” If an Editor is running another checkout, do not build through it. Keep the package versions and scene references intact.

The historical distribution uses gzip compression plus decompression fallback. The WebGL/mobile quality preset has linear upscaling and depth texture support, and camera post-processing remains enabled. Inspect warnings and runtime output; the last recorded build had zero errors but retained package shader/future collider pre-baking warnings.

## Prepare a local browser distribution

The portable helper creates a staging directory by combining the shell and the new generated build. It splits large compressed scene data into host-sized chunks, uses content-versioned paths and records SHA-256. It expects this project's gzip `.unityweb` output.

```bash
python3 Tools/prepare_web_release.py --build-dir BuildArtifacts/DoroWebGL --output-dir BuildArtifacts/SitePreview
python3 -m http.server 8080 --directory BuildArtifacts/SitePreview
```

Open http://localhost:8080, choose Enter the café and click the canvas. Test visible characters, walking/turning/idle, camera follow/orbit/pan/zoom, sound/mute and blur. Check the browser Console. Stop the server when finished. The helper refuses an existing output directory; choose a fresh staging path for a new build.

`Sites/doro-cafe/dist/build-config.json` in source documents a historical release. The referenced compiled game files are deliberately absent from Git. Running the source shell alone will therefore not load a game until it is paired with a build.

## Publish

The original game is hosted at https://doro-quiet-cafe.shrewdmoss10.chatgpt.site . `Sites/doro-cafe/.openai/hosting.json` preserves that Site's identity for the owner; it is not a credential or a generic destination for forks. Publish through an authorized Sites workflow with a matching source revision and generated archive, retaining the intended audience.

For a different static host, deploy the complete staging output and check its asset-size/MIME/compression behavior. The current loader reconstructs scene bytes from chunks; do not upload only index.html or rename one build file without updating its matching configuration.

There is no GitHub Actions deployment integration in this repository. A `git push` does not rebuild Unity or change the public game. No new website deployment is part of the source-import/documentation commit.
