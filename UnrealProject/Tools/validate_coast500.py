import unreal,json,pathlib
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
geometry=[a for a in E.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label().startswith('Resort_')]
items=[]
for actor in geometry:
 o,e=actor.get_actor_bounds(False)
 items.append({'actor':actor.get_actor_label(),'bounds_cm':{'min':[o.x-e.x,o.y-e.y,o.z-e.z],'max':[o.x+e.x,o.y+e.y,o.z+e.z]},'collision_profile':str(actor.static_mesh_component.get_collision_profile_name())})
probes=[]
for x,y in [(-34300,35700),(-45000,26000),(-65000,12000),(-85000,5000)]:
 hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,15000),unreal.Vector(x,y,-1000),unreal.TraceTypeQuery.ECC_VISIBILITY,True,[],unreal.DrawDebugTrace.NONE,True)
 info={'xy_cm':[x,y],'hit':bool(hit)}
 if hit:
  detail=hit.to_tuple();loc=detail[4]
  info['location_cm']=[loc.x,loc.y,loc.z]
  if x==-34300:
   for a in E.get_all_level_actors():
    if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(x,y,loc.z+100),False,True)
 probes.append(info)
assert len(geometry)==16, len(geometry)
assert min(i['bounds_cm']['min'][1] for i in items)>-2,'Geometry remains beyond inland boundary'
assert world.get_path_name().startswith('/Game/Resort/Maps/Resort_HalfWest.')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report={'world':world.get_path_name(),'dimensions_m':[1000,500],'static_mesh_actors':len(geometry),'geometry':items,'ground_probes':probes,'validated':True}
pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject/Saved/coast500_validation.json').write_text(json.dumps(report,indent=2))
print('VALIDATED',json.dumps(report))
