import bpy, math
from mathutils import Vector
c=bpy.data.collections['MARE_01_QUIOSQUE_ORIGINAL'];base=bpy.data.collections['MARE_ORLA_PERMANENTE']
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];teal=bpy.data.materials['MARE_Painted_Teal'];steel=bpy.data.materials['MARE_Brushed_Stainless'];brass=bpy.data.materials['MARE_Brushed_Brass'];pavers=bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers']
def solid(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    for name_uv in ['UrbanMeters','WoodGrain','UVMap']:
        uv=me.uv_layers.new(name=name_uv)
        for f in me.polygons:
            normal=max((abs(f.normal[k]),k) for k in range(3))[1];axes=[k for k in range(3) if k!=normal]
            if normal==2:axes=[0,1]
            for li in f.loop_indices:
                p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]])
    o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc;b=o.modifiers.new('Crafted edges','BEVEL');b.width=.012;b.segments=2;o['unlock_stage']=1;o['module_id']='mare_01';return o
def strut(name,a,b,width,mat,c):
    d=Vector(b)-Vector(a);o=solid(name,(Vector(a)+Vector(b))/2,(width,width,d.length),mat,c);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
# Real load paths: eave beams, tie beams, king posts and knee braces.
for x in [-2.9,2.9]:
    solid('MARE_Truss_Tie_Beam',(x,-16,3.34),(.18,5.65,.22),wood,c)
    strut('MARE_Truss_King_Post',(x,-16,3.4),(x,-16,4.48),.14,wood,c)
    for sign in [-1,1]:
        y=-16+sign*2.35
        strut('MARE_Eave_Post_Extension',(x,y,3.32),(x,y,3.78),.18,wood,c)
        strut('MARE_Truss_Diagonal',(x,y,3.42),(x,-16,4.40),.12,wood,c)
        strut('MARE_Knee_Brace',(x,y,2.80),(x,y-sign*.62,3.28),.10,wood,c)
        solid('MARE_Timber_Connection_Plate',(x+.105,y,3.43),(.022,.25,.26),brass,c)
for y in [-18.35,-13.65]:solid('MARE_Eave_Main_Beam',(0,y,3.75),(6.35,.19,.20),wood,c)
# Cabinet carries the sink; a front panel and toe kick meet the deck.
solid('MARE_Sink_Base_Cabinet',(-1.75,-15.6,.81),(1.06,.76,.72),teal,c)
solid('MARE_Sink_Toe_Kick',(-1.75,-15.60,.52),(.97,.65,.14),wood,c)
for x in [-2.01,-1.49]:
    solid('MARE_Sink_Cabinet_Door',(x,-16.00,.83),(.49,.045,.59),wood,c)
    strut('MARE_Sink_Cabinet_Handle',(x,-16.04,.83),(x,-16.04,1.03),.018,brass,c)
solid('MARE_Sink_Lateral_Worktop',(-2.37,-15.6,1.27),(.25,.77,.06),steel,c)
# Footings for the exterior café table and planters.
solid('MARE_Cafe_Paved_Pad',(-5.3,-16,.055),(1.9,3,.12),pavers,c)
for x in [-4.7,4.7]:solid('MARE_Planter_Plinth',(x,-18,.05),(1.1,1.1,.1),pavers,c)
solid('MARE_Kiosk_Public_Connector',(-3.2,-30,.02),(1.4,8,.05),pavers,c)
# Beach boards slope down to the actual sand level; rail heights follow them.
for o in list(base.objects):
    if any(o.name.startswith('MARE_'+n) for n in ['Accessible_Beach_Boardwalk','Boardwalk_Rail_Post','Boardwalk_Handrail']):bpy.data.objects.remove(o,do_unlink=True)
for x in [-90,0,90]:
    points=[(-42,.14),(-48,.04),(-54,-.06),(-61,-.17),(-68,-.27)]
    for i in range(4):
        y0,z0=points[i];y1,z1=points[i+1]
        d=Vector((0,y1-y0,z1-z0));o=solid('MARE_Graded_Beach_Boardwalk',(x,(y0+y1)/2,(z0+z1)/2),(3.2,d.length,.06),wood,base);o.rotation_euler.x=math.atan2(z1-z0,y1-y0)
        for side in [-1,1]:
            strut('MARE_Boardwalk_Rail',(x+side*1.55,y0,z0+1),(x+side*1.55,y1,z1+1),.055,wood,base)
            strut('MARE_Boardwalk_Post',(x+side*1.55,y0,z0),(x+side*1.55,y0,z0+1),.055,wood,base)
for o in c.objects:o['module_id']='mare_01';o['unlock_stage']=1
s=bpy.data.scenes['MARE_ETAPA_01'];bpy.context.window.scene=s;s['support_fix']=True
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Quiosque_20Etapas_v1.blend')
print('Roof support and sink cabinet completed',len(c.objects),'founding objects')
