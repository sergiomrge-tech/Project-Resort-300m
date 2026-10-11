import unreal,json,pathlib
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
act=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=act.get_all_level_actors()
city=[a for a in actors if a.get_actor_label().startswith('Resort_City_')]
boundary=[a for a in actors if a.get_actor_label()=='Resort_HalfWest_BoundarySurfaces']
result={'world':world.get_path_name(),'city_tiles':len(city),'boundary_meshes':len(boundary),'probes':[]}
assert len(city)==25 and len(boundary)==1, 'Unexpected half-map actor count'
for x,y in [(-34300,35700),(-34300,32000),(-50000,30000),(-50000,0),(-80000,-30000)]:
    detail=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,20000),unreal.Vector(x,y,-1000),unreal.TraceTypeQuery.ECC_VISIBILITY,True,[],unreal.DrawDebugTrace.NONE,True)
    hit=detail is not None
    entry={'x_cm':x,'y_cm':y,'hit':hit}
    if hit:
        location=detail.to_tuple()[4]
        entry['z_cm']=location.z
        if x==-34300 and y==35700:
            for actor in actors:
                if isinstance(actor,unreal.PlayerStart):
                    actor.set_actor_location(unreal.Vector(x,y,location.z+100),False,True)
                    result['player_start_cm']=[x,y,location.z+100]
    result['probes'].append(entry)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject/Saved/half_map_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
