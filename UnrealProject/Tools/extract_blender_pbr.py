import bpy,bmesh,json,os,re,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ProjectResort_300m_CompactPass/UnrealProject/SourceArt/BlenderPBR')
ROOT.mkdir(parents=True,exist_ok=True)
images={}
for im in bpy.data.images:
    if im.source not in {'FILE','TILED'}: continue
    original=bpy.path.abspath(im.filepath)
    filename=Path(original).name or (re.sub(r'[^A-Za-z0-9_]','_',im.name)+'.png')
    target=ROOT/filename
    try:
        if im.packed_file: target.write_bytes(im.packed_file.data)
        elif Path(original).is_file(): shutil.copyfile(original,target)
        else: continue
        images[im.name]=str(target)
    except Exception as e: print('IMAGE_ERROR',im.name,str(e),flush=True)

def texture_upstream(socket,visited=None):
    visited=set() if visited is None else visited
    for link in socket.links:
        n=link.from_node
        if n.as_pointer() in visited: continue
        visited.add(n.as_pointer())
        if n.type=='TEX_IMAGE' and n.image and n.image.name in images:
            return {'file':images[n.image.name],'image':n.image.name,'colorspace':n.image.colorspace_settings.name}
        for inp in n.inputs:
            if inp.is_linked:
                found=texture_upstream(inp,visited)
                if found: return found
    return None

materials=[]
for m in bpy.data.materials:
    if not m.use_nodes: continue
    bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bs: continue
    entry={'name':m.name,'base_color':list(bs.inputs['Base Color'].default_value),'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'textures':{}}
    for slot in ['Base Color','Roughness','Metallic','Normal']:
        t=texture_upstream(bs.inputs[slot])
        if t: entry['textures'][slot]=t
    materials.append(entry)
scene=bpy.data.scenes['RESORT_MAIN_MARE_20']
bpy.context.window.scene=scene
dg=bpy.context.evaluated_depsgraph_get()
boundaries=[];temps=[]
for inst in dg.object_instances:
    ob=inst.object
    if ob.type!='MESH' or ob.hide_render: continue
    p=inst.matrix_world.translation
    if -1000<=p.x<0 and -500<=p.y<500: continue
    corners=[inst.matrix_world@Vector(c) for c in ob.bound_box]
    lo=[min(c[k] for c in corners) for k in range(3)]; hi=[max(c[k] for c in corners) for k in range(3)]
    if hi[0]<=-1000 or lo[0]>=0 or hi[1]<=-500 or lo[1]>=500: continue
    if hi[2]>20 or max(hi[0]-lo[0],hi[1]-lo[1])<150: continue
    ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg,preserve_all_data_layers=True)
    bm=bmesh.new();bm.from_mesh(me);bm.transform(inst.matrix_world)
    for co,no in [((-1000,0,0),(-1,0,0)),((0,0,0),(1,0,0)),((0,-500,0),(0,-1,0)),((0,500,0),(0,1,0))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector(co),plane_no=Vector(no),clear_outer=True,clear_inner=False,dist=0.00001)
    if bm.faces:
        bm.to_mesh(me);me.update()
        temp=bpy.data.objects.new('HalfBoundary_'+ob.name,me);scene.collection.objects.link(temp);temps.append(temp)
        boundaries.append({'source':ob.name,'bounds_before':[lo,hi],'faces':len(me.polygons)})
    else: bpy.data.meshes.remove(me)
    bm.free()
if temps:
    bpy.ops.object.select_all(action='DESELECT')
    for ob in temps: ob.select_set(True)
    bpy.context.view_layer.objects.active=temps[0]
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'HalfWest_BoundarySurfaces.fbx'),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_ALL',global_scale=100.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE',use_tspace=True,add_leaf_bones=False,path_mode='AUTO')
(ROOT/'materials.json').write_text(json.dumps({'images':images,'materials':materials,'boundary_surfaces':boundaries},indent=2),encoding='utf8')
print('PBR_EXTRACTION',json.dumps({'images':len(images),'materials':len(materials),'boundaries':boundaries}),flush=True)
