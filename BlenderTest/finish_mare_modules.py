import bpy,math
from mathutils import Vector
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    uv=me.uv_layers.new(name='UrbanMeters');wooduv=me.uv_layers.new(name='WoodGrain')
    for f in me.polygons:
        normal=max((abs(f.normal[k]),k) for k in range(3))[1];axes=[k for k in range(3) if k!=normal]
        for li in f.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;co=(v[axes[0]],v[axes[1]]);uv.data[li].uv=co;wooduv.data[li].uv=co
    o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc;return o
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];steel=bpy.data.materials['MARE_Brushed_Stainless'];cream=bpy.data.materials['MARE_Linen_Canvas'];teal=bpy.data.materials['MARE_Painted_Teal'];ceramic=bpy.data.materials['MARE_Glazed_Ceramic'];curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete'];pavers=bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers']
c=bpy.data.collections['MARE_11_PISCINA']
for o in list(c.objects):
    if any(o.name.startswith('MARE_'+n) for n in ['Deck_Structure','Individual_Teak_Board','Deck_Edge','Pool_Basin']):bpy.data.objects.remove(o,do_unlink=True)
for x in [-36.75,-17.25]:box('MARE_Pool_Deck_Side',(x,25,.15),(3.5,20,.16),pavers,c)
for y in [17.5,32.5]:box('MARE_Pool_Deck_End',(-27,y,.15),(16,5,.16),pavers,c)
box('MARE_Pool_Tiled_Bottom',(-27,25,-.54),(16,10,.12),teal,c)
for x in [-34.9,-19.1]:box('MARE_Pool_Wall',(x,25,-.17),(.2,10,.75),teal,c)
for y in [20.1,29.9]:box('MARE_Pool_Wall',(-27,y,-.17),(16,.2,.75),teal,c)
for x in [-73,73]:
    c=bpy.data.collections['MARE_17_VILLAS']
    for y in [161.3,166.7]:box('MARE_Villa_Pool_Rim',(x,y,.22),(10.6,.35,.15),curb,c)
    for xx in [x-5.3,x+5.3]:box('MARE_Villa_Pool_Rim',(xx,164,.22),(.35,5.7,.15),curb,c)
    box('MARE_Villa_Pool_Base',(x,164,.1),(10,5,.2),teal,c)
c=bpy.data.collections['MARE_04_SANITARIOS']
# Opaque privacy walls behind glass fronts, separate toilet cubicles.
box('MARE_Bathroom_Privacy_Wall',(15,-6.86,1.75),(6.7,.10,2.6),curb,c)
for x in [13,17]:
    box('MARE_Bathroom_Door',(x,-6.94,1.53),(.95,.07,2.15),teal,c)
    box('MARE_WC_Cistern',(x,-1.6,.9),(.5,.22,.65),ceramic,c)
    box('MARE_WC_Pedestal',(x,-1.9,.65),(.37,.4,.4),ceramic,c)
    box('MARE_WC_Bowl',(x,-2.05,.90),(.5,.65,.20),ceramic,c)
    box('MARE_WC_Seat',(x,-2.05,1.02),(.53,.69,.045),cream,c)
box('MARE_Bathroom_Partition',(15,-2.1,1.75),(.12,3,2.6),curb,c)
c=bpy.data.collections['MARE_19_SUSTENTABILIDADE']
for x in [89,93,97,101]:
    for y in [130,134]:box('MARE_Solar_Mount_Rail',(x,y,3.68),(2.8,.05,.24),steel,c)
c=bpy.data.collections['MARE_13_KIDS_CLUB']
for x in [41,49]:box('MARE_Play_Frame_Post',(x,31,1.4),(.18,.18,2.8),wood,c)
box('MARE_Play_Frame_Beam',(45,31,2.85),(8.2,.20,.22),wood,c)
for x in [43,47]:
    box('MARE_Swing_Seat',(x,31,.65),(.65,.40,.08),wood,c)
    for xx in [x-.25,x+.25]:box('MARE_Swing_Rope',(xx,31,1.75),(.025,.025,2.1),cream,c)
# Service route remains clear of plot footprints.
c=bpy.data.collections['MARE_08_OPERACAO']
box('MARE_Service_Access',(113,90,.075),(5,225,.15),pavers,c)
box('MARE_Service_Connector',(89,145,.08),(48,4,.16),pavers,c)
for c in bpy.data.collections:
    if c.name.startswith('MARE_') and c.get('unlock_stage'):
        stage=c['unlock_stage']
        for o in c.objects:o['module_id']='mare_%02d'%stage;o['unlock_stage']=stage
g=bpy.data.materials['MARE_Coastal_Garden'];nt=g.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
coord=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=.2;n.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Object'],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.08,.12,.035,1);r.color_ramp.elements[1].color=(.26,.31,.085,1);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
bpy.context.window.scene=bpy.data.scenes['MARE_ETAPA_20']
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Quiosque_20Etapas_v1.blend')
print('Pools, bathrooms, playground, service route and solar supports finished')
