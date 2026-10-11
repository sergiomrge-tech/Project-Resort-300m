import bpy,math,json
from mathutils import Vector
s=bpy.context.scene
if s.get('urban_pbr_pass_v1'):raise RuntimeError('Urban PBR already applied')
folder='D:/ProjectResort_300m_CompactPass/BlenderTest/TexturesPBR_Urban/'
loaded={};materials={}
def image(asset,suffix,linear=False):
    key=asset+'_'+suffix
    if key not in loaded:
        im=bpy.data.images.load(folder+asset+'_'+suffix+'_4k.jpg',check_existing=True);im.name='URBAN_4K_'+key
        if linear:im.colorspace_settings.name='Non-Color'
        loaded[key]=im
    return loaded[key]
def pbr(name,asset,meters=2,tint=None,normalstrength=.55,height=.015):
    m=bpy.data.materials.new('URBAN_PBR_'+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');p=nt.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.75;nt.links.new(p.outputs[0],out.inputs[0])
    uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UrbanMeters';scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/meters;nt.links.new(uv.outputs[0],scale.inputs[0])
    maps={}
    for suffix in ['diff','nor_gl','rough','disp']:
        n=nt.nodes.new('ShaderNodeTexImage');n.image=image(asset,suffix,suffix!='diff');n.label=asset+' '+suffix;n.extension='REPEAT';nt.links.new(scale.outputs[0],n.inputs['Vector']);maps[suffix]=n
    if tint:
        grey=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(maps['diff'].outputs['Color'],grey.inputs[0])
        color=nt.nodes.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=.40;color.inputs[1].default_value=(*tint[:3],1);nt.links.new(grey.outputs[0],color.inputs[2]);nt.links.new(color.outputs[0],p.inputs['Base Color']);m.diffuse_color=(*tint[:3],1)
    else:nt.links.new(maps['diff'].outputs['Color'],p.inputs['Base Color'])
    rough=nt.nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.52;rough.inputs['To Max'].default_value=.94;nt.links.new(maps['rough'].outputs['Color'],rough.inputs['Value']);nt.links.new(rough.outputs[0],p.inputs['Roughness'])
    normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map='UrbanMeters';normal.inputs['Strength'].default_value=normalstrength;nt.links.new(maps['nor_gl'].outputs['Color'],normal.inputs['Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=height;nt.links.new(maps['disp'].outputs['Color'],bump.inputs['Height']);nt.links.new(normal.outputs[0],bump.inputs['Normal']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
    m['texture_source']='https://polyhaven.com/a/'+asset;m['license']='CC0';m['tile_width_m']=meters;m['height_use']='bump shading only, no geometric displacement';materials[name]=m
    return m
sidewalk=pbr('Sidewalk_Stone_Pavers','pavement_03',2,normalstrength=.72,height=.018)
forecourt=pbr('Retail_Concrete_Pavers','concrete_pavers_02',2,normalstrength=.7,height=.012)
curb=pbr('Curb_Cut_Concrete','concrete',2,tint=(.63,.61,.55),normalstrength=.35,height=.006)
trim=pbr('Facade_Cast_Concrete','concrete',3,tint=(.74,.71,.62),normalstrength=.35,height=.007)
promenade=pbr('Promenade_Stone_Pavers','pavement_03',2,tint=(.73,.71,.64),normalstrength=.55,height=.012)
paint={}
for name in ['IP_Coral_Plaster','IP_Teal_Plaster','IP_Sage_Plaster','IP_Ochre_Plaster','IP_Ivory']:
    old=bpy.data.materials[name];p=next(n for n in old.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tint=tuple(p.inputs['Base Color'].default_value)
    paint[name]=pbr(name+'_Painted_Render','grey_plaster_02',3,tint,normalstrength=.48,height=.008)
    # Small-scale variation plus vertically stretched rain staining, kept subtle.
    m=paint[name];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');color=next(n for n in nt.nodes if n.type=='MIX_RGB')
    coords=nt.nodes.new('ShaderNodeTexCoord');stretch=nt.nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(.25,.25,.018);nt.links.new(coords.outputs['Object'],stretch.inputs[0]);n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=4;n.inputs['Detail'].default_value=3;nt.links.new(stretch.outputs[0],n.inputs['Vector']);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.08;nt.links.new(color.outputs[0],mix.inputs[1]);nt.links.new(n.outputs['Fac'],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])

cols={o.instance_collection.name:o.instance_collection for o in s.objects if o.instance_collection and o.instance_collection.name.endswith('CONNECTED_ROADS_GROUNDED')}
objects={o.name:o for c in cols.values() for o in c.all_objects if o.type=='MESH'}
changed=[]
for o in objects.values():
    newslots=[];changed_slot=False
    for old in o.data.materials:
        target=old;name=o.name
        if old and old.name in paint:target=paint[old.name]
        elif old and 'checkered_pavement' in old.name:target=forecourt if 'Forecourt' in name else sidewalk
        elif old and old.name=='IP_Limestone':
            if 'Curb' in name or 'Paving_Transition' in name:target=curb
            elif 'Promenade' in name and 'Joints' not in name:target=promenade
            elif any(t in name for t in ['Cornice','Lintel','Base__','Portal','Roof__','Frames__','Balcony','Parapet','Patio']):target=trim
        changed_slot=changed_slot or target!=old;newslots.append(target)
    if not changed_slot:continue
    me=o.data.copy();o.data=me
    for i,m in enumerate(newslots):me.materials[i]=m
    uv=me.uv_layers.get('UrbanMeters')
    if not uv:uv=me.uv_layers.new(name='UrbanMeters')
    me.update()
    for face in me.polygons:
        axis=max((abs(face.normal[k]),k) for k in range(3))[1]
        for li in face.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co+o.location
            if axis==2:co=(p.x,p.y)
            elif axis==1:co=(p.x,p.z)
            else:co=(p.y,p.z)
            uv.data[li].uv=co
    changed.append(o.name)

# Existing window geometry now has sharper reflections and less plastic-looking glass.
m=bpy.data.materials['IP_Glass'];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.14;p.inputs['Metallic'].default_value=.28;p.inputs['Transmission Weight'].default_value=.16;p.inputs['IOR'].default_value=1.45
root=bpy.data.collections['MAP_2000x1000_COMERCIO']
name='URBAN_FACADE_TEXTURE_DETAIL';data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);root.objects.link(cam);cam.location=(-65,-327,4.7);data.lens=36;data.clip_end=15000;cam.rotation_euler=(Vector((-65,-314,8))-cam.location).to_track_quat('-Z','Y').to_euler()
s['urban_pbr_pass_v1']=True;s['urban_pbr_meshes']=len(changed);s['urban_pbr_materials']=json.dumps({k:m.name for k,m in materials.items()});s['urban_pbr_image_count']=len(loaded)
bpy.context.view_layer.update();bpy.ops.file.pack_all();s.camera=bpy.data.objects['RETAIL_CAFE'];s.cycles.samples=48;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Urban_Textures_v3.blend')
s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/urban_pbr_walk.png';bpy.ops.render.render(write_still=True)
print('URBAN_PBR_DONE',len(changed),'meshes',len(materials),'materials',len(loaded),'4K maps')
