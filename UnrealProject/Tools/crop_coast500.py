"""Physically crop source FBX meshes to the retained coastal rectangle."""
import bpy,bmesh,json,gc
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ProjectResort_300m_CompactPass/UnrealProject')
OUT=ROOT/'SourceArt/Coast1000x500';OUT.mkdir(parents=True,exist_ok=True)
sources=[ROOT/'SourceArt/BlenderV7_HalfWest_200m'/f'City_{x:02d}_03.fbx' for x in range(1,6)]
sources.append(ROOT/'SourceArt/BlenderPBR/HalfWest_BoundarySurfaces.fbx')
report=[]
for src in sources:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(src))
 kept=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type!='MESH': continue
  bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world)
  # Previous FBX exports have global scale 100; normalize back to metres.
  for v in bm.verts:v.co*=0.01
  for co,no in [((-1000,0,0),(-1,0,0)),((0,0,0),(1,0,0)),((0,-500,0),(0,-1,0)),((0,0,0),(0,1,0))]:
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector(co),plane_no=Vector(no),clear_outer=True,dist=0.00001)
  if not bm.faces:
   bm.free();bpy.data.objects.remove(ob,do_unlink=True);continue
  bm.to_mesh(ob.data);bm.free();ob.data.update();ob.matrix_world.identity();kept.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in kept:ob.select_set(True)
 bpy.context.view_layer.objects.active=kept[0]
 name=src.stem+'_Coast500'
 target=OUT/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(target),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_ALL',global_scale=100.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_tspace=True,add_leaf_bones=False,path_mode='AUTO')
 bounds=[[min(v.co[k] for ob in kept for v in ob.data.vertices) for k in range(3)],[max(v.co[k] for ob in kept for v in ob.data.vertices) for k in range(3)]]
 report.append({'file':str(target),'bounds_m':bounds,'faces':sum(len(ob.data.polygons) for ob in kept)})
 (OUT/'crop_report.json').write_text(json.dumps(report,indent=2))
 print('CROPPED',name,bounds,flush=True);gc.collect()
