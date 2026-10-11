import bpy,math
from mathutils import Vector
context=bpy.data.collections['UNIDA_ORLA_CONTINUA'];c=bpy.data.collections['UNIDA_19_AMPLIACAO_VERTICAL'];mat=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete']
def mesh(name,vs,fs,mat,c):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);o=bpy.data.objects.new(name,me);c.objects.link(o);return o
def box(name,loc,size,mat,c):
    a,b,d=loc;x,y,z=[v/2 for v in size];return mesh(name,[(a-x,b-y,d-z),(a+x,b-y,d-z),(a+x,b+y,d-z),(a-x,b+y,d-z),(a-x,b-y,d+z),(a+x,b-y,d+z),(a+x,b+y,d+z),(a-x,b+y,d+z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,c)
for x in [-9.4,-6.6]:box('UNIDA_Roof_Lift_Wall',(x,.4,11.22),(.12,2.8,2.3),mat,c)
box('UNIDA_Roof_Lift_Back',(-8,1.8,11.22),(2.9,.12,2.3),mat,c)
box('UNIDA_Roof_Lift_Cap',(-8,.4,12.44),(3,3,.16),mat,c)
for o in list(context.objects):
    if o.name.startswith('MARE_Ocean'):context.objects.unlink(o)
o=bpy.data.objects['UNIDA_Continuous_Sea'];o.data=o.data.copy();water=bpy.data.materials['RIO_Atlantic_Water_Backdrop'].copy();water.name='UNIDA_Atlantic_Blue_Water';o.data.materials.clear();o.data.materials.append(water)
p=next(n for n in water.node_tree.nodes if n.type=='BSDF_PRINCIPLED');nt=water.node_tree
for link in list(nt.links):
    if link.to_node==p and link.to_socket.name in ['Base Color','Normal']:nt.links.remove(link)
p.inputs['Roughness'].default_value=.14;p.inputs['Transmission Weight'].default_value=.18;p.inputs['IOR'].default_value=1.333
coord=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=.8;n.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Object'],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.008,.065,.12,1);r.color_ramp.elements[1].color=(.025,.20,.25,1);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.12;b.inputs['Strength'].default_value=.22;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
foam=bpy.data.materials.new('UNIDA_Shoreline_Foam');foam.use_nodes=True;nt=foam.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');mix=nt.nodes.new('ShaderNodeMixShader');transparent=nt.nodes.new('ShaderNodeBsdfTransparent');p=nt.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.84,.92,.88,1);p.inputs['Roughness'].default_value=.9
nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(p.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
co=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=2.1;n.inputs['Detail'].default_value=3;nt.links.new(co.outputs['Object'],n.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.44;r.color_ramp.elements[1].position=.58;nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],mix.inputs[0])
vs=[];fs=[]
for i in range(221):
    x=-220+i*2;y=-108+2.1*math.sin(x*.035)+.6*math.sin(x*.17);w=1.3+.8*math.sin(x*.23)**2;vs.extend([(x,y-w,-.581),(x,y+w,-.581)])
for i in range(220):fs.append((2*i,2*i+1,2*i+3,2*i+2))
mesh('UNIDA_Static_Shoreline_Foam',vs,fs,foam,context)
cam=bpy.data.objects['UNIDA_Camera_Orla'];cam.location=(70,-170,18);cam.rotation_euler=(Vector((0,-23,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort']
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.clip_end=5000;space.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Unificada_v2.blend')
print('Unified rooftop lift head and seafront water/foam prepared; foam is static art')
