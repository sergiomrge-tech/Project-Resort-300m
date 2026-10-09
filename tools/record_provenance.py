"""Record migration provenance from the temporary, read-only-source copy."""
import hashlib
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / '.work/BakeProject'
def guid(p):
    return re.search(r'^guid: ([a-f0-9]{32})$', p.read_text(), re.M)[1]
def clean(s):
    return re.sub(r'[^A-Za-z0-9_]', '_', re.sub(r'R\d+[_ ]?', '', s))
assets = {guid(p): p.with_suffix('') for p in (ROOT/'UnityProject/Assets').rglob('*.meta')
          if p.with_suffix('').is_file()}
temp_assets = {guid(p): p.with_suffix('') for p in (TEMP/'Assets/R15').rglob('*.meta')
               if p.with_suffix('').is_file()}
sources = re.findall(r'^\| `(Assets/[^`]+)` \|', (ROOT/'docs/DEPENDENCIES_BEFORE.md').read_text(encoding='utf-8'), re.M)
catalog = []
for path in sources:
    p = TEMP / path
    if not p.is_file():
        continue
    names = {clean(p.stem)}
    if p.suffix in ('.mat','.asset','.shader'):
        text = p.read_text(errors='replace')
        names.update(clean(x) for x in re.findall(r'^\s*m_Name: (.+)$', text, re.M))
        names.update(clean(x) for x in re.findall(r'Shader "([^"]+)"', text))
    catalog.append((path, p, names))
rows = ['destination\tdestination_guid\tsource_candidates\tsource_guids\tmatch']
for g, dest in sorted(assets.items(), key=lambda pair: str(pair[1])):
    if g not in temp_assets or dest.suffix == '.asset' and '/Meshes/' in dest.as_posix():
        continue
    origin = temp_assets[g]
    suffix = re.sub(r'^R15_\d{4}_', '', origin.stem)
    candidates = []
    method = 'original_object_name'
    if dest.suffix.lower() in ('.png','.jpg','.jpeg'):
        h = hashlib.sha256(dest.read_bytes()).digest()
        candidates = [(path,p) for path,p,n in catalog if p.suffix==dest.suffix and hashlib.sha256(p.read_bytes()).digest()==h]
        method = 'exact_source_bytes_sha256'
    else:
        candidates = [(path,p) for path,p,n in catalog if suffix in n and p.suffix==dest.suffix]
    rows.append('\t'.join([dest.relative_to(ROOT/'UnityProject').as_posix(),g,
                           '|'.join(path for path,p in candidates),
                           '|'.join(guid(Path(str(p)+'.meta')) for path,p in candidates),method]))
(ROOT/'evidence/provenance.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')
export = (ROOT/'evidence/export_paths.txt').read_text().splitlines()
mapped = []
for path in export:
    g=guid(TEMP/(path+'.meta'))
    mapped.append(assets[g].relative_to(ROOT/'UnityProject').as_posix())
(ROOT/'evidence/export_paths.txt').write_text('\n'.join(sorted(mapped))+'\n')
print(f'Recorded {len(rows)-1} asset provenance rows; texture matches use exact bytes')
