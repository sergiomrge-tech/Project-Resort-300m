import bpy,json,hashlib
from pathlib import Path
root=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
last=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
manifest=json.loads(last['interior_manifest_json'])
scenes=[];leaks=[];expanded=[]
for i in range(1,21):
    s=bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i]
    rc=[o for o in s.objects if o.get('room_id')]
    cs=[c for c in s.collection.children if c.name.startswith('INTERIOR_')]
    scenes.append({'stage':i,'scene':s.name,'rooms':len(rc),'interior_collections':[c.name for c in cs]})
    for c in cs:
        if c.get('unlock_stage',0)>i or c.get('last_stage',20)<i:leaks.append([i,c.name])
for o in last.objects:
    if o.name.startswith('GAME_'):
        expanded.append({'id':o.name,'type':o.get('interaction_type'),'position':list(o.matrix_world.translation),'runtime_implemented':False})
    if o.get('room_id') and o.instance_collection:
        for a in o.instance_collection.objects:
            if a.name.startswith('GAME_'):
                expanded.append({'id':o['room_id']+'/'+a.name,'type':a.get('interaction_type'),'position':list((o.matrix_world @ a.matrix_world).translation),'runtime_implemented':False})
manifest['collections']=[{'name':c.name,'objects':len(c.objects),'first':c.get('unlock_stage',0),'last':c.get('last_stage',20)} for c in bpy.data.collections if c.name.startswith('INTERIOR_')]
manifest['scenes']=scenes;manifest['expanded_final_activity_anchors']=expanded;manifest['room_count']=scenes[-1]['rooms'];manifest['file']=bpy.data.filepath
(root/'mare_interiors_manifest_v3.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
images=[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and im.users]
report={'file':bpy.data.filepath,'blender':bpy.app.version_string,'stages':len(scenes),'final_room_count':scenes[-1]['rooms'],'activity_anchors':len(expanded),'future_or_expired_collection_leaks':leaks,'all_used_file_textures_packed':all(x['packed'] for x in images),'source_city_preserved':bool(bpy.data.scenes.get('RESORT_2x1KM_COMERCIO')),'runtime_verified':False,'collision_navigation_verified':False,'visual_review':'real Blender renders; not a Unity playtest','images':images}
(root/'mare_interiors_validation_v3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTERIOR_REOPEN_VALIDATION '+json.dumps({k:v for k,v in report.items() if k not in ['images','file']}))
