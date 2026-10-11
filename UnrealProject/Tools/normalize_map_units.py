import unreal,json,pathlib
act=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
items=[]
for actor in act.get_all_level_actors():
    if not isinstance(actor,unreal.StaticMeshActor) or not actor.get_actor_label().startswith('Resort_'):continue
    box=actor.static_mesh_component.static_mesh.get_bounding_box()
    maximum=max(abs(box.min.x),abs(box.max.x),abs(box.min.y),abs(box.max.y))
    scale=100.0 if maximum<5000 else 1.0
    actor.set_actor_scale3d(unreal.Vector(scale,scale,scale))
    origin,extent=actor.get_actor_bounds(False)
    items.append({'actor':actor.get_actor_label(),'unit_conversion_scale':scale,'bounds_cm':{'min':[origin.x-extent.x,origin.y-extent.y,origin.z-extent.z],'max':[origin.x+extent.x,origin.y+extent.y,origin.z+extent.z]}})
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject/Saved/half_map_world_bounds.json').write_text(json.dumps(items,indent=2),encoding='utf8')
print('Converted',len(items),'actors to Unreal centimetres')
