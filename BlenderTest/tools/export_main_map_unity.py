import bpy,json,math,struct,re,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('D:/ProjectResort_300m_CompactPass/BlenderTest/UnityExport_v4');ROOT.mkdir(exist_ok=True)
(ROOT/'Textures').mkdir(exist_ok=True)
city=bpy.data.collections['MAIN_CITY_WITH_MARE_LOT']
stages=[bpy.data.collections['MAIN_MARE_STAGE_%02d'%i] for i in range(1,21)]
collections=[];col_ids={};objects={};mats=[];mat_ids={};mesh_ids={};meshes=[]
def collect(c):
    if c.name in col_ids:return col_ids[c.name]
    idx=len(collections);col_ids[c.name]=idx;collections.append(c)
    for child in c.children:collect(child)
    for o in c.objects:
        if o.hide_render or o.type=='CAMERA':continue
        objects[o.name]=o
        if o.instance_type=='COLLECTION' and o.instance_collection:collect(o.instance_collection)
        if o.type in ['MESH','FONT','CURVE']:
            for m in o.data.materials:
                if m and m.name not in mat_ids:mat_ids[m.name]=len(mats);mats.append(m)
    return idx
collect(city)
assemblies={}
for i,c in enumerate(stages,1):
    for a in c.children:collect(a);assemblies.setdefault(a.name,[]).append(i)
print('EXPORT_LIBRARY_SOURCES',len(collections),len(objects),len(mats),flush=True)
scene=bpy.data.scenes.new('UNITY_EXPORT_LIBRARY');bpy.context.window.scene=scene
library=bpy.data.collections.new('UNITY_EXPORT_SOURCE_OBJECTS');scene.collection.children.link(library)
for o in objects.values():
    if o.type in ['MESH','FONT','CURVE']:library.objects.link(o)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
C=Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
def matrix(m):return [float(v) for row in C@m@C for v in row]
def pnode(m):return next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
def uv_name(m):
    if m.use_nodes:
        n=next((n for n in m.node_tree.nodes if n.type=='UVMAP'),None)
        if n:return n.uv_map or 'UVMap'
    return 'UVMap'
def tile(m):return float(m.get('tile_width_m',1))
def collider(name):
    low=name.lower()
    if any(s in low for s in ['water','sea','ocean','glass','glazing','leaf','foliage','lamp','light','curtain','rug','pool_water','foam','mirror','head_trim']):return False
    return any(s in low for s in ['floor','foundation','ground','site_','terrain','asphalt','road','sidewalk','paver','promenade','wall','structure','shell','slab','stair','tread','ramp','deck','curb','column','pier','post','bed_platform','counter','canopy','roof'])
for k,o in enumerate(objects.values()):
    if o.type not in ['MESH','FONT','CURVE']:continue
    ev=o.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
    if not me or not me.polygons:
        if me:ev.to_mesh_clear()
        continue
    me.calc_loop_triangles();n=len(me.loops)
    coords=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
    indices=np.empty(n,dtype=np.int32);me.loops.foreach_get('vertex_index',indices)
    normal=np.empty(n*3,dtype=np.float32);me.corner_normals.foreach_get('vector',normal);normal=normal.reshape(-1,3)
    uv=np.zeros((n,2),dtype=np.float32);slots=[m.name if m else None for m in me.materials]
    for f in me.polygons:
        m=me.materials[f.material_index] if len(me.materials)>f.material_index else None
        layer=me.uv_layers.get(uv_name(m)) if m else None
        layer=layer or (me.uv_layers.active if me.uv_layers else None)
        if layer:
            ids=list(f.loop_indices)
            uv[ids]=np.asarray([layer.data[li].uv[:] for li in ids],dtype=np.float32)/(tile(m) if m else 1)
    vertex=np.concatenate([coords[indices][:,[0,2,1]],normal[:,[0,2,1]],uv],axis=1).astype('<f4')
    groups={}
    for tri in me.loop_triangles:
        mi=tri.material_index;groups.setdefault(mi,[]).extend([tri.loops[0],tri.loops[2],tri.loops[1]])
    idx=len(meshes);mesh_ids[o.name]=idx;path=ROOT/('mesh_%05d.meshbin'%idx)
    with path.open('wb') as stream:
        stream.write(struct.pack('<III',0x3452534d,n,len(groups)));stream.write(vertex.tobytes())
        sub=[]
        for mi,ts in sorted(groups.items()):
            mid=mat_ids.get(slots[mi],0) if mi<len(slots) else 0
            stream.write(struct.pack('<II',mid,len(ts)));stream.write(np.asarray(ts,dtype='<i4').tobytes());sub.append(mid)
    meshes.append({'id':idx,'name':o.name,'file':path.name,'vertices':n,'triangles':sum(len(v)//3 for v in groups.values()),'materials':sub})
    ev.to_mesh_clear()
    if k%500==0:print('MESH_EXPORT',k,idx,flush=True)
# Bake material channels on a UV tile, preserving the exact node network on the source copy.
scene.collection.children.unlink(library);scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
except Exception:scene.cycles.device='CPU'
me=bpy.data.meshes.new('Material Bake Tile');me.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);me.update()
for name in ['BakeUV','UrbanMeters','WoodGrain','UVMap','WorldMeters']:me.uv_layers.new(name=name)
plane=bpy.data.objects.new('UNITY_MATERIAL_BAKE_TILE',me);scene.collection.objects.link(plane);plane.select_set(True);bpy.context.view_layer.objects.active=plane
material_records=[];out=bpy.data.worlds.new('ExportNeutralWorld');out.use_nodes=True;scene.world=out
def image_save(im,name):
    ext=Path(im.filepath).suffix.lower()
    if ext not in ['.jpg','.png','.hdr','.exr','.tif','.tga']:ext='.png'
    path=ROOT/'Textures'/(name+ext)
    if im.packed_file:path.write_bytes(bytes(im.packed_file.data))
    elif Path(bpy.path.abspath(im.filepath)).is_file():
        import shutil;shutil.copyfile(bpy.path.abspath(im.filepath),path)
    else:im.save_render(filepath=str(path))
    return 'Textures/'+path.name
def bake_channel(copy,source,channel,path,size,color=True):
    nt=copy.node_tree;output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');original=output.inputs['Surface'].links[0].from_socket if output.inputs['Surface'].is_linked else None
    emission=None
    if channel!='NORMAL':
        emission=nt.nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
        if source.is_linked:nt.links.new(source.links[0].from_socket,emission.inputs['Color'])
        else:
            val=source.default_value;emission.inputs['Color'].default_value=tuple(val) if hasattr(val,'__len__') else (val,val,val,1)
        nt.links.new(emission.outputs[0],output.inputs['Surface'])
    im=bpy.data.images.new('UNITY_BAKE_'+path,width=size,height=size,alpha=True);im.colorspace_settings.name='sRGB' if color else 'Non-Color'
    receiver=nt.nodes.new('ShaderNodeTexImage');receiver.image=im;nt.nodes.active=receiver
    bpy.ops.object.bake(type='NORMAL' if channel=='NORMAL' else 'EMIT',margin=2,use_clear=True)
    im.filepath_raw=str(ROOT/'Textures'/path);im.file_format='PNG';im.save()
    nt.nodes.remove(receiver)
    if original:nt.links.new(original,output.inputs['Surface'])
    if emission:nt.nodes.remove(emission)
    return im
for i,m in enumerate(mats):
    bs=pnode(m)
    record={'id':i,'name':m.name,'color':list(bs.inputs['Base Color'].default_value) if bs else list(m.diffuse_color),'metallic':float(bs.inputs['Metallic'].default_value) if bs else 0,'smoothness':1-float(bs.inputs['Roughness'].default_value) if bs else .3,'base_map':'','normal_map':'','metallic_map':'','emission':list(bs.inputs['Emission Color'].default_value) if bs else [0,0,0,1],'emission_strength':float(bs.inputs['Emission Strength'].default_value) if bs else 0,'transparent':False,'alpha':1,'tile_m':tile(m),'conversion':'Unity URP equivalent; UV material tile bake for linked channels'}
    transmission=float(bs.inputs['Transmission Weight'].default_value) if bs else 0
    low=m.name.lower();record['transparent']=any(t in low for t in ['glass','glazing','clear_','pool_water']) and 'lamp' not in low
    if record['transparent']:record['alpha']=.18 if 'pool' not in low else .73
    copy=m.copy();me.materials.clear();me.materials.append(copy);copybs=pnode(copy)
    for layer in me.uv_layers:
        factor=record['tile_m'] if layer.name==uv_name(m) else 1
        for li,uvco in enumerate([(0,0),(1,0),(1,1),(0,1)]):layer.data[li].uv=(uvco[0]*factor,uvco[1]*factor)
    me.uv_layers.active_index=0;me.uv_layers[0].active_render=True
    if copybs:
        if copybs.inputs['Base Color'].is_linked:
            size=2048 if any(n.type=='TEX_IMAGE' and n.image for n in m.node_tree.nodes) else 1024
            im=bake_channel(copy,copybs.inputs['Base Color'],'COLOR','mat_%03d_base.png'%i,size,True);record['base_map']='Textures/'+Path(im.filepath_raw).name;record['color']=[1,1,1,1];bpy.data.images.remove(im)
        nor=next((n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and any(t in n.image.name.lower() for t in ['nor_gl','normal'])),None)
        if nor:record['normal_map']=image_save(nor,'mat_%03d_normal'%i)
        elif copybs.inputs['Normal'].is_linked:
            im=bake_channel(copy,copybs.inputs['Normal'],'NORMAL','mat_%03d_normal.png'%i,1024,False);record['normal_map']='Textures/'+Path(im.filepath_raw).name;bpy.data.images.remove(im)
        if copybs.inputs['Roughness'].is_linked:
            im=bake_channel(copy,copybs.inputs['Roughness'],'ROUGH','temp_rough_%03d.png'%i,1024,False)
            pixels=np.empty(1024*1024*4,dtype=np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(-1,4);rough=pixels[:,0].copy();pixels[:,0]=record['metallic'];pixels[:,1:3]=0;pixels[:,3]=1-np.clip(rough,0,1);im.pixels.foreach_set(pixels.ravel());path=ROOT/'Textures'/('mat_%03d_metallic.png'%i);im.filepath_raw=str(path);im.save();record['metallic_map']='Textures/'+path.name
            (ROOT/'Textures'/('temp_rough_%03d.png'%i)).unlink(missing_ok=True);bpy.data.images.remove(im)
    material_records.append(record);bpy.data.materials.remove(copy);print('MATERIAL_EXPORT',i,m.name,flush=True)
sky=next((n.image for n in bpy.data.scenes['RESORT_MAIN_MARE_20'].world.node_tree.nodes if n.type=='TEX_ENVIRONMENT' and n.image),None)
sky_path=image_save(sky,'main_sky_panorama') if sky else ''
col_records=[]
for c in collections:
    nodes=[]
    for child in c.children:nodes.append({'name':child.name,'collection':col_ids[child.name],'mesh':-1,'matrix':matrix(Matrix.Identity(4)),'kind':'collection','collider':False})
    for o in c.objects:
        if o.hide_render or o.type=='CAMERA':continue
        node={'name':o.name,'collection':-1,'mesh':mesh_ids.get(o.name,-1),'matrix':matrix(o.matrix_world),'kind':o.type,'collider':collider(o.name),'interaction':o.get('interaction_type',''),'room_id':o.get('room_id',''),'light_color':[1,1,1],'light_energy':0,'light_range':0}
        if o.instance_type=='COLLECTION' and o.instance_collection:
            node['kind']='collection';node['collection']=col_ids[o.instance_collection.name];node['matrix']=matrix(o.matrix_world @ Matrix.Translation(-o.instance_collection.instance_offset))
        elif o.type=='LIGHT':node['kind']=o.data.type;node['light_color']=list(o.data.color);node['light_energy']=o.data.energy;node['light_range']=max(3,min(12,math.sqrt(max(1,o.data.energy))*.5))
        elif node['mesh']<0 and not node['interaction'] and not node['room_id']:continue
        nodes.append(node)
    col_records.append({'id':col_ids[c.name],'name':c.name,'nodes':nodes})
data={'version':4,'map_width':2000,'map_depth':1000,'unity_meters':True,'city_collection':col_ids[city.name],'sky':sky_path,'materials':material_records,'meshes':meshes,'collections':col_records,'assemblies':[{'name':name,'collection':col_ids[name],'stages':stages} for name,stages in assemblies.items()],'resort_matrix':matrix(Matrix.Translation(Vector((-340,-295,0)))),'final_room_count':59,'source':'Resort_Main_Map_Mare_Integrated_v4.blend','runtime_gameplay_implemented':False}
(ROOT/'main_map_export.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('UNITY_EXPORT_COMPLETE '+json.dumps({'meshes':len(meshes),'materials':len(mats),'collections':len(collections),'bytes':sum(p.stat().st_size for p in ROOT.glob('*.meshbin')),'sky':sky_path}),flush=True)
