import bpy, os, json, math, time, gc
from collections import Counter
from mathutils import Vector
import numpy as np
from pathlib import Path
OUT=Path('D:/ProjectResort_300m_CompactPass/UnrealProject/SourceArt/BlenderV7_HalfWest_200m')
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.data.scenes.get('RESORT_MAIN_MARE_20') or bpy.context.scene
if bpy.context.window: bpy.context.window.scene=scene
dg=bpy.context.evaluated_depsgraph_get()
XMIN,XMAX,YMIN,YMAX=-1000.0,0.0,-500.0,500.0
TILE=200.0; NX,NY=5,5

cache={}; summaries=[]; t0=time.time()
for ty in range(NY):
  for tx in range(NX):
    xmin=XMIN+tx*TILE; xmax=min(xmin+TILE,XMAX)
    ymin=YMIN+ty*TILE; ymax=min(ymin+TILE,YMAX)
    tile=f'City_{tx+1:02d}_{ty+1:02d}'
    b={'v':[],'f':[],'uv':[],'mi':[],'smooth':[],'mats':[]}; cache.clear(); count=0
    for inst in dg.object_instances:
      ob=inst.object
      if ob.type!='MESH' or ob.hide_render: continue
      p=inst.matrix_world.translation
      if p.x<xmin or p.x>=xmax or p.y<ymin or p.y>=ymax: continue
      key=ob.original.as_pointer(); data=cache.get(key)
      if data is None:
        ev=ob.evaluated_get(dg); mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
        if mesh is None or not mesh.polygons:
          if mesh: ev.to_mesh_clear()
          cache[key]=False; continue
        mesh.calc_loop_triangles()
        v=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
        uv=np.zeros((len(mesh.loops),2),dtype=np.float32)
        layer=mesh.uv_layers.active or (mesh.uv_layers[0] if mesh.uv_layers else None)
        if layer: layer.data.foreach_get('uv',uv.ravel())
        faces=[]; mats=[]; uvtri=[]; smooth=[]
        for tr in mesh.loop_triangles:
          faces.append(tuple(int(q) for q in tr.vertices)); mats.append(int(mesh.polygons[tr.polygon_index].material_index))
          uvtri.append(tuple(tuple(float(a) for a in uv[li]) for li in tr.loops)); smooth.append(bool(mesh.polygons[tr.polygon_index].use_smooth))
        materials=[m for m in mesh.materials]
        data=(v,faces,mats,uvtri,smooth,materials); cache[key]=data;ev.to_mesh_clear()
      if data is False: continue
      v,faces,mats,uvtri,smooth,materials=data
      if not faces: continue
      mat=inst.matrix_world
      xyz=(v @ np.asarray(mat.to_3x3(),dtype=np.float32).T + np.asarray(mat.translation,dtype=np.float32)).astype(np.float32)
      offset=len(b['v']);b['v'].extend(tuple(float(a) for a in row) for row in xyz)
      for m in materials:
        nm=m.name if m else 'Default'
        if nm not in b['mats']:b['mats'].append(nm)
      slots={nm:i for i,nm in enumerate(b['mats'])}
      for j,face in enumerate(faces):
        b['f'].append(tuple(offset+q for q in face));m=materials[mats[j]] if mats[j]<len(materials) else None
        b['mi'].append(slots[m.name if m else 'Default']);b['uv'].extend(uvtri[j]);b['smooth'].append(smooth[j])
      count+=1
    if not b['f']:
      summaries.append({'tile':tile,'empty':True});continue
    me=bpy.data.meshes.new(tile+'_Mesh');me.from_pydata(b['v'],[],b['f']);me.update(calc_edges=True)
    obj=bpy.data.objects.new(tile,me);scene.collection.objects.link(obj)
    for nm in b['mats']:me.materials.append(bpy.data.materials.get(nm) or bpy.data.materials.new(nm))
    for j,p in enumerate(me.polygons):p.material_index=b['mi'][j];p.use_smooth=b['smooth'][j]
    layer=me.uv_layers.new(name='UVMap')
    for j,p in enumerate(me.polygons):
      for k,li in enumerate(p.loop_indices):layer.data[li].uv=b['uv'][j*3+k]
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    fbx=OUT/(tile+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_ALL',global_scale=100.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,add_leaf_bones=False,embed_textures=False,path_mode='AUTO',batch_mode='OFF')
    sm={'tile':tile,'x_m':[xmin,xmax],'y_m':[ymin,ymax],'instances':count,'vertices':len(me.vertices),'triangles':len(me.polygons),'materials':len(me.materials),'fbx':str(fbx),'bytes':fbx.stat().st_size}
    summaries.append(sm);print('TILE_PASS',json.dumps(sm),flush=True)
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(me);del obj,me,b;gc.collect()
report={'scene':scene.name,'bounds_m':{'x':[XMIN,XMAX],'y':[YMIN,YMAX]},'tile_m':[TILE,TILE],'tiles':summaries,'triangles':sum(s.get('triangles',0) for s in summaries),'vertices':sum(s.get('vertices',0) for s in summaries),'bytes':sum(s.get('bytes',0) for s in summaries),'seconds':round(time.time()-t0,1)}
(OUT/'export_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('EXPORT_PASS',json.dumps({k:report[k] for k in ['bounds_m','tile_m','triangles','vertices','bytes','seconds']},ensure_ascii=False),flush=True)
