import bpy,math,random
from mathutils import Vector,noise
random.seed(704)
s=bpy.context.scene;col=bpy.data.collections['CRISTO_REDENTOR_DETAILED'];stone=bpy.data.materials['CRISTO_Soapstone_Mosaic']
v=[];f=[];N=144;R=40
for j in range(R+1):
    t=j/R;z=28.5+4.65*t;w=3.1*(1-t)+.90*t;d=1.30*(1-t)+.82*t
    for i in range(N):
        a=math.tau*i/N;fold=.06*math.cos(a*20+t*3);v.append(((w+fold)*math.cos(a),(d+fold)*math.sin(a),z))
for j in range(R):
    for i in range(N):k=j*N+i;f.append((k,j*N+(i+1)%N,(j+1)*N+(i+1)%N,k+N))
f.extend([tuple(reversed(range(N))),tuple(R*N+i for i in range(N))])
me=bpy.data.meshes.new('Cristo_Shoulder_Mantle');me.from_pydata(v,[],f);me.materials.append(stone);me.update();o=bpy.data.objects.new('Cristo_Continuous_Shoulder_Mantle',me);col.objects.link(o);o.location=(-350,1650,704)
for p in me.polygons:p.use_smooth=True
for o in col.objects:
    if o.type=='MESH' and o.name.startswith('Cristo_Cheek'):
        for v in o.data.vertices:v.co.y=-.90+(v.co.y+.90)*.50;v.co.x=(.68 if v.co.x>0 else -.68)+(v.co.x-(.68 if v.co.x>0 else -.68))*.80
    if o.type=='CURVE' and o.name.startswith('Cristo_Brow_Ridge'):o.data.bevel_depth=.065
    if o.type=='CURVE' and o.name.startswith('Cristo_Upper_Eyelid'):o.data.bevel_depth=.035
    if o.name=='Cristo_Carved_Hair_Cap':
        for v in o.data.vertices:v.co.z=35.90+(v.co.z-35.6)*.80
    if o.type=='MESH' and o.name.startswith('Cristo_Side_Hair'):
        for v in o.data.vertices:v.co.y=.49+(v.co.y-.49)*.7
p=next(n for n in bpy.data.materials['CRISTO_Carved_Recess'].node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.44,.48,.44,1)

# Terrain fractures at multiple physical scales, preserving the landmark's summit terrace.
for o in bpy.data.collections['RIO_MOUNTAINS_AND_FOREST'].objects:
    if o.type!='MESH' or not o.name.endswith('_TERRAIN'):continue
    for v in o.data.vertices:
        x,y,z=v.co
        if z<2:continue
        if o.name.startswith('CORCOVADO') and math.hypot(x+350,y-1650)<45:continue
        nv=noise.noise_vector(Vector((x*.025,y*.025,z*.005)))
        v.co.z+=nv.z*9+noise.noise_vector(Vector((x*.08,y*.08,7))).z*2.5
        v.co.x+=nv.x*4;v.co.y+=nv.y*4
    o.data.update()
m=bpy.data.materials['RIO_Granite_Atlantic_Forest'];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');geo=next(n for n in nt.nodes if n.type=='NEW_GEOMETRY');n=next(n for n in nt.nodes if n.type=='TEX_NOISE');r=next(n for n in nt.nodes if n.type=='VALTORGB')
r.color_ramp.elements[0].position=.24;r.color_ramp.elements[0].color=(.235,.26,.26,1);r.color_ramp.elements[1].position=.59;r.color_ramp.elements[1].color=(.032,.11,.025,1)
scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.035;nt.links.new(geo.outputs['Position'],scale.inputs[0]);nt.links.new(scale.outputs[0],n.inputs['Vector']);n.inputs['Scale'].default_value=4.0
b=next(n for n in nt.nodes if n.type=='BUMP');b.inputs['Distance'].default_value=3;b.inputs['Strength'].default_value=.55
# Distant forest canopy has real surface relief and physical tree instances on gentler slopes.

# Camera rays see a blue cloud panorama; the original packed HDRI still lights the scene.
world=s.world;nt=world.node_tree;bg=next(n for n in nt.nodes if n.type=='BACKGROUND');output=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD')
coords=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=4.8;n.inputs['Detail'].default_value=5;n.inputs['Roughness'].default_value=.68;nt.links.new(coords.outputs['Normal'],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.46;r.color_ramp.elements[0].color=(.045,.23,.52,1);r.color_ramp.elements[1].position=.65;r.color_ramp.elements[1].color=(.82,.88,.91,1);nt.links.new(n.outputs['Fac'],r.inputs[0])
skybg=nt.nodes.new('ShaderNodeBackground');skybg.inputs['Strength'].default_value=.8;nt.links.new(r.outputs[0],skybg.inputs['Color'])
lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(bg.outputs[0],mix.inputs[1]);nt.links.new(skybg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface'])
bpy.context.view_layer.update();s.camera=bpy.data.objects['RIO_CRISTO_DETAIL'];s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/rio_cristo_detail.png';s.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Cristo_Montanhas_Vegetacao.blend')
bpy.ops.render.render(write_still=True)
print('REFINED_CRISTO_AND_ROCK')
