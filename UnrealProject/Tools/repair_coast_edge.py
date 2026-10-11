import unreal,pathlib,json
R=pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject')
A=unreal.EditorAssetLibrary;S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
opts=unreal.FbxImportUI();opts.automated_import_should_detect_type=False
opts.import_mesh=True;opts.import_as_skeletal=False;opts.import_materials=False;opts.import_textures=False;opts.import_animations=False
opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opts.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.generate_lightmap_u_vs=False;opts.static_mesh_import_data.auto_generate_collision=False
opts.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
name='City_01_03_Coast500_Final';path='/Game/Resort/Coast500/'+name
if not A.does_asset_exist(path):
 t=unreal.AssetImportTask();t.filename=str(R/'SourceArt/Coast1000x500/City_01_03_Coast500.fbx');t.destination_path='/Game/Resort/Coast500';t.destination_name=name;t.automated=True;t.save=True;t.factory=unreal.FbxFactory();t.options=opts
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset(path)
original=unreal.load_asset('/Game/Resort/CityHalfWest200/City_01_03')
bindings={str(s.material_slot_name):s.material_interface for s in original.static_materials}
slots=list(mesh.static_materials)
for s in slots:s.material_interface=bindings.get(str(s.material_slot_name),s.material_interface)
mesh.set_editor_property('static_materials',slots)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
ns=S.get_nanite_settings(mesh);ns.enabled=True;S.set_nanite_settings(mesh,ns)
A.save_loaded_asset(mesh)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label()=='Resort_City_01_03_Coast500':a.static_mesh_component.set_static_mesh(mesh)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print('EDGE_REPAIRED',mesh.get_bounding_box())
