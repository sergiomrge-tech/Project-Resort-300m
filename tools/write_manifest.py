"""Record distributable project bytes; never includes Unity-generated caches."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'Library','Logs','Temp','UserSettings','obj','BuildCache'}
files = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (ROOT / 'UnityProject').rglob('*')
         if p.is_file() and not any(x in p.parts for x in IGNORED)}
(ROOT / 'evidence/files_sha256.json').write_text(json.dumps(files, indent=2)+'\n')
print(f'Hashed {len(files)} project files')
