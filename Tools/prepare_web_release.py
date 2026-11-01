"""Stage the Doro shell with an explicitly supplied gzip Unity WebGL build."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 25 * 1024 * 1024


def stage(build, output, chunk_mib=14):
    build, output = Path(build).resolve(), Path(output).resolve()
    chunk_size = int(chunk_mib * 1024 * 1024)
    if not 0 < chunk_size < LIMIT:
        raise ValueError('Chunk size must be greater than zero and below 25 MiB')
    if output.exists():
        raise FileExistsError(f'Refusing existing output: {output}')
    if build == output or build in output.parents or output in build.parents:
        raise ValueError('Build and output directories must be separate')
    def one(pattern):
        files = list(build.rglob(pattern))
        if len(files) != 1:
            raise ValueError(f'Expected one {pattern}, found {len(files)}')
        return files[0]
    data = one('*.data.unityweb')
    framework = one('*.framework.js.unityweb')
    wasm = one('*.wasm.unityweb')
    loader = one('*.loader.js')
    raw = data.read_bytes()
    for asset in [data, framework, wasm]:
        with gzip.open(asset, 'rb') as stream:
            magic = stream.read(4)
            if asset == wasm and magic != b'\x00asm':
                raise ValueError('Invalid WASM signature')
            while stream.read(1024 * 1024):
                pass  # Validate gzip CRC, including the full scene stream.
    digest = hashlib.sha256(raw).hexdigest()
    release = 'r-' + digest[:16]
    shutil.copytree(ROOT / 'Sites/doro-cafe/dist', output, ignore=shutil.ignore_patterns('game'))
    target = output / 'game/Build' / release
    target.mkdir(parents=True)
    config = {'release': release, 'dataBytes': len(raw), 'dataSHA256': digest}
    for key, file in [('loaderUrl', loader), ('frameworkUrl', framework), ('codeUrl', wasm)]:
        shutil.copy2(file, target / file.name)
        config[key] = (target / file.name).relative_to(output).as_posix()
    config['dataParts'] = []
    for index, start in enumerate(range(0, len(raw), chunk_size)):
        part = target / f'scene.data.part{index:02d}.bin'
        part.write_bytes(raw[start:start + chunk_size])
        config['dataParts'].append(part.relative_to(output).as_posix())
    streaming = list(build.rglob('StreamingAssets'))
    if len(streaming) > 1:
        raise ValueError('Multiple StreamingAssets directories')
    if streaming:
        shutil.copytree(streaming[0], output / 'StreamingAssets')
    (output / 'build-config.json').write_text(json.dumps(config, indent=2) + '\n')
    oversized = [p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and p.stat().st_size >= LIMIT]
    if oversized:
        raise ValueError(f'Assets exceed hosting limit: {oversized}')
    print(json.dumps(config, indent=2))
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--chunk-mib', default=14, type=float)
    args = parser.parse_args()
    stage(args.build_dir, args.output_dir, args.chunk_mib)
