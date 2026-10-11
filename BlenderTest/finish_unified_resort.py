import bpy,math,random
from mathutils import Vector
random.seed(8)
c=bpy.data.collections['UNIDA_20_RESORT_UNICO'];wood=bpy.data.materials['MARE_Teak_Existing_PBR'];teal=bpy.data.materials['MARE_Painted_Teal'];cream=bpy.data.materials['MARE_Linen_Canvas'];brass=bpy.data.materials['MARE_Brushed_Brass'];leaf=bpy.data.materials['MARE_Leaf_Green'];lightleaf=bpy.data.materials['MARE_Leaf_Sunlit'];water=bpy.data.materials['MARE_Pool_Water'];curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete']
def mesh(name,vs,fs,mat,c):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);uv=me.uv_layers.new(name='UrbanMeters');wg=me.uv_layers.new(name='WoodGrain')
    for f in me.polygons:
        axes=[k for k in range(3) if k!=max((abs(f.normal[j]),j) for j in range(3))[1]]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]]);wg.data[li].uv=uv.data[li].uv
    o=bpy.data.objects.new(name,me);c.objects.link(o);return o
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];a,b,d=loc
    return mesh(name,[(a-x,b-y,d-z),(a+x,b-y,d-z),(a+x,b+y,d-z),(a-x,b+y,d-z),(a-x,b-y,d+z),(a+x,b-y,d+z),(a+x,b+y,d+z),(a-x,b+y,d+z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,c)
# Remove the earlier floating garden and replace it with roof-supported terraces.
for o in list(c.objects):
    if 'Roof_Garden_' in o.name:bpy.data.objects.remove(o,do_unlink=True)
for x,y,z in [(-21,8,10.28),(21,8,10.28),(40,24,6.98),(-23,48,3.88)]:
    box('UNIDA_Roof_Planter',(x,y,z),(3,8,.42),wood,c)
    for j in range(14):
        xx=x+random.uniform(-1.2,1.2);yy=y+random.uniform(-3.6,3.6)
        for k in range(8):
            a=k*math.tau/8;r=.4+random.random()*.2;top=z+.45+random.random()*.28
            mesh('UNIDA_Dense_Garden_Leaf',[(xx,yy,z+.2),(xx+r*math.cos(a-.25),yy+r*math.sin(a-.25),top),(xx+r*1.4*math.cos(a),yy+r*1.4*math.sin(a),top-.05),(xx+r*math.cos(a+.25),yy+r*math.sin(a+.25),top)],[(0,1,2,3)],leaf if k%3 else lightleaf,c)
# Balcony rhythm, privacy screens and planters share the same final facade.
for level in range(3):
    z=.45+level*3.2
    for x in range(-27,28,6):
        for j in range(6):box('UNIDA_Balcony_Teak_Privacy',(x+j*.12,-21.60,z+1.45),(.055,1.1,2.6),wood,c)
        box('UNIDA_Balcony_Planter',(x+2,-22.2,z+.26),(.9,.3,.45),teal,c)
        for j in range(6):
            a=j*1.1;xx=x+2;yy=-22.2
            mesh('UNIDA_Balcony_Plant',[(xx,yy,z+.5),(xx+.35*math.cos(a),yy+.15*math.sin(a),z+.9),(xx+.45*math.cos(a+.2),yy+.15*math.sin(a+.2),z+.75)],[(0,1,2)],leaf,c)
# Supported rooftop pool and lounge make the roof a usable terrace.
box('UNIDA_Rooftop_Pool_Base',(-21,-6,10.20),(12,7,.28),teal,c)
box('UNIDA_Rooftop_Pool_Water',(-21,-6,10.36),(11.6,6.6,.045),water,c)
for x in [-27,-15]:box('UNIDA_Rooftop_Pool_Edge',(x,-6,10.42),(.25,7.5,.24),curb,c)
for y in [-9.7,-2.3]:box('UNIDA_Rooftop_Pool_Edge',(-21,y,10.42),(12.3,.25,.24),curb,c)
for x in [15,27]:
    for y in [-15,5]:box('UNIDA_Rooftop_Pergola_Post',(x,y,11.45),(.16,.16,2.8),wood,c)
for y in [-15,5]:box('UNIDA_Rooftop_Pergola_Beam',(21,y,12.84),(12.7,.22,.20),wood,c)
for j in range(11):
    x=15+j*1.2
    box('UNIDA_Rooftop_Rafter',(x,-5,12.88),(.09,21,.16),wood,c)
    pts=[(x-.42,-15,12.8),(x+.42,-15,12.8),(x+.42,-5,12.43),(x-.42,-5,12.43),(x-.42,5,12.8),(x+.42,5,12.8)]
    mesh('UNIDA_Sagged_Canvas_Shade',pts,[(0,1,2,3),(3,2,5,4)],cream,c)
source=bpy.data.collections['MARE_11_PISCINA']
lounge=bpy.data.collections.new('UNIDA_ROOF_LOUNGER_ASSET')
for o in source.objects:
    if 'Lounger' in o.name and -34<o.location.x<-32 and o.location.y<20:lounge.objects.link(o)
for x in [17,21,25]:
    for y in [-11,-4]:
        o=bpy.data.objects.new('UNIDA_Rooftop_Lounger',None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=lounge;o.location=(x+33,y-17,9.9)
# Roof parapets and railings trace connected guest wings.
for x in [-30,30]:
    box('UNIDA_Roof_Glass_Parapet',(x,-3,10.58),(.04,36,1),bpy.data.materials['MARE_Architectural_Glass'],c)
    box('UNIDA_Roof_Top_Rail',(x,-3,11.10),(.055,36,.055),brass,c)
box('UNIDA_Roof_Front_Parapet',(0,-21,10.56),(60,.04,1),bpy.data.materials['MARE_Architectural_Glass'],c)
box('UNIDA_Roof_Front_Rail',(0,-21,11.10),(60,.055,.055),brass,c)
# Founding hotel lobby stays a lobby: upper-floor rooms retain their beds.
base=bpy.data.collections['UNIDA_06_HOTEL_SIMPLES']
for o in list(base.objects):
    if any(t in o.name for t in ['Bed_','Pillow']) and o.location.z<3:bpy.data.objects.remove(o,do_unlink=True)
for x in [-7,7]:box('UNIDA_Lobby_Sofa',(x,-13,.85),(2.6,.95,.8),cream,base)
# Fuller instanced palm crowns for the entire waterfront.
palms=bpy.data.collections['MARE_PALM_REUSABLE']
for o in list(palms.objects):
    if 'Palm_Leaflet' in o.name:bpy.data.objects.remove(o,do_unlink=True)
vs=[[],[]];fs=[[],[]];origin=Vector((.3,.15,8))
for j in range(23):
    a=j*math.tau/23;length=3.2+random.random()*.9
    for k in range(1,20):
        t=k/20;p=origin+Vector((math.cos(a)*length*t,math.sin(a)*length*t,1.5*math.sin(math.pi*t)-1.2*t*t))
        for side in [-1,1]:
            aa=a+side*1.0;long=.75*math.sin(math.pi*t)+.22;end=p+Vector((math.cos(aa)*long,math.sin(aa)*long,-.30*long));perp=Vector((-math.sin(aa)*.055,math.cos(aa)*.055,0));middle=p.lerp(end,.55);idx=j%2;offset=len(vs[idx]);vs[idx].extend([tuple(p),tuple(middle+perp),tuple(end),tuple(middle-perp)]);fs[idx].append((offset,offset+1,offset+2,offset+3))
for idx in range(2):mesh('UNIDA_Full_Palm_Crown',vs[idx],fs[idx],leaf if idx==0 else lightleaf,palms)
for o in c.objects:o['unlock_stage']=20;o['module_id']='mare_unified_20'
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Unificada_v2.blend')
print('Unified resort facade, connected roof terrace and palm crowns refined')
