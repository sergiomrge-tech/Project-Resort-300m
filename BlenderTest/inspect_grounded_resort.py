import bpy,json
from pathlib import Path
s=bpy.context.scene
audit=json.loads(s['grounding_audit_json'])
sectors=[o for o in s.objects if o.instance_collection and o.instance_collection.name.endswith('CONNECTED_ROADS_GROUNDED')]
counts={}
for o in sectors:counts[o.instance_collection.name]=counts.get(o.instance_collection.name,0)+1
relocations=sum(sum(1 for p in log['vegetation'] if abs(p['from'][0]-p['to'][0])+abs(p['from'][1]-p['to'][1])>.01)*counts.get(name+'_GROUNDED',0) for name,log in audit.items())
grounded=sum(len(log['vegetation'])*counts.get(name+'_GROUNDED',0) for name,log in audit.items())
images=[i for i in bpy.data.images if i.source=='FILE']
result={'file':bpy.data.filepath,'scene':s.name,'map_dimensions_m':list(bpy.data.objects['SITE_2000x1000_METERS'].dimensions),'sector_count':len(sectors),'sector_prototypes':counts,'xy_relocated_vegetation_instances':relocations,'grounded_vegetation_instances':grounded,'packed_images':sum(bool(i.packed_file) for i in images),'file_images':len(images),'unpacked_images':[i.name for i in images if not i.packed_file],'prototype_audit':audit,'detail_support_counts_per_coastal_sector':s.get('grounding_details_counts'),'limitations':['Geometric grounding and visual Blender inspection only; no Unity physics or FPS measurement.','Vegetation placement uses street corridors and building footprints; not a complete NavMesh accessibility audit.']}
Path('D:/ProjectResort_300m_CompactPass/BlenderTest/grounding_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('GROUNDING_VALIDATION',json.dumps({k:v for k,v in result.items() if k!='prototype_audit'}))
