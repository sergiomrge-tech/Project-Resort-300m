"""Export only Unity-measured dependency closure from the temporary bake."""
from pathlib import Path
import shutil
root = Path(__file__).resolve().parents[1]
source = root / '.work/BakeProject'
target = root / 'UnityProject'
for folder in ('Packages', 'ProjectSettings'):
    shutil.copytree(source / folder, target / folder, dirs_exist_ok=True)
paths = (root / 'evidence/export_paths.txt').read_text().splitlines()
for path in paths:
    for suffix in ('', '.meta'):
        src = source / (path + suffix)
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
