import bpy,json
from mathutils import Vector
def block(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];a,b,d=loc;vs=[(a-x,b-y,d-z),(a+x,b-y,d-z),(a+x,b+y,d-z),(a-x,b+y,d-z),(a-x,b-y,d+z),(a+x,b-y,d+z),(a+x,b+y,d+z),(a-x,b+y,d+z)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat);uv=me.uv_layers.new(name='UrbanMeters')
    for li,loop in enumerate(me.loops):p=me.vertices[loop.vertex_index].co;uv.data[li].uv=(p.x,p.y)
    o=bpy.data.objects.new(name,me);c.objects.link(o);return o
def slope(name,c,y0,y1,z0,z1,width):
    me=bpy.data.meshes.new(name);me.from_pydata([(-width/2,y0,z0),(width/2,y0,z0),(width/2,y1,z1),(-width/2,y1,z1)],[],[(0,1,2,3)]);me.update();me.materials.append(bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers']);uv=me.uv_layers.new(name='UrbanMeters')
    for li,loop in enumerate(me.loops):p=me.vertices[loop.vertex_index].co;uv.data[li].uv=(p.x,p.y)
    o=bpy.data.objects.new(name,me);c.objects.link(o)
paving=bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers'];curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete'];wood=bpy.data.materials['MARE_Teak_Existing_PBR'];cream=bpy.data.materials['MARE_Linen_Canvas']
c=bpy.data.collections['UNIDA_02_DECK_RESTAURANTE'];block('UNIDA_Deck_To_Restaurant_Link',(-7,-20.25,.45),(6,.56,.14),paving,c)
slope('UNIDA_Restaurant_Entrance_Ramp',bpy.data.collections['UNIDA_04_RESTAURANTE_TRANSFORMADO'],-34,-20,.14,.53,4)
slope('UNIDA_Hotel_Entrance_Ramp',bpy.data.collections['UNIDA_06_HOTEL_SIMPLES'],-34,-21,.14,.53,4)
slope('UNIDA_Final_Arrival_Forecourt',bpy.data.collections['UNIDA_20_RESORT_UNICO'],-34,-21,.14,.53,13)
for c in [bpy.data.collections['UNIDA_06_HOTEL_SIMPLES'],bpy.data.collections['UNIDA_07_ALA_ESQUERDA'],bpy.data.collections['UNIDA_08_ALA_DIREITA']]:
    for o in list(c.objects):
        if 'Facade_Glass' not in o.name or o.location.y>-20 or o.location.z<3:continue
        x=o.location.x;z=o.location.z
        for side in [-1,1]:block('UNIDA_Guest_Curtain',(x+side*.9,-20.75,z),(.35,.045,2.3),cream,c)
# Weather-protected stair exit is replaced when new floors are bought.
def headhouse(name,floor):
    c=bpy.data.collections.new(name)
    for x in [5.82,9.98]:block('UNIDA_Stair_Exit_Wall',(x,-3.8,floor+1.15),(.12,4.3,2.3),curb,c)
    block('UNIDA_Stair_Exit_Back',(7.9,-1.62,floor+1.15),(4.3,.12,2.3),curb,c)
    block('UNIDA_Stair_Exit_Lid',(7.9,-3.8,floor+2.34),(4.4,4.5,.16),curb,c)
    for x in [6.4,9.4]:block('UNIDA_Stair_Exit_Front_Pier',(x,-5.98,floor+1.15),(.50,.12,2.3),wood,c)
    return c
low=headhouse('UNIDA_STAIR_EXIT_LOW',6.86);high=headhouse('UNIDA_STAIR_EXIT_ROOFTOP',10.07)
for i in range(6,19):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(low)
for i in [19,20]:bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(high)
cam=bpy.data.objects['UNIDA_Camera_Hotel'];cam.location=(-42,-58,28);cam.rotation_euler=(Vector((0,2,2))-cam.location).to_track_quat('-Z','Y').to_euler()
# Active Blender file opens at the complete connected structure.
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
bpy.context.scene['canonical_progression_file']='mare_unified_progression_20.json'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Unificada_v2.blend')
print('Physical terrace and arrival links completed, weather protected stair exits')
