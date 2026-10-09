"""Export only Unity-measured dependency closure from the temporary bake."""
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[1]
source = root / '.work/BakeProject'
target = root / 'UnityProject'
for folder in ('Packages', 'ProjectSettings'):
    shutil.copytree(source / folder, target / folder, dirs_exist_ok=True)
paths = (root / 'evidence/export_paths.txt').read_text().splitlines()
import re
source_guids = {}
for meta in (source / 'Assets').rglob('*.meta'):
    match = re.search(r'^guid: ([a-f0-9]{32})$', meta.read_text(), re.M)
    if match:
        source_guids[match[1]] = meta.with_suffix('').relative_to(source).as_posix()
for path in paths:
    source_path = path
    if not (source / source_path).is_file():
        # QA may rename historical labels while retaining the asset GUID.
        meta = target / (path + '.meta')
        match = re.search(r'^guid: ([a-f0-9]{32})$', meta.read_text(), re.M)
        source_path = source_guids[match[1]]
    for suffix in ('', '.meta'):
        src = source / (source_path + suffix)
        if not src.is_file():
            raise RuntimeError(f'Missing exported file {src}')
        dst = target / (path + suffix)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    parent = Path(path).parent
    while str(parent) != 'Assets':
        meta = source / (str(parent) + '.meta')
        if meta.is_file():
            shutil.copy2(meta, target / (str(parent) + '.meta'))
        parent = parent.parent
print(f'Exported {len(paths)} local dependencies')
