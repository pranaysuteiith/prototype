"""Check portable documentation, key source files and source inventory."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    for name in ['Assets/Scenes/GetStarted_Scene.unity', 'Packages/manifest.json',
                 'ProjectSettings/ProjectVersion.txt', 'Blender/Environment/doro-style.blend']:
        if not (ROOT / name).is_file():
            errors.append(f'Missing source: {name}')
    documents = [ROOT / 'README.md', ROOT / 'CONTRIBUTING.md', *ROOT.joinpath('Docs').glob('*.md'),
                 ROOT / 'Docs/Doro-Project-History/README.md']
    for document in documents:
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', document.read_text()):
            target = target.strip('<>').split('#')[0]
            if not target or re.match(r'[a-zA-Z]+:', target):
                continue
            if not (document.parent / unquote(target)).exists():
                errors.append(f'{document.relative_to(ROOT)}: broken link {target}')
    for item in json.loads((ROOT / 'Docs/important-files.json').read_text())['files']:
        path = ROOT / item['path']
        if not path.is_file() or path.stat().st_size != item['bytes']:
            errors.append(f'Inventory mismatch: {item["path"]}')
    for path in ROOT.rglob('*'):
        if '.git' in path.relative_to(ROOT).parts:
            if path.name == '.git' and path != ROOT / '.git':
                errors.append(f'Nested Git repository: {path.relative_to(ROOT)}')
            continue
        if path.name in {'Library', 'node_modules', '__pycache__'} or path.name == '.env':
            errors.append(f'Unexpected generated/private path: {path.relative_to(ROOT)}')
    print(json.dumps({'passed': not errors, 'errors': errors}, indent=2))
    return not errors


if __name__ == '__main__':
    sys.exit(0 if check() else 1)
