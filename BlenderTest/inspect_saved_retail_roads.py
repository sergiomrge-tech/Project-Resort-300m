import bpy, json
s=bpy.context.scene
report={
    'file':bpy.data.filepath,'scene':s.name,
    'dimensions_m':list(bpy.data.objects['SITE_2000x1000_METERS'].dimensions),
    'sectors':s['sector_count'],'coastal_businesses':s['coastal_business_count'],
    'rounded_junctions':s['junctions_with_rounded_curbs'],'new_zebra_crossings':s['new_zebra_crossings'],'curb_ramps':s['curb_ramps'],
    'cleared_surface_assets':s['cleared_surface_assets'],'rounded_pavement_assets':s['rounded_pavement_assets'],
    'packed_images':len([im for im in bpy.data.images if im.source=='FILE' and im.packed_file]),
    'missing_or_unpacked_images':[im.name for im in bpy.data.images if im.source=='FILE' and (not im.packed_file or im.size[0]==0)],
    'sector_scales':list({tuple(o.scale) for o in s.objects if o.instance_type=='COLLECTION'}),
    'resolution':[s.render.resolution_x,s.render.resolution_y],
    'notes':'Blender art asset inspection; no runtime, physics or performance claims.'
}
with open('C:/Users/sergi/Documents/ChatGPT/resort/retail_roads_validation.json','w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('REOPENED_ASSET',json.dumps(report))
