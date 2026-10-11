import bpy, math
from mathutils import Vector
s=bpy.context.scene
root=bpy.data.collections['MAP_2000x1000_COMERCIO']
roads=bpy.data.collections.new('STREETS_CURVES_CROSSINGS_SIGNAGE'); root.children.link(roads)
asphalt=bpy.data.materials['asphalt_03']; stone=bpy.data.materials['IP_Limestone']; white=bpy.data.materials['IP_Road_Paint']; metal=bpy.data.materials['IP_Bronze']; dark=bpy.data.materials['IP_Window_Recess']; red=bpy.data.materials['SHOP_Berry']; grass=bpy.data.materials['IP_Groundcover']
def material(name,c,emission=0):
    m=bpy.data.materials.new('ROAD_'+name); m.use_nodes=True; m.diffuse_color=(*c,1)
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=.62
    if emission: bs.inputs['Emission Color'].default_value=(*c,1); bs.inputs['Emission Strength'].default_value=emission
    return m
yellow=material('Yellow',(.88,.57,.035)); blue=material('Direction_Blue',(.025,.15,.30)); signred=material('Sign_Red',(.62,.025,.022)); signalred=material('Signal_Red',(1,.018,.01),2); signalgreen=material('Signal_Green',(.018,.65,.08),2)
batch={}; counts={'intersections':0,'crossings':0,'ramps':0}
def geom(name,v,f,m):
    vv,ff,mm=batch.setdefault((name,m.name),([],[],m)); off=len(vv); vv.extend(v); ff.extend(tuple(i+off for i in face) for face in f)
def box(name,p,d,m):
    x,y,z=p; a,b,c=[t*.5 for t in d]
    v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    geom(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def text(body,x,y,z,size,m,flat=False):
    cu=bpy.data.curves.new('ROAD_LABEL_'+body,'FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.extrude=.002
    ob=bpy.data.objects.new('ROAD_LABEL_'+body,cu); roads.objects.link(ob); ob.location=(x,y,z); cu.materials.append(m)
    if not flat: ob.rotation_euler.x=math.pi/2
def plate(x,y,z,r,m,n=32):
    v=[]
    for yy in (y-.018,y+.018):
        for i in range(n):
            a=math.tau*i/n+math.pi/8; v.append((x+r*math.cos(a),yy,z+r*math.sin(a)))
    geom('Traffic_Sign_Plates',v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def stop_sign(x,y):
    box('Sign_Posts',(x,y,1.42),(.075,.075,2.65),metal)
    plate(x,y,2.62,.37,white,8); plate(x,y-.025,2.62,.335,signred,8)
    text('PARE',x,y-.050,2.56,.14,white)
def speed_sign(x,y):
    box('Sign_Posts',(x,y,1.5),(.075,.075,2.8),metal)
    plate(x,y,2.7,.35,signred); plate(x,y-.025,2.7,.29,white)
    text('30',x,y-.052,2.58,.27,dark)
def crosswalk(x,y,direction,width=12,z=.279):
    counts['crossings']+=1
    for i in range(int(width/1.4)):
        offset=-width/2+.7+i*1.4
        if direction=='H': box('Zebra_Crossings',(x+offset,y,z),(.8,3.3,.016),white)
        else: box('Zebra_Crossings',(x,y+offset,z),(3.3,.8,.016),white)
def arrow(x,y,z=.278):
    geom('Lane_Direction_Arrows',[(x-.13,y-1.5,z),(x+.13,y-1.5,z),(x+.13,y+.45,z),(x+.6,y+.45,z),(x,y+1.5,z),(x-.6,y+.45,z),(x-.13,y+.45,z)],[(0,1,2,3,4,5,6)],white)
def accessible_ramp(x,y,sx,sy,z=.28):
    counts['ramps']+=1
    # Actual sloping curb transition, with a tactile warning pad behind it.
    cx=x+sx*6.85; cy=y+sy*14.2
    v=[(cx-.9,cy-.9,z),(cx+.9,cy-.9,z),(cx+.9,cy+.9,z+.22),(cx-.9,cy+.9,z+.22)]
    geom('Curb_Ramps',v,[(0,1,2,3)],stone)
    box('Tactile_Warning_Pads',(cx,cy+1.15,z+.22),(1.65,.5,.025),yellow)
    for i in range(7):
        for j in range(2): box('Tactile_Raised_Dots',(cx-.65+i*.21,cy+1.04+j*.21,z+.245),(.07,.07,.035),yellow)
def rounded_corner(x,y,sx,sy,hx=6,hy=6,z=.27,r=5):
    cx=x+sx*(hx+r); cy=y+sy*(hy+r)
    arc=[]
    for i in range(25):
        a=i*math.pi/48
        arc.append((cx-sx*r*math.cos(a),cy-sy*r*math.sin(a),z))
    # Asphalt fillet physically joins the perpendicular roads around a rounded curb.
    verts=[(x+sx*hx,y+sy*hy,z)]+arc
    geom('Asphalt_Corner_Fillets',verts,[tuple(range(len(verts)))],asphalt)
    for i in range(24):
        a=arc[i]; b=arc[i+1]
        aa=(a[0]+sx*.23,a[1]+sy*.23,z+.22); bb=(b[0]+sx*.23,b[1]+sy*.23,z+.22)
        geom('Rounded_Curbs',[a,b,bb,aa],[(0,1,2,3)],stone)
def junction(x,y,kind='X',coastal=False):
    counts['intersections']+=1
    hy=8 if coastal else 6; z=.228 if coastal else .278
    for sx in (-1,1):
        for sy in ((1,) if kind=='T_N' else ((-1,) if kind=='T_S' else (-1,1))): rounded_corner(x,y,sx,sy,6,hy,z)
    for side in (-1,1): crosswalk(x+side*16,y,'V',hy*2,z+.006)
    if kind!='T_S':
        crosswalk(x,y+17,'H',12,z+.006)
        box('Stop_Lines',(x+3,y+20,z+.006),(5.6,.32,.018),white)
        arrow(x+3,y+25,z+.01)
        stop_sign(x+7.7,y+20)
        accessible_ramp(x,y,1,1,z)
    if kind=='X':
        crosswalk(x,y-17,'H',12,z+.006)
        box('Stop_Lines',(x-3,y-20,z+.006),(5.6,.32,.018),white)
        accessible_ramp(x,y,-1,-1,z)
    if coastal:
        # Static traffic signal model; no traffic simulation or timing logic.
        box('Signal_Poles',(x-8.3,y+14.3,2.4),(.10,.10,4.6),metal)
        box('Signal_Housing',(x-8.3,y+14.3,4.3),(.32,.23,.9),dark)
        plate(x-8.3,y+14.15,4.5,.095,signalred,20)
        plate(x-8.3,y+14.15,4.12,.095,signalgreen,20)
        box('Wayfinding_Panels',(x+9,y+24,2.8),(2,.09,.46),blue)
        box('Sign_Posts',(x+9,y+24,1.55),(.07,.07,2.5),metal)
        text('ORLA  >',x+9,y+23.94,2.74,.18,white)

# Align inland avenues so adjoining districts connect, retaining the original building size.
variants={}
sectors=[o for o in s.objects if o.instance_type=='COLLECTION']
for ob in sectors:
    old=ob.instance_collection
    if old.name not in variants:
        c=bpy.data.collections.new(old.name+'_CONNECTED_ROADS')
        for item in old.objects:
            if not item.name.startswith('Avenue_LaneMark__'): c.objects.link(item)
        for child in old.children: c.children.link(child)
        variants[old.name]=c
    ob.instance_collection=variants[old.name]
    ob.rotation_euler.z=0
    # Raised pedestrian/driveway bridge joins the local street across its former sidewalk gap.
    x=ob.location.x+25; y=ob.location.y-32
    v=[(x-5,y-8,.226),(x+5,y-8,.226),(x+5,y-4,.49),(x-5,y-4,.49),(x-5,y+4,.49),(x+5,y+4,.49),(x+5,y+8,.226),(x-5,y+8,.226)]
    geom('Raised_Street_Connectors',v,[(0,1,2,3),(3,2,5,4),(4,5,6,7)],asphalt)
    crosswalk(x,y,'H',9,.503)
    box('Raised_Crossing_StopLine',(x+2.5,y+10,.239),(4.4,.30,.018),white)
    stop_sign(x+6,y+8)
    # Smooth bridge through the cross-street sidewalk, rather than a hard curb blocking the T.
    yy=ob.location.y+32; xx=ob.location.x+32
    v=[(xx-7,yy-5,.23),(xx-7,yy+5,.23),(xx-2,yy+5,.49),(xx-2,yy-5,.49),(xx+2,yy-5,.49),(xx+2,yy+5,.49),(xx+7,yy+5,.23),(xx+7,yy-5,.23)]
    geom('Raised_CrossStreet_Connectors',v,[(0,1,2,3),(3,2,5,4),(4,5,6,7)],asphalt)

# Perimeter intersections and the coastal T-junctions: 45 junctions across the grid.
for x in range(-800,801,200):
    junction(x,-334,'T_N',True)
    for y in (-190,10,210): junction(x,y,'X')
    junction(x,410,'T_S')
    for low,high in [(-314,-210),(-170,-10),(30,190),(230,390)]:
        for dx in (-.14,.14): box('Double_Yellow_Centerlines',(x+dx,(low+high)/2,.282),(.10,high-low,.016),yellow)

for y in (-334,-134,66,266,-190,10,210,410):
    z=.238 if y in (-334,-134,66,266) else .282
    for x in range(-1000,1000,200):
        for dy in (-.14,.14): box('Double_Yellow_Centerlines',(x+100,y+dy,z),(164,.10,.016),yellow)
for x in range(-900,901,200): speed_sign(x-15,-322)

for (name,mname),(v,f,m) in batch.items():
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.materials.append(m); me.update()
    ob=bpy.data.objects.new('STREET_'+name+'__'+mname,me); roads.objects.link(ob)
    uv=me.uv_layers.new(name='WorldMeters')
    for p in me.polygons:
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=(co.x*.25,co.y*.25)

for name,loc,target,lens in [
    ('STREET_COAST_JUNCTION',(32,-373,19),(0,-327,0),30),
    ('STREET_GRID_JUNCTION',(24,-24,55),(0,10,0),40),
    ('STREET_PEDESTRIAN',(14,-354,1.72),(-3,-328,1.7),27)]:
    data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); root.objects.link(ob); ob.location=loc; data.lens=lens; data.clip_end=15000
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
s['junctions_with_rounded_curbs']=counts['intersections']; s['new_zebra_crossings']=counts['crossings']; s['curb_ramps']=counts['ramps']
s['street_note']='Aligned district arteries, geometric fillets and raised street connectors; signs and signals are static scenery.'
s.camera=bpy.data.objects['STREET_COAST_JUNCTION']
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Comercio_Ruas.blend')
print('STREETS_SAVED',counts)
