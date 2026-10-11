import bpy, json
s=bpy.context.scene
images=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.name.startswith('URBAN_4K_')]
root=bpy.data.collections.get('MAP_2000x1000_COMERCIO')
instances=[o for o in root.all_objects if o.instance_type=='COLLECTION' and o.instance_collection and o.instance_collection.name.startswith('MODULE_')] if root else []
report={'file':bpy.data.filepath,'scene':s.name,'urban_meshes':s.get('urban_pbr_meshes'),'urban_image_count':s.get('urban_pbr_image_count'),'images':images,'sector_instances':len(instances),'sector_scales_unit':all(all(abs(v-1)<0.00001 for v in o.scale) for o in instances),'materials':json.loads(s.get('urban_pbr_materials','{}'))}
report['lot_surface_fix']=bool(s.get('urban_lot_surface_fix'))
report['lot_surface_meshes']=len([o for o in bpy.data.objects if o.name.startswith('URBAN_Lot_Surface_')])
with open('D:/ProjectResort_300m_CompactPass/BlenderTest/urban_pbr_validation.json','w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print('URBAN_VALIDATION_JSON='+json.dumps(report))
