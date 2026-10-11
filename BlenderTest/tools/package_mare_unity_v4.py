import pathlib, hashlib, json, shutil, datetime
art=pathlib.Path(r'D:\ProjectResort_300m_CompactPass\BlenderTest')
proj=pathlib.Path(r'D:\ProjectResort_300m_CompactPass\UnityProject')
asset=proj/'Assets/R15/BlenderIntegrated'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=sorted(p for p in asset.rglob('*') if p.is_file())
scene=proj/'Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity'
files += [scene,pathlib.Path(str(scene)+'.meta'),pathlib.Path(str(asset)+'.meta')]
missing_meta=[str(p.relative_to(proj)) for p in asset.rglob('*') if not p.name.endswith('.meta') and not pathlib.Path(str(p)+'.meta').exists()]
records=[{'path':str(p.relative_to(proj)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
evidence=[]
for p in sorted((art/'UnityCaptures_v4').glob('*')):
 if p.is_file():evidence.append({'path':str(p.relative_to(art)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)})
sources=[]
for p in [art/'Resort_Main_Map_Mare_Integrated_v4.blend',art/'MARE_UNITY_INTEGRACAO_V4.md',*sorted((art/'tools').glob('*'))]:
 if p.is_file():sources.append({'path':str(p.relative_to(art)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)})
out={'version':4,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unity_project':str(proj),'source_blend':'Resort_Main_Map_Mare_Integrated_v4.blend','map_m':[2000,1000],'missing_meta':missing_meta,'unity_asset_files':records,'sources':sources,'evidence':evidence,'fps_measured':False,'play_mode_tested':False,'art_approved':False,'integration_complete':True}
(art/'mare_unity_hashes_v4.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert not missing_meta,missing_meta
stages=json.loads((art/'UnityCaptures_v4/stages_validation.json').read_text())
assert len(stages)==20 and all(x['missing_meshes']==x['missing_materials']==0 for x in stages)
assert stages[-1]['rooms']==59
print(json.dumps({'assets_hashed':len(records),'asset_bytes':sum(r['bytes'] for r in records),'missing_meta':len(missing_meta),'stages_verified':len(stages),'final_rooms':stages[-1]['rooms'],'manifest':str(art/'mare_unity_hashes_v4.json')}))
