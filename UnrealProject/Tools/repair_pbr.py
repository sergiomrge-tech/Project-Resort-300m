import pathlib,json,unreal
original_report=json.loads(pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject/Saved/half_map_build.json').read_text(encoding='utf8'))
source=pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject/Tools/build_half_map.py').read_text(encoding='utf-8-sig')
exec(compile(source.split('files=sorted(')[0],'<repair_pbr>','exec'))
updated=0
for actor in ACT.get_all_level_actors():
    if not isinstance(actor,unreal.StaticMeshActor) or not actor.get_actor_label().startswith('Resort_'):continue
    mesh=actor.static_mesh_component.static_mesh
    for i,slot in enumerate(mesh.static_materials):
        names=[clean(str(slot.material_slot_name)),clean(slot.material_interface.get_name()) if slot.material_interface else '']
        replacement=next((native[n] for n in names if n in native),None)
        if replacement and slot.material_interface != replacement:
            mesh.set_material(i,replacement);updated+=1
    AS.save_loaded_asset(mesh)
LEVEL.save_current_level()
original_report['pbr_materials']=report['pbr_materials']
original_report['warnings']=report['warnings']
original_report['pbr_slots_updated']=updated
(ROOT/'Saved/half_map_build.json').write_text(json.dumps(original_report,indent=2),encoding='utf8')
print('PBR_REPAIR',json.dumps({'materials':len(report['pbr_materials']),'warnings':len(report['warnings']),'slots_updated':updated}))
