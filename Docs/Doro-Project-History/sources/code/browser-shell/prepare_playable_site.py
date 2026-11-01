from pathlib import Path
import json,hashlib,shutil,gzip
root=Path('/Users/pranay/My project');build=root/'BuildArtifacts/DoroWebGL-PlayableBoy/Build';site=root/'Sites/doro-cafe/dist'
files=list(build.glob('*'));data=next(p for p in files if p.name.endswith('.data.unityweb'));wasm=next(p for p in files if p.name.endswith('.wasm.unityweb'));framework=next(p for p in files if p.name.endswith('.framework.js.unityweb'));loader=next(p for p in files if p.name.endswith('.loader.js'))
payload=data.read_bytes();sha=hashlib.sha256(payload).hexdigest();release='r20261028-'+sha[:10];old=site/'game'
# Generated public build outputs are versioned in the Site repository; replace them together.
if old.exists():shutil.rmtree(old)
dest=old/'Build'/release;dest.mkdir(parents=True)
for p in [wasm,framework,loader]:shutil.copy2(p,dest/p.name)
parts=[];chunk=14*1024*1024
for i,offset in enumerate(range(0,len(payload),chunk)):
 name='scene.data.part%02d.bin'%i;(dest/name).write_bytes(payload[offset:offset+chunk]);parts.append(str((dest/name).relative_to(site)))
rebuilt=b''.join((site/p).read_bytes() for p in parts);assert hashlib.sha256(rebuilt).hexdigest()==sha
# Confirm the scene stream and executable are valid gzip streams before publishing.
assert len(gzip.decompress(payload))>len(payload)
assert gzip.decompress(wasm.read_bytes())[:4]==b'\0asm'
config=dict(loaderUrl=str((dest/loader.name).relative_to(site)),frameworkUrl=str((dest/framework.name).relative_to(site)),codeUrl=str((dest/wasm.name).relative_to(site)),dataParts=parts,dataBytes=len(payload),dataSHA256=sha,release=release)
(site/'build-config.json').write_text(json.dumps(config,indent=2)+'\n')
(old/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../"><title>Doro Café</title><a href="../">Open Doro Café</a>')
for path in site.rglob('*'):
 if path.is_file():assert path.stat().st_size<25*1024*1024,(path,path.stat().st_size)
(root/'BuildArtifacts/playable-site-package-check.json').write_text(json.dumps(dict(release=release,sceneDataSHA256=sha,compressedSceneBytes=len(payload),chunks=len(parts),allFilesUnder25MiB=True,wasmValid=True),indent=2))
print(json.dumps(config,indent=2))
