import bpy,json
from pathlib import Path
root=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
design=json.loads((root/'mare_unified_progression_20.json').read_text(encoding='utf-8'))
stages=[]
for row in design['stages']:
    s=bpy.data.scenes.get(row['scene'])
    assemblies=[c.name for c in s.collection.children] if s else []
    stages.append({'stage':row['id'],'scene':row['scene'],'present':bool(s),'assemblies':assemblies,'restaurant_location':s.get('restaurant_location') if s else None})
images=[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE' and im.users]
replacement_correct=all('MARE_01_QUIOSQUE_ORIGINAL' not in row['assemblies'] for row in stages if row['stage']>=4)
rear_correct=all('UNIDA_06_RESTAURANTE_NOS_FUNDOS' in row['assemblies'] for row in stages if row['stage']>=6)
future_leaks=[]
for row in stages:
    for name in row['assemblies']:
        c=bpy.data.collections[name]
        if c.get('unlock_stage',0)>row['stage']:future_leaks.append((row['stage'],name))
report={'file':bpy.data.filepath,'version':bpy.app.version_string,'stages':stages,'all_20_scenes_present':all(s['present'] for s in stages),'obsolete_kiosk_shell_replaced_at_4':replacement_correct,'rear_restaurant_from_stage_6':rear_correct,'future_stage_leaks':future_leaks,'source_city_preserved':bool(bpy.data.scenes.get('RESORT_2x1KM_COMERCIO')),'images':images,'all_used_file_images_packed':all(i['packed'] for i in images),'active_scene':bpy.context.scene.name,'runtime_verified':False}
(root/'mare_unified_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('UNIFIED_VALIDATION: 20 scenes',report['all_20_scenes_present'],'replacement',replacement_correct,'rear restaurant',rear_correct,'future leaks',len(future_leaks),'packed images',report['all_used_file_images_packed'])
