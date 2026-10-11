from pathlib import Path
import json,hashlib,shutil,struct,datetime
root=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
manifest=json.loads((root/'mare_interiors_manifest_v3.json').read_text(encoding='utf-8'))
design=json.loads((root/'mare_unified_progression_20.json').read_text(encoding='utf-8'))
design['schema_version']=3;design['blender_file']='Mare_Evolucao_Interiores_v3_1.blend';design['interior_manifest']='mare_interiors_manifest_v3.json';design['runtime_implemented']=False
last=0
for row,scene in zip(design['stages'],manifest['scenes']):
    row['rooms_represented_delta']=scene['rooms']-last;row['rooms_represented_total']=scene['rooms'];row['interior_collections']=scene['interior_collections'];last=scene['rooms']
(root/'mare_progression_interiors_v3.json').write_text(json.dumps(design,ensure_ascii=False,indent=2),encoding='utf-8')
sources=['build_mare_interiors_v3.py','refine_mare_interiors_v3.py','finish_mare_interiors_v3.py','prepare_mare_headless_v3.py','detail_mare_interiors_v3.py','link_mare_upper_interiors_v3.py','polish_mare_interiors_v3.py','support_mare_spa_v3.py','inspect_mare_interiors_v3.py','render_mare_interiors_v3.py','package_mare_interiors_v3.py']
for source in sources:shutil.copy2(Path.cwd()/source,root/source)
names=['Mare_Evolucao_Interiores_v3_1.blend','mare_progression_interiors_v3.json','mare_interiors_manifest_v3.json','mare_interiors_validation_v3.json','mare_interiors_render_evidence_v3.json','MARE_INTERIORES_V3.md']+['interior_v3_'+s+'.png' for s in ['lobby','quarto','restaurante','cozinha','spa','lavanderia']]+sources
files=[]
for name in names:
    p=root/name;h=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    row={'file':name,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
    if p.suffix=='.png':
        with p.open('rb') as stream:header=stream.read(24)
        row['resolution']=list(struct.unpack('>II',header[16:24]))
    files.append(row)
(root/'mare_interiors_hashes_v3.json').write_text(json.dumps({'revision':3,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files},indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'rooms':last,'renders':[r['resolution'] for r in files if 'resolution' in r],'blend':str(root/names[0])}))
