import bpy, os, json, math, time
from collections import Counter, defaultdict
from mathutils import Vector
import numpy as np
from pathlib import Path
SOURCE='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Main_Map_Mare_Houses_v7.blend'
OUT=Path('D:/ProjectResort_300m_CompactPass/UnrealProject/SourceArt/BlenderV7')
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.get('RESORT_MAIN_MARE_20') or bpy.context.scene
if bpy.context.window: bpy.context.window.scene=scene
dg=bpy.context.evaluated_depsgraph_get()
# Project dimensions are exactly 2,000 x 1,000 Blender metres. Split into 200 m tiles.
XMIN,XMAX,YMIN,YMAX=-1000.0,1000.0,-500.0,500.0
TILE=200.0; NX,NY=10,5
cache={}; tile_data=defaultdict(lambda:{'v':[],'f':[],'uv':[],'mi':[],'smooth':[],'mats':[]})
counts=Counter(); tris=Counter(); included=0; skipped=0; t0=time.time()
# Read evaluated local mesh data once per source object; repeated scene instances reuse it.
for k,inst in enumerate(dg.object_instances):
    ob=inst.object
    if ob.type!='MESH' or ob.hide_render: continue
    p=inst.matrix_world.translation
    if p.x<XMIN-25 or p.x>XMAX+25 or p.y<YMIN-25 or p.y>YMAX+25:
        skipped+=1; continue
    tx=max(0,min(NX-1,int(math.floor((p.x-XMIN)/TILE))))
    ty=max(0,min(NY-1,int(math.floor((p.y-YMIN)/TILE))))
    tile=f'City_{tx+1:02d}_{ty+1:02d}'
    key=ob.original.as_pointer()
    cached=cache.get(key)
    if cached is None:
        ev=ob.evaluated_get(dg); mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
        if mesh is None or not mesh.polygons:
            if mesh: ev.to_mesh_clear()
            cache[key]=None; continue
        mesh.calc_loop_triangles()
        v=np.empty(len(mesh.vertices)*3,dtype=np.float64); mesh.vertices.foreach_get('co',v); v=v.reshape(-1,3)
        uv_layer=mesh.uv_layers.active or (mesh.uv_layers[0] if mesh.uv_layers else None)
        uv=np.zeros((len(mesh.loops),2),dtype=np.float32)
        if uv_layer: uv_layer.data.foreach_get('uv',uv.ravel())
        # Keep transformed local vertices; the instance transform is applied for each copy.
        tri=[]; tri_mat=[]; tri_uv=[]; tri_smooth=[]
        for tr in mesh.loop_triangles:
            tri.append(tuple(int(x) for x in tr.vertices))
            poly=mesh.polygons[tr.polygon_index]
            tri_mat.append(int(poly.material_index))
            tri_uv.append(tuple(tuple(float(q) for q in uv[li]) for li in tr.loops))
            tri_smooth.append(bool(poly.use_smooth))
        mats=[m for m in mesh.materials]
        cached=(v,tri,tri_mat,tri_uv,tri_smooth,mats)
        ev.to_mesh_clear(); cache[key]=cached
    if cached is None: continue
    v,faces,mis,uvs,smooth,mats=cached
    if not faces: continue
    b=tile_data[tile]; offset=len(b['v'])
    mat=inst.matrix_world
    coords=(v @ np.asarray(mat.to_3x3(),dtype=np.float64).T + np.asarray(mat.translation,dtype=np.float64)).astype(np.float32)
    b['v'].extend(tuple(float(q) for q in xyz) for xyz in coords)
    # Create one tile mesh with global material slots keyed by Blender material name.
    for mi,m in enumerate(mats):
        nm=m.name if m else 'Default'
        if nm not in b['mats']: b['mats'].append(nm)
    slotmap={nm:i for i,nm in enumerate(b['mats'])}
    for fi,face in enumerate(faces):
        b['f'].append(tuple(offset+idx for idx in face))
        source_mat=mats[mis[fi]] if mis[fi]<len(mats) else None
        b['mi'].append(slotmap[source_mat.name if source_mat else 'Default'])
        b['uv'].extend(uvs[fi]); b['smooth'].append(smooth[fi])
    included+=1; counts[tile]+=1; tris[tile]+=len(faces)
    if k and k%15000==0: print('PROGRESS',k,'instances',included,'tiles',len(tile_data),'sec',round(time.time()-t0,1),flush=True)
# Build spatially chunked meshes in scene-local metric coordinates.
collection=bpy.data.collections.new('UE_CITY_V7_EXPORT'); scene.collection.children.link(collection)
created=[]
for tile,b in tile_data.items():
    if not b['f']: continue
    me=bpy.data.meshes.new(tile+'_Mesh'); me.from_pydata(b['v'],[],b['f']); me.update(calc_edges=True)
    ob=bpy.data.objects.new(tile,me); collection.objects.link(ob)
    for nm in b['mats']:
        me.materials.append(bpy.data.materials.get(nm) or bpy.data.materials.new(nm))
    for i,poly in enumerate(me.polygons):
        poly.material_index=b['mi'][i]; poly.use_smooth=b['smooth'][i]
    layer=me.uv_layers.new(name='UVMap')
    for i,poly in enumerate(me.polygons):
        for j,li in enumerate(poly.loop_indices): layer.data[li].uv=b['uv'][i*3+j]
    created.append(ob)
    print('BUILT',tile,'vertices',len(me.vertices),'triangles',len(me.polygons),'materials',len(me.materials),flush=True)
# Export one FBX with 50 named mesh objects; Unreal imports as per-tile StaticMeshes.
bpy.ops.object.select_all(action='DESELECT')
for ob in created: ob.select_set(True)
bpy.context.view_layer.objects.active=created[0]
fbx=OUT/'ProjectResort_CityV7_2kmx1km.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_ALL',global_scale=100.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,add_leaf_bones=False,embed_textures=False,path_mode='AUTO',batch_mode='OFF')
report={'source':SOURCE,'scene':scene.name,'bounds_m':{'x':[XMIN,XMAX],'y':[YMIN,YMAX]},'tile_m':[TILE,TILE],'tiles':len(created),'instances':included,'skipped_outside':skipped,'triangles':sum(tris.values()),'vertices':sum(len(o.data.vertices) for o in created),'fbx':str(fbx),'bytes':fbx.stat().st_size,'seconds':round(time.time()-t0,1)}
(OUT/'export_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('EXPORT_PASS',json.dumps(report,ensure_ascii=False),flush=True)
