import bpy,json
from pathlib import Path
out={'scenes':[],'collections':[]}
for s in bpy.data.scenes:
 out['scenes'].append({'name':s.name,'camera':s.camera.name if s.camera else None,'world':s.world.name if s.world else None,'roots':[c.name for c in s.collection.children]})
for c in bpy.data.collections:
 if c.name.startswith(('MAIN_CITY','MAIN_MARE_STAGE','RESORT_MAIN_MARE')):
  out['collections'].append({'name':c.name,'objects':len(c.objects),'children':[x.name for x in c.children],'instances':sum(1 for o in c.objects if o.instance_type=='COLLECTION')})
p=Path('D:/ProjectResort_300m_CompactPass/BlenderTest/unreal_export_inspection.json')
p.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'scenes':out['scenes'][-4:],'interesting_collections':out['collections'][-30:]},ensure_ascii=False),flush=True)
