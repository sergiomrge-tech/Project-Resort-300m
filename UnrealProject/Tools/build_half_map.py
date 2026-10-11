"""Build the west-half Unreal level using saved Blender assets and native PBR."""
import unreal,pathlib,json,re,gc,traceback
ROOT=pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject')
DEST='/Game/Resort/CityHalfWest200'
MAP='/Game/Resort/Maps/Resort_HalfWest'
META=json.loads((ROOT/'SourceArt/BlenderPBR/materials.json').read_text(encoding='utf8'))
ME=unreal.MaterialEditingLibrary
AS=unreal.EditorAssetLibrary
TOOLS=unreal.AssetToolsHelpers.get_asset_tools()
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
ACT=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVEL=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report={'map':MAP,'tiles':[],'pbr_materials':[],'warnings':[]}

def clean(name): return re.sub(r'[^A-Za-z0-9_]','_',name)
def note(message):
    unreal.log('RESORT_BUILD '+message)
    (ROOT/'Saved/half_map_build.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def collect():
    gc.collect();unreal.SystemLibrary.collect_garbage()

def import_boundary():
    path=DEST+'/HalfWest_BoundarySurfaces'
    if AS.does_asset_exist(path): return path
    opts=unreal.FbxImportUI()
    opts.automated_import_should_detect_type=False
    opts.import_mesh=True;opts.import_as_skeletal=False
    opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    opts.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
    opts.import_materials=True;opts.import_textures=False;opts.import_animations=False
    opts.static_mesh_import_data.combine_meshes=True
    opts.static_mesh_import_data.generate_lightmap_u_vs=False
    opts.static_mesh_import_data.auto_generate_collision=False
    opts.static_mesh_import_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    t=unreal.AssetImportTask();t.filename=str(ROOT/'SourceArt/BlenderPBR/HalfWest_BoundarySurfaces.fbx')
    t.destination_path=DEST;t.destination_name='HalfWest_BoundarySurfaces';t.automated=True;t.save=True
    t.factory=unreal.FbxFactory();t.options=opts;TOOLS.import_asset_tasks([t])
    AS.save_directory(DEST,only_if_is_dirty=True,recursive=True)
    return path

texture_cache={}
def texture(entry,kind):
    file=pathlib.Path(entry['file']);name=clean(file.stem)
    path='/Game/Resort/Textures/'+name
    if path in texture_cache: return texture_cache[path]
    if not AS.does_asset_exist(path):
        t=unreal.AssetImportTask();t.filename=str(file);t.destination_path='/Game/Resort/Textures';t.destination_name=name;t.automated=True;t.save=True
        TOOLS.import_asset_tasks([t])
    tex=unreal.load_asset(path)
    if not isinstance(tex,unreal.Texture2D): raise RuntimeError('Not a Texture2D: '+path)
    if kind=='Normal':
        tex.set_editor_property('srgb',False)
        tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('flip_green_channel','_gl' in file.stem.lower())
    elif kind in ('Roughness','Metallic'):
        tex.set_editor_property('srgb',False)
        tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS)
    AS.save_loaded_asset(tex);texture_cache[path]=tex
    return tex

def aligned_sample(mat,tex,kind,y):
    obj=ME.create_material_expression(mat,unreal.MaterialExpressionTextureObject,-800,y)
    obj.texture=tex
    obj.sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind=='Normal' else (unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if kind in ('Roughness','Metallic') else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    call=ME.create_material_expression(mat,unreal.MaterialExpressionMaterialFunctionCall,-350,y)
    func_name='WorldAlignedNormal' if kind=='Normal' else 'WorldAlignedTexture'
    func=unreal.load_asset('/Engine/Functions/Engine_MaterialFunctions01/Texturing/'+func_name)
    if not func: raise RuntimeError('Engine material function missing: '+func_name)
    if hasattr(call,'set_material_function'): call.set_material_function(func)
    else: call.set_editor_property('material_function',func)
    inputs=list(ME.get_material_expression_input_names(call));outputs=list(ME.get_material_expression_output_names(call))
    tex_pin=next((p for p in inputs if 'textureobject' in re.sub(r'[^a-z]','',p.lower())),None)
    size_pin=next((p for p in inputs if 'texturesize' in re.sub(r'[^a-z]','',p.lower())),None)
    out=next((p for p in outputs if 'xyz' in p.lower()),None)
    if not tex_pin or not size_pin or not out: raise RuntimeError('Unexpected function pins: '+str((inputs,outputs)))
    size=ME.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-800,y+90)
    size.constant=unreal.LinearColor(200,200,200,1)
    if not ME.connect_material_expressions(obj,'',call,tex_pin): raise RuntimeError('Texture object connection failed')
    if not ME.connect_material_expressions(size,'',call,size_pin): raise RuntimeError('Texture scale connection failed')
    return call,out

native={}
for entry in META['materials']:
    if not entry['textures']: continue
    source_name=clean(entry['name'])
    if not AS.does_asset_exist(DEST+'/'+source_name): continue
    path='/Game/Resort/Materials/M_PBR_'+source_name
    try:
        mat=unreal.load_asset(path) if AS.does_asset_exist(path) else TOOLS.create_asset('M_PBR_'+source_name,'/Game/Resort/Materials',unreal.Material,unreal.MaterialFactoryNew())
        ME.delete_all_material_expressions(mat)
        mat.set_editor_property('two_sided',True)
        mat.set_editor_property('tangent_space_normal',False)
        properties={'Base Color':unreal.MaterialProperty.MP_BASE_COLOR,'Roughness':unreal.MaterialProperty.MP_ROUGHNESS,'Metallic':unreal.MaterialProperty.MP_METALLIC,'Normal':unreal.MaterialProperty.MP_NORMAL}
        for y,(kind,prop) in enumerate(properties.items()):
            if kind in entry['textures']:
                node,out=aligned_sample(mat,texture(entry['textures'][kind],kind),kind,y*240)
            elif kind=='Base Color':
                node=ME.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-200,y*240)
                node.constant=unreal.LinearColor(*entry['base_color']);out=''
            elif kind=='Normal': continue
            else:
                node=ME.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,y*240)
                node.r=entry[kind.lower()];out=''
            if not ME.connect_material_property(node,out,prop): raise RuntimeError('Material property connection failed: '+kind)
        ME.recompile_material(mat);AS.save_loaded_asset(mat)
        native[source_name]=mat;report['pbr_materials'].append(path);note('PBR '+source_name)
    except Exception:
        report['warnings'].append({'material':source_name,'error':traceback.format_exc()})
        unreal.log_warning(traceback.format_exc())

files=sorted((ROOT/'SourceArt/BlenderV7_HalfWest_200m').glob('City_*.fbx'))
paths=[DEST+'/'+f.stem for f in files]
assert len(paths)==25 and all(AS.does_asset_exist(p) for p in paths),'Missing city tiles'
paths.append(import_boundary())
# Configure each saved mesh before creating actors, so unused import data can be collected.
for path in paths:
    mesh=unreal.load_asset(path)
    for index,slot in enumerate(mesh.static_materials):
        names=[clean(str(slot.material_slot_name)),clean(slot.material_interface.get_name()) if slot.material_interface else '']
        replacement=next((native[n] for n in names if n in native),None)
        if replacement and slot.material_interface != replacement: mesh.set_material(index,replacement)
    body=mesh.get_editor_property('body_setup')
    if body:
        body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    triangles=mesh.get_num_triangles(0)
    if triangles>100000:
        settings=SM.get_nanite_settings(mesh)
        if not settings.enabled:
            settings.enabled=True;SM.set_nanite_settings(mesh,settings)
    AS.save_loaded_asset(mesh)
    box=mesh.get_bounding_box()
    report['tiles'].append({'asset':path,'triangles':triangles,'bounds_cm':{'min':[box.min.x,box.min.y,box.min.z],'max':[box.max.x,box.max.y,box.max.z]},'nanite':SM.get_nanite_settings(mesh).enabled,'collision':str(SM.get_collision_complexity(mesh))})
    note('Mesh configured '+path)
    del mesh,body;collect()

LEVEL.load_level('/Game/ThirdPerson/Lvl_ThirdPerson')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
AS.make_directory('/Game/Resort/Maps')
if not unreal.EditorLoadingAndSavingUtils.save_map(world,MAP): raise RuntimeError('Could not save destination map')
LEVEL.load_level(MAP)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for actor in ACT.get_all_level_actors():
    if isinstance(actor,unreal.StaticMeshActor): ACT.destroy_actor(actor)
for path in paths:
    mesh=unreal.load_asset(path)
    actor=ACT.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    actor.set_actor_label('Resort_'+path.rsplit('/',1)[1])
    actor.set_folder_path('Resort/WestHalf')
    actor.static_mesh_component.set_static_mesh(mesh)
    box=mesh.get_bounding_box()
    scale=100.0 if max(abs(box.min.x),abs(box.max.x),abs(box.min.y),abs(box.max.y))<5000 else 1.0
    actor.set_actor_scale3d(unreal.Vector(scale,scale,scale))
    actor.static_mesh_component.set_collision_profile_name('BlockAll')
    actor.static_mesh_component.set_mobility(unreal.ComponentMobility.STATIC)
# Start on the promenade directly in front of the resort plot.
start=unreal.Vector(-34300,35700,350)
starts=[a for a in ACT.get_all_level_actors() if isinstance(a,unreal.PlayerStart)]
player_start=starts[0] if starts else ACT.spawn_actor_from_class(unreal.PlayerStart,start)
player_start.set_actor_location(start,False,True)
player_start.set_actor_rotation(unreal.Rotator(0,-90,0),True)
player_start.set_actor_label('Resort_PlayerStart')
for actor in ACT.get_all_level_actors():
    if isinstance(actor,unreal.DirectionalLight):
        actor.set_actor_rotation(unreal.Rotator(-38,-35,0),True)
    if isinstance(actor,unreal.SkyLight):
        actor.light_component.set_editor_property('real_time_capture',True)
loc=unreal.Vector(-64000,60000,42000)
rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(-38000,12000,0))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(loc,rot)
LEVEL.save_current_level()
report['actor_count']=len(ACT.get_all_level_actors())
report['player_start_cm']=[start.x,start.y,start.z]
report['status']='assembled'
note('ASSEMBLED')
