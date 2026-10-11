import bpy, math, random
from mathutils import Vector
random.seed(40)
s=bpy.context.scene; col=bpy.data.collections['IPANEMA_NEW_MAP_200x200']; batch={}
stone=bpy.data.materials['IP_Limestone']; grass=bpy.data.materials['IP_Groundcover']; wood=bpy.data.materials['IP_Teak']; metal=bpy.data.materials['IP_Bronze']; leaf=bpy.data.materials['IP_Leaf']; leaf2=bpy.data.materials['IP_Leaf_Sunlit']; trunk=bpy.data.materials['IP_Bark']; glass=bpy.data.materials['IP_Glass']; dark=bpy.data.materials['IP_Window_Recess']
def geom(name,v,f,m):
    vv,ff,mm=batch.setdefault((name,m.name),([],[],m)); off=len(vv); vv.extend(v); ff.extend(tuple(i+off for i in face) for face in f)
def box(name,loc,dims,m):
    x,y,z=loc; a,b,c=[t*.5 for t in dims]
    v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    geom(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def rod(name,a,b,r,m,n=10):
    a=Vector(a); b=Vector(b); q=(b-a).to_track_quat('Z','Y'); v=[]
    for p in (a,b):
        for i in range(n): v.append(tuple(p+q@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),0))))
    geom(name,v,[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def leafy(x,y,h=5):
    rod('GardenTrees',(x,y,.4),(x,y,h*.75),.15,trunk,16)
    for j in range(9):
        a=j*math.tau/9; center=Vector((x+math.cos(a)*1.2,y+math.sin(a)*1.2,h*.8+random.uniform(-.4,.6)))
        rod('GardenTrees',(x,y,h*.5),tuple(center),.055,trunk,10)
        for i in range(45):
            p=center+Vector((random.uniform(-1.1,1.1),random.uniform(-1.1,1.1),random.uniform(-.65,.7)))
            angle=random.random()*math.tau; t=Vector((math.cos(angle),math.sin(angle),0)); q=Vector((-math.sin(angle),math.cos(angle),.25))
            geom('GardenLeaves',[tuple(p-t*.18),tuple(p+q*.09),tuple(p+t*.18),tuple(p-q*.09)],[(0,1,2),(0,2,3)],leaf if i%3 else leaf2)
def shrubs(x,y,w,d):
    box('GardenBeds',(x,y,.34),(w,d,.22),grass)
    for j in range(int(w*d*7)):
        p=Vector((x+random.uniform(-w*.48,w*.48),y+random.uniform(-d*.48,d*.48),random.uniform(.6,1.2)))
        for a in range(3):
            t=Vector((math.cos(a*2.1)*.23,math.sin(a*2.1)*.23,0)); q=Vector((-math.sin(a*2.1)*.08,math.cos(a*2.1)*.08,.10))
            geom('ShrubLeaves',[tuple(p-t),tuple(p+q),tuple(p+t),tuple(p-q)],[(0,1,2),(0,2,3)],leaf if j%4 else leaf2)

# Repair closed pool basin: actual frame, bottom and visible water surface.
ob=bpy.data.objects['Pool_Basin__IP_Limestone']; ob.hide_render=True; ob.hide_set(True)
for x in (-59.15,-36.85): box('Pool_Coping',(x,23,.71),(1.15,27,.28),stone)
for y in (9.85,36.15): box('Pool_Coping',(-48,y,.71),(21.4,1.15,.28),stone)
for x in (-58.2,-37.8):
    for yy in (10.7,13.0): rod('Pool_Ladder',(x,yy,.7),(x,yy,1.5),.025,metal,12)

# Garden and walking route between hotel and city; occupied lots, clear paths.
box('Resort_Garden',(-6,34,.31),(38,42,.22),grass)
box('Garden_Walkway',(-6,34,.49),(4,42,.14),stone)
box('Garden_Crosswalk',(-6,34,.49),(38,3,.14),stone)
for x in (-19,7):
    for y in (18,29,42,51): shrubs(x,y,5,3); leafy(x,y,4.5+random.random())
for y in (20,46):
    box('Garden_Bench',(-2,y,.9),(1.8,.6,.13),wood)
    box('Garden_Bench',(-2,y+.25,1.25),(1.8,.12,.5),wood)
    for dx in (-.7,.7): box('Garden_Bench',(-2+dx,y,.63),(.1,.5,.6),metal)
box('Restaurant_Terrace',(-43,48,.49),(27,6,.18),stone)
for x in (-53,-43,-33):
    rod('Restaurant_Tables',(x,48,.5),(x,48,1.2),.04,metal)
    rod('Restaurant_Tables',(x,48,1.2),(x,48,1.28),.6,wood,32)
    for dx in (-.85,.85): box('Restaurant_Seats',(x+dx,48,.85),(.5,.55,.16),wood)
for x in (-57,-29): shrubs(x,49,2,5)
for x in (-89,-72,-55,-38,-20,1): shrubs(x,91,6,3)
for x,y in [(-80,57),(-91,57),(-33,84),(6,90),(-16,-27),(15,-27)]: leafy(x,y,5.5)

# West hotel's pool-facing elevation: reveals, metal frames and sun-breakers.
for z in (5,8,11,14):
    for yy in (6,10,14,18,22,26,30,34,38):
        for dy in (-.97,.97): box('Aurora_SideFrames',(-76.40,yy+dy,z),(.16,.10,2.1),metal)
        box('Aurora_SideFrames',(-76.40,yy,z+1.04),(.35,2.05,.10),stone)
        box('Aurora_SideFrames',(-76.40,yy,z-1.04),(.35,2.05,.10),stone)
        for dy in (-1.24,1.24): box('Aurora_Sunscreens',(-76.2,yy+dy,z),(.60,.10,2.8),wood)
for x in (-87,-77,-67,-57,-47): shrubs(x,-29,4,1.5)

# Thicker palm leaflets; retain curved ribs and detailed trunks.
for ob in s.objects:
    if ob.name.startswith('Palms_Leaflets__'):
        me=ob.data
        for poly in me.polygons:
            ids=list(poly.vertices)
            if len(ids)==4:
                base=(me.vertices[ids[0]].co+me.vertices[ids[1]].co)*.5
                tip=(me.vertices[ids[2]].co+me.vertices[ids[3]].co)*.5
                for i in ids[:2]: me.vertices[i].co=base+(me.vertices[i].co-base)*2
                for i in ids[2:]: me.vertices[i].co=tip+(me.vertices[i].co-tip)*2.5

# Shade structures on terraces.
for x in (-62,-42):
    for y in (2,43):
        for dx in (-2,2):
            for dy in (-1.2,1.2): rod('Pool_Cabanas',(x+dx,y+dy,.4),(x+dx,y+dy,3.2),.07,wood,12)
        for j in range(13): box('Pool_Cabanas',(x-2.2+j*.36,y,3.3),(.18,3,.12),wood)

for (name,mname),(v,f,m) in batch.items():
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.materials.append(m); me.update()
    ob=bpy.data.objects.new(name+'__'+mname,me); col.objects.link(ob)
    uv=me.uv_layers.new(name='WorldMeters')
    for p in me.polygons:
        axis=0
        if abs(p.normal.y)>abs(p.normal.x): axis=1
        if abs(p.normal.z)>abs(p.normal[axis]): axis=2
        for i in p.loop_indices:
            co=me.vertices[me.loops[i].vertex_index].co
            uv.data[i].uv=(co.y*.25,co.z*.25) if axis==0 else ((co.x*.25,co.z*.25) if axis==1 else (co.x*.25,co.y*.25))
    if name in ('Garden_Walkway','Garden_Crosswalk','Restaurant_Terrace'): ob.data.materials[0]=bpy.data.materials['checkered_pavement_tiles']

for n in bpy.data.materials['checkered_pavement_tiles'].node_tree.nodes:
    if n.type=='MAPPING': n.inputs['Scale'].default_value=(2,2,2)
bpy.data.lights['IP_Sun'].energy=1.3
for n in s.world.node_tree.nodes:
    if n.type=='BACKGROUND': n.inputs['Strength'].default_value=.85
s.view_settings.exposure=.25
cam=bpy.data.objects['IP_Pool']; cam.location=(-25,5,2.1); cam.rotation_euler=(Vector((-51,25,3.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=25
s.camera=bpy.data.objects['IP_Aerial']; s.render.resolution_percentage=100; s.cycles.samples=40
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_NEW_200x200.blend')
print('REFINED',len(s.objects),'objects')
