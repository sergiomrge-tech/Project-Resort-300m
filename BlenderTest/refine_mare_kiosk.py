import bpy, math
from mathutils import Vector
c=bpy.data.collections['MARE_01_QUIOSQUE_ORIGINAL']
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];nt=wood.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');p=nt.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.43;nt.links.new(p.outputs[0],out.inputs[0])
uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='WoodGrain';scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(18,.8,1);nt.links.new(uv.outputs[0],scale.inputs[0])
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=4;n.inputs['Roughness'].default_value=.7;nt.links.new(scale.outputs[0],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(.055,.023,.009,1);r.color_ramp.elements[1].position=.82;r.color_ramp.elements[1].color=(.32,.16,.058,1);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
b=nt.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.002;b.inputs['Strength'].default_value=.22;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
wood['source']='Original procedural wood grain, longitudinal metre UVs';wood['license']='Project Resort original'
seen=set()
for o in bpy.data.objects:
    if o.type!='MESH' or wood not in list(o.data.materials) or o.data.name in seen:continue
    seen.add(o.data.name);me=o.data;layer=me.uv_layers.get('WoodGrain') or me.uv_layers.new(name='WoodGrain')
    spans=[max(v.co[k] for v in me.vertices)-min(v.co[k] for v in me.vertices) for k in range(3)];long=max((spans[k],k) for k in range(3))[1]
    for f in me.polygons:
        normal=max((abs(f.normal[k]),k) for k in range(3))[1];axes=[k for k in range(3) if k!=normal]
        if long in axes:axes.remove(long);axes.append(long)
        for li in f.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(co[axes[0]],co[axes[1]])
# Keep the founding kiosk clear from the promenade view.
for o in bpy.data.collections['MARE_ORLA_PERMANENTE'].objects:
    if o.instance_collection and o.instance_collection.name=='MARE_PALM_REUSABLE' and abs(o.location.x)<14 and o.location.y<-26:o.location.x=18 if o.location.x>=0 else -18
# Replace flat placeholder with a true sloped access ramp.
for o in list(c.objects):
    if o.name.startswith('MARE_Entrance_Ramp'):bpy.data.objects.remove(o,do_unlink=True)
verts=[(-3.9,-26,.02),(-2.5,-26,.02),(-2.5,-20,.02),(-3.9,-20,.02),(-3.9,-26,.06),(-2.5,-26,.06),(-2.5,-20,.48),(-3.9,-20,.48)]
me=bpy.data.meshes.new('MARE_Sloped_Ramp');me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(wood)
layer=me.uv_layers.new(name='WoodGrain')
for li,loop in enumerate(me.loops):co=me.vertices[loop.vertex_index].co;layer.data[li].uv=(co.x,co.y)
o=bpy.data.objects.new('MARE_Entrance_Sloped_Ramp',me);c.objects.link(o);o['slope_percent']=7.0;o['width_m']=1.4;o['note']='Art geometry; accessibility and collisions not certified'
# Use originals from the founding module for small hardware instances.
source=next(o for o in c.objects if o.name.startswith('MARE_Post_Bolt'))
for i in range(40):
    for y in [-19.75,-12.25]:
        o=bpy.data.objects.new('MARE_Deck_Screw',source.data);c.objects.link(o);o.location=(-3.88+i*.194,y,.488);o.scale=(.30,.30,.30)
# Rolled shade and gable bracing.
source=next(o for o in c.objects if o.name.startswith('MARE_Stool_Foot_Ring'))
for side in [-1,1]:
    for j in range(10):
        y=-18.95+j*.59;z=3.53+.95*(1-abs(y+16)/3.15)
        a=Vector((side*3.45,y,3.55));end=Vector((side*3.45,y,z));d=end-a
        if d.length<.04:continue
        o=bpy.data.objects.new('MARE_Gable_Louver',source.data.copy());c.objects.link(o)
        # Source is a cylinder-like ring; scale creates slender slats under roof.
        o.location=(a+end)/2;o.scale=(.10,.10,d.length/.035);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.clear();o.data.materials.append(wood)
for i in [1,2]:
    ld=bpy.data.lights.new('MARE_Task_Light','AREA');ld.energy=45;ld.color=(1,.79,.52);ld.shape='DISK';ld.size=.45
    o=bpy.data.objects.new('MARE_Task_Light',ld);c.objects.link(o);o.location=(-1.2 if i==1 else 1.2,-17.1,2.7)
for o in c.objects:o['module_id']='mare_01';o['unlock_stage']=1
bpy.context.window.scene=bpy.data.scenes['MARE_ETAPA_01']
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Quiosque_20Etapas_v1.blend')
print('Kiosk refinements',len(c.objects),'objects',len(seen),'wood meshes')
