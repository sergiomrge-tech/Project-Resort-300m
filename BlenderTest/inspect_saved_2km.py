import bpy, json
s=bpy.context.scene
report={
    'file':bpy.data.filepath,
    'scene':s.name,
    'site_dimensions_m':list(bpy.data.objects['Exact_Site_2000x2000__IP_Limestone'].dimensions),
    'sector_instances':len([o for o in s.objects if o.instance_type=='COLLECTION']),
    'sector_scales':list({tuple(o.scale) for o in s.objects if o.instance_type=='COLLECTION'}),
    'packed_images':len([im for im in bpy.data.images if im.source=='FILE' and im.packed_file]),
    'missing_or_unpacked':[im.name for im in bpy.data.images if im.source=='FILE' and (not im.packed_file or im.size[0]==0)],
    'camera_names':[o.name for o in s.objects if o.type=='CAMERA'],
    'render_resolution':[s.render.resolution_x,s.render.resolution_y],
    'render_engine':s.render.engine,
    'world':s.world.name if s.world else None
}
with open('C:/Users/sergi/Documents/ChatGPT/resort/resort_2km_validation.json','w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('SAVED_FILE_INSPECTION',json.dumps(report))
