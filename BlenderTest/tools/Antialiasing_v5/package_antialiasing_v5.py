import pathlib,json,hashlib,datetime
art=pathlib.Path(r'D:\ProjectResort_300m_CompactPass\BlenderTest')
proj=pathlib.Path(r'D:\ProjectResort_300m_CompactPass\UnityProject')
def record(p,root):
 h=hashlib.sha256(p.read_bytes())
 return {'path':str(p.relative_to(root)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':h.hexdigest()}
paths=[proj/'Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity',proj/'ProjectSettings/GraphicsSettings.asset',proj/'ProjectSettings/QualitySettings.asset']
paths+=sorted((proj/'Assets/R15/BlenderIntegrated/Rendering').rglob('*'))
paths+=[proj/'Assets/R15/BlenderIntegrated/Rendering.meta']
missing=[str(p) for p in paths if str(p).startswith(str(proj/'Assets')) and not p.name.endswith('.meta') and not pathlib.Path(str(p)+'.meta').exists()]
assert not missing,missing
paths=[p for p in paths if p.is_file()]
files=sorted((art/'UnityCaptures_AA_v5').glob('*'))+sorted((art/'tools/Antialiasing_v5').glob('*'))+[art/'ANTIALIASING_V5.md']
data={'version':5,'scope':'antialiasing delta over integration v4','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_manifest':'mare_unity_hashes_v4.json','changed_unity_files':[record(p,proj) for p in paths],'evidence_and_tools':[record(p,art) for p in files if p.is_file()],'missing_meta':missing,'fps_measured':False}
out=art/'mare_antialiasing_hashes_v5.json';out.write_text(json.dumps(data,indent=2),encoding='utf8')
print(json.dumps({'manifest':str(out),'unity_files':len(paths),'evidence_and_tools':len(data['evidence_and_tools']),'missing_meta':missing}))
