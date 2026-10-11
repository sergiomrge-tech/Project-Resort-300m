"""Import the approved west half, checkpointing each asset to limit memory."""
import unreal, pathlib, json, gc, time, traceback
ROOT = pathlib.Path('D:/ProjectResort_300m_CompactPass/UnrealProject')
SOURCE = ROOT / 'SourceArt/BlenderV7_HalfWest_200m'
DEST = '/Game/Resort/CityHalfWest200'
REPORT = ROOT / 'Saved/half_map_import.json'
results=[]
tools=unreal.AssetToolsHelpers.get_asset_tools()

def checkpoint():
    REPORT.write_text(json.dumps({'source':str(SOURCE),'bounds_m':{'x':[-1000,0],'y':[-500,500]},'tiles':results},indent=2),encoding='utf-8')

for source in sorted(SOURCE.glob('City_*.fbx')):
    name=source.stem
    path=DEST+'/'+name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        results.append({'asset':path,'status':'already_saved'})
        checkpoint()
        continue
    unreal.log('RESORT_IMPORT_BEGIN '+name)
    try:
        opts=unreal.FbxImportUI()
        opts.automated_import_should_detect_type=False
        opts.import_mesh=True
        opts.import_as_skeletal=False
        opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
        opts.original_import_type=unreal.FBXImportType.FBXIT_STATIC_MESH
        opts.import_materials=True
        opts.import_textures=True
        opts.import_animations=False
        data=opts.static_mesh_import_data
        data.combine_meshes=True
        data.generate_lightmap_u_vs=False
        data.auto_generate_collision=False
        data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task=unreal.AssetImportTask()
        task.filename=str(source)
        task.destination_path=DEST
        task.destination_name=name
        task.automated=True
        task.replace_existing=False
        task.save=True
        task.factory=unreal.FbxFactory()
        task.options=opts
        tools.import_asset_tasks([task])
        mesh=unreal.load_asset(path)
        if not isinstance(mesh,unreal.StaticMesh):
            raise RuntimeError('StaticMesh missing after import: '+path)
        info={'asset':path,'status':'saved','triangles':mesh.get_num_triangles(0),'materials':len(mesh.static_materials)}
        unreal.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
        results.append(info)
        unreal.log('RESORT_IMPORT_DONE '+json.dumps(info))
        del mesh,task,opts,data
        gc.collect()
        unreal.SystemLibrary.collect_garbage()
        checkpoint()
    except Exception:
        results.append({'asset':path,'status':'error','message':traceback.format_exc()})
        checkpoint()
        unreal.log_error(traceback.format_exc())
        break
unreal.log('RESORT_IMPORT_FINISHED '+str(len(results)))
