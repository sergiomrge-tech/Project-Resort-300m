"""Build the playable coastal map; all removed inland sectors stay out of this level."""
import unreal,json,pathlib,re,gc
ROOT=pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject')
AS=unreal.EditorAssetLibrary; AT=unreal.AssetToolsHelpers.get_asset_tools()
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
OLD='/Game/Resort/CityHalfWest200';DEST='/Game/Resort/Coast500'
MAP='/Game/Resort/Maps/Resort_HalfWest'
assert len(list((ROOT/'SourceArt/Coast1000x500').glob('*.fbx')))==6,'Cropping incomplete'
assert L.load_level(MAP),'Cannot load destination level'
# Reuse the original material bindings, including the repaired native PBR shaders.
materials={}
for name in [f'City_{x:02d}_03' for x in range(1,6)]+['HalfWest_BoundarySurfaces']:
 mesh=unreal.load_asset(OLD+'/'+name)
 for slot in mesh.static_materials:
  for n in [str(slot.material_slot_name)]:
   materials[n]=slot.material_interface
 del mesh
paths=[];report={'map':MAP,'bounds_m':{'x':[-1000,0],'y':[-500,0]},'removed_depth_m':500,'meshes':[]}
for f in sorted((ROOT/'SourceArt/Coast1000x500').glob('*.fbx')):
 asset_name=f.stem+'_Final' if f.stem=='City_01_03_Coast500' else f.stem
 path=DEST+'/'+asset_name
 if not AS.does_asset_exist(path):
  opts=unreal.FbxImportUI();opts.automated_import_should_detect_type=False
  opts.import_mesh=True;opts.import_as_skeletal=False
  opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
  opts.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
  opts.import_materials=False;opts.import_textures=False;opts.import_animations=False
  data=opts.static_mesh_import_data
  data.combine_meshes=True;data.generate_lightmap_u_vs=False;data.auto_generate_collision=False
  data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
  t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=DEST;t.destination_name=asset_name
  t.automated=True;t.save=True;t.factory=unreal.FbxFactory();t.options=opts
  AT.import_asset_tasks([t])
 mesh=unreal.load_asset(path);assert isinstance(mesh,unreal.StaticMesh),path
 slots=list(mesh.static_materials);missing=[];materials_changed=False
 for slot in slots:
  names=[str(slot.material_slot_name)]
  candidates=names+[re.sub(r'\.\d+$','',n) for n in names]
  mat=next((materials[n] for n in candidates if n in materials and materials[n]),None)
  if mat and slot.material_interface != mat:slot.material_interface=mat;materials_changed=True
  elif not mat:missing.append(names)
 if materials_changed:mesh.set_editor_property('static_materials',slots)
 body=mesh.get_editor_property('body_setup')
 body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 ns=SM.get_nanite_settings(mesh)
 if mesh.get_num_triangles(0)>100000 and not ns.enabled:
  ns.enabled=True;SM.set_nanite_settings(mesh,ns)
 AS.save_loaded_asset(mesh)
 paths.append(path);report['meshes'].append({'asset':path,'triangles':mesh.get_num_triangles(0),'unmatched_materials':missing})
 (ROOT/'Saved/coast500_build.json').write_text(json.dumps(report,indent=2))
 unreal.log('COAST500_IMPORTED '+path)
 del mesh,body,slots;gc.collect();unreal.SystemLibrary.collect_garbage()
# Replace level geometry, keeping sky, sun, cloud and gameplay setup.
for actor in E.get_all_level_actors():
 if isinstance(actor,unreal.StaticMeshActor):E.destroy_actor(actor)
paths += [OLD+f'/City_{x:02d}_{y:02d}' for x in range(1,6) for y in (1,2)]
for path in paths:
 mesh=unreal.load_asset(path)
 actor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
 actor.set_actor_label('Resort_'+path.rsplit('/',1)[1]);actor.set_folder_path('Resort/Coast1000x500')
 actor.static_mesh_component.set_static_mesh(mesh)
 box=mesh.get_bounding_box()
 scale=100.0 if max(abs(box.min.x),abs(box.max.x),abs(box.min.y),abs(box.max.y))<5000 else 1.0
 actor.set_actor_scale3d(unreal.Vector(scale,scale,scale))
 actor.static_mesh_component.set_collision_profile_name('BlockAll')
 actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
starts=[a for a in E.get_all_level_actors() if isinstance(a,unreal.PlayerStart)]
start=starts[0] if starts else E.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(-34300,35700,140))
start.set_actor_label('Resort_PlayerStart');start.set_actor_location(unreal.Vector(-34300,35700,140),False,True)
for actor in E.get_all_level_actors():
 if isinstance(actor,unreal.DirectionalLight):actor.set_actor_rotation(unreal.Rotator(-38,-35,0),True)
 if isinstance(actor,unreal.SkyLight):actor.light_component.set_editor_property('real_time_capture',True)
loc=unreal.Vector(-62000,65000,50000)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(loc,unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(-50000,22000,0)))
assert L.save_current_level(),'Map save failed'
report['status']='saved';report['static_mesh_actors']=len(paths)
report['world']=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()
(ROOT/'Saved/coast500_build.json').write_text(json.dumps(report,indent=2))
print('COAST500_FINISHED',json.dumps(report))
