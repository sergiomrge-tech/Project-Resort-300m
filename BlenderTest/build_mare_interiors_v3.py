import bpy, math, random, json
from mathutils import Vector
random.seed(40)
OUT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
if bpy.data.collections.get('INTERIOR_06_LOBBY'):raise RuntimeError('Interior pass already installed')
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];teal=bpy.data.materials['MARE_Painted_Teal'];linen=bpy.data.materials['MARE_Linen_Canvas'];steel=bpy.data.materials['MARE_Brushed_Stainless'];brass=bpy.data.materials['MARE_Brushed_Brass'];glass=bpy.data.materials['MARE_Architectural_Glass'];plaster=bpy.data.materials['URBAN_PBR_IP_Ivory_Painted_Render'];dark=bpy.data.materials['MARE_Charcoal']
def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
ceramic=material('INTERIOR_Glazed_Ivory_Ceramic',(.86,.82,.72),.18)
coral=material('INTERIOR_Coral_Upholstery',(.42,.105,.068),.85)
navy=material('INTERIOR_Deep_Sea_Fabric',(.015,.09,.105),.82)
mirror=material('INTERIOR_Polished_Mirror',(.8,.82,.85),.03,1)
floor=material('INTERIOR_Travertine_Honed',(.5,.43,.32),.4)
nt=floor.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=4;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.035;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
lamp=material('INTERIOR_Warm_Lamp_Diffuser',(1,.65,.30),.5);p=next(n for n in lamp.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Color'].default_value=(1,.61,.25,1);p.inputs['Emission Strength'].default_value=2
allcols=[];rooms=[];stations=[]
def collection(name,stage=0,last=20):
    c=bpy.data.collections.new('INTERIOR_'+name);c['unlock_stage']=stage;c['last_stage']=last;allcols.append(c)
    if stage:
        for i in range(stage,last+1):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(c)
    return c
def box(name,loc,size,mat,c,bevel=.015):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new('INT_'+name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    for uvname in ['UrbanMeters','WoodGrain']:
        uv=me.uv_layers.new(name=uvname)
        for f in me.polygons:
            axis=max((abs(f.normal[j]),j) for j in range(3))[1];axes=[j for j in range(3) if j!=axis]
            for li in f.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
    o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc
    if bevel:m=o.modifiers.new('Soft finished edges','BEVEL');m.width=bevel;m.segments=3
    return o
def cylinder(name,loc,radius,depth,mat,c,vertices=24):
    vs=[]
    for z in [-depth/2,depth/2]:
        for i in range(vertices):a=i*math.tau/vertices;vs.append((radius*math.cos(a),radius*math.sin(a),z))
    fs=[tuple(reversed(range(vertices))),tuple(range(vertices,2*vertices))]
    for i in range(vertices):j=(i+1)%vertices;fs.append((i,j,j+vertices,i+vertices))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat)
    for f in me.polygons:f.use_smooth=len(f.vertices)==4
    o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;return o
def text(name,body,loc,size,c,mat=brass):
    d=bpy.data.curves.new('INT_'+name,'FONT');d.body=body;d.size=size;d.align_x='CENTER';d.extrude=.001;o=bpy.data.objects.new('INT_'+name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(mat);return o
def light(name,loc,energy,c,size=2):
    d=bpy.data.lights.new('INT_'+name,'AREA');d.energy=energy;d.color=(1,.81,.62);d.shape='DISK';d.size=size;o=bpy.data.objects.new('INT_'+name,d);c.objects.link(o);o.location=loc;return o
def instance(name,asset,c,loc,rotation=0):
    o=bpy.data.objects.new('INT_'+name,None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=asset;o.location=loc;o.rotation_euler.z=rotation;return o
def socket(name,loc,kind,c):
    o=bpy.data.objects.new('GAME_'+name,None);c.objects.link(o);o.location=loc;o.empty_display_type='SPHERE';o.empty_display_size=.12;o['interaction_type']=kind;o['runtime_implemented']=False;stations.append({'id':o.name,'type':kind,'position':list(loc),'collection':c.name});return o
def plant(c,x,y,z):
    cylinder('Planter',(x,y,z+.27),.24,.52,ceramic,c)
    for i in range(11):
        a=i*2.4;ob=box('Leaf',(x+.16*math.cos(a),y+.16*math.sin(a),z+.70+i*.025),(.11,.48,.025),teal,c,.015);ob.rotation_euler=(.5*math.cos(a),.4*math.sin(a),a)
def chair(c,x,y,z,rotation=0):
    asset=chairasset;return instance('Dining_Chair',asset,c,(x,y,z),rotation)
chairasset=collection('ASSET_DINING_CHAIR')
box('Chair_Cushion',(0,0,.48),(.48,.47,.12),linen,chairasset,.05);box('Chair_Back',(0,.22,.77),(.49,.065,.46),wood,chairasset,.035)
for x in [-.19,.19]:
    for y in [-.18,.18]:box('Chair_Leg',(x,y,.23),(.045,.045,.46),wood,chairasset)
def sofa(c,x,y,z,w=2.5):
    box('Sofa_Base',(x,y,z+.24),(w,.9,.38),wood,c,.03);box('Sofa_Back',(x,y+.38,z+.60),(w,.16,.65),navy,c,.05)
    for j in range(3):box('Sofa_Cushion',(x-w/3+j*w/3,y,z+.48),(w/3-.03,.73,.18),linen,c,.065)
    for dx in [-w/2+.1,w/2-.1]:box('Sofa_Arm',(x+dx,y,z+.51),(.18,.94,.52),navy,c,.04)
def table(c,x,y,z):
    box('Dining_Top',(x,y,z+.76),(1.1,1.1,.075),wood,c,.025);cylinder('Dining_Base',(x,y,z+.37),.11,.70,brass,c);cylinder('Dining_Foot',(x,y,z+.055),.36,.075,brass,c)
    for dx in [-.34,.34]:
        cylinder('Plate',(x+dx,y,z+.816),.16,.018,ceramic,c);cylinder('Water_Glass',(x+dx,y+.3,z+.89),.035,.14,glass,c)
        box('Napkin',(x+dx,y-.22,z+.82),(.17,.22,.013),linen,c);box('Knife',(x+dx+.2,y,z+.823),(.016,.23,.012),steel,c)
    cylinder('Table_Vase',(x,y+.20,z+.88),.045,.14,ceramic,c)
    for dx,dy,a in [(0,-.85,0),(0,.85,math.pi),(-.85,0,-math.pi/2),(.85,0,math.pi/2)]:chair(c,x+dx,y+dy,z,a)
def sink(c,x,y,z):
    box('Vanity_Cabinet',(x,y,z+.43),(1.0,.55,.8),wood,c,.03)
    # Basin cavity is built from rim panels, not a solid white cube.
    for xx in [-.40,.40]:box('Basin_Side',(x+xx,y,z+.87),(.10,.5,.13),ceramic,c)
    for yy in [-.21,.21]:box('Basin_Rim',(x,y+yy,z+.87),(.75,.08,.13),ceramic,c)
    box('Basin_Bottom',(x,y,z+.81),(.75,.36,.025),ceramic,c);cylinder('Basin_Drain',(x,y,z+.825),.035,.008,steel,c)
    cylinder('Faucet_Stem',(x,y+.21,z+1.03),.025,.28,steel,c);box('Faucet_Spout',(x,y+.10,z+1.17),(.05,.25,.045),steel,c)
    box('Mirror',(x,y+.31,z+1.63),(.92,.025,.72),mirror,c,.03)
def toilet(c,x,y,z):
    cylinder('WC_Pedestal',(x,y,z+.19),.17,.38,ceramic,c);o=cylinder('WC_Bowl',(x,y,z+.43),.24,.14,ceramic,c);o.scale.y=1.25
    o=cylinder('WC_Seat',(x,y-.035,z+.52),.245,.045,ceramic,c);o.scale.y=1.27
    box('WC_Cistern',(x,y+.3,z+.73),(.48,.18,.50),ceramic,c,.05);box('WC_Flush',(x,y+.2,z+.93),(.08,.015,.04),steel,c)
def bathroom(c,x,y,z):
    sink(c,x,y-.7,z);toilet(c,x+.60,y+.25,z)
    box('Shower_Tray',(x-.55,y+1.0,z+.05),(1.12,1.05,.10),ceramic,c,.03)
    box('Shower_Glass',(x-.55,y+.48,z+1.15),(1.15,.02,2.2),glass,c,0)
    box('Shower_Arm',(x-.55,y+1.35,z+2.2),(.035,.4,.035),steel,c);cylinder('Shower_Head',(x-.55,y+1.1,z+2.17),.10,.025,steel,c)
    box('Towel_Rail',(x+1,y-.3,z+1.10),(.025,.5,.035),brass,c);box('Folded_Towel',(x+.99,y-.3,z+.94),(.035,.45,.32),linen,c)
    for j in range(2):cylinder('Amenity_Bottle',(x-.22+j*.13,y-.67,z+1.0),.035,.17,teal,c)
# Fully reusable en-suite room, 6 x 7 m; circulation door faces local +Y.
roomasset=collection('ASSET_ENSUITE_ROOM')
box('Room_Floor',(0,0,.10),(5.86,6.88,.035),wood,roomasset,0)
for x in [-2.96,2.96]:box('Party_Wall',(x,0,1.46),(.12,7,2.8),plaster,roomasset)
# Door opening at x -1.4; open door leaf stays inside the vestibule.
for x,w in [(-2.5,.9),(.85,4.2)]:box('Corridor_Wall',(x,3.45,1.46),(w,.12,2.8),plaster,roomasset)
box('Door_Lintel',(-1.4,3.45,2.61),(1.3,.14,.50),wood,roomasset);o=box('Open_Entry_Door',(-2.04,2.86,1.22),(.065,1.17,2.2),wood,roomasset);box('Door_Handle',(-1.985,2.55,1.05),(.065,.15,.035),brass,roomasset)
box('Bed_Platform',(-.55,-1.6,.29),(1.96,2.18,.38),wood,roomasset,.04);box('Mattress',(-.55,-1.6,.56),(1.86,2.08,.25),linen,roomasset,.09)
box('Headboard',(-.55,-2.69,1.1),(2.6,.12,1.6),navy,roomasset,.04)
for x in [-1.0,-.1]:box('Pillow',(x,-2.2,.76),(.75,.45,.18),linen,roomasset,.08)
box('Bed_Throw',(-.55,-.90,.705),(1.9,.62,.045),coral,roomasset,.025)
for x in [-1.90,.8]:
    box('Nightstand',(x,-2.25,.41),(.48,.5,.62),wood,roomasset,.03);cylinder('Bed_Lamp_Stem',(x,-2.25,.86),.025,.30,brass,roomasset);cylinder('Bed_Lamp_Shade',(x,-2.25,1.07),.16,.23,lamp,roomasset)
box('Bathroom_South_Wall',(1.65,.35,1.46),(2.5,.12,2.8),plaster,roomasset)
for y,h in [(.6,.5),(2.5,1.9)]:box('Bathroom_West_Wall',(.38,y,1.46),(.12,h,2.8),plaster,roomasset)
box('Bathroom_Lintel',(.38,1.32,2.60),(.14,1.0,.5),plaster,roomasset)
bathroom(roomasset,1.7,1.35,.10)
box('Wardrobe',(-2.3,2.20,1.18),(1.02,1.1,2.15),wood,roomasset,.025)
for x in [-2.55,-2.05]:box('Wardrobe_Handle',(x,1.635,1.20),(.025,.045,.30),brass,roomasset)
box('Minibar',(-2.3,.8,.60),(1,.65,1),teal,roomasset,.025);box('Minibar_Door',(-2.3,.465,.60),(.90,.03,.83),glass,roomasset)
box('Luggage_Bench',(-2.3,-.1,.34),(1,.6,.50),wood,roomasset)
box('Wall_TV',(-2.875,-1.9,1.65),(.06,1.1,.65),dark,roomasset);text('Welcome_Card','MARÉ',(-2.3,.45,1.3),.12,roomasset)
box('Curtain_Left',(-2.6,-3.33,1.52),(.5,.06,2.75),linen,roomasset);box('Curtain_Right',(2.6,-3.33,1.52),(.5,.06,2.75),linen,roomasset)
box('Ceiling_Panel',(0,0,2.94),(5.87,6.85,.045),linen,roomasset,0);cylinder('Room_Ceiling_Lamp',(0,-.4,2.88),.26,.055,lamp,roomasset);light('Room_Warm_Light',(0,-.4,2.83),75,roomasset,1.4)
plant(roomasset,2.25,-2.8,.1);socket('Guest_Bed',(-.55,-.5,.6),'housekeeping_bed',roomasset);socket('Guest_Minibar',(-2.3,.4,.6),'restock_minibar',roomasset)
def addroom(c,name,x,y,z,rot=0):
    o=instance(name,roomasset,c,(x,y,z),rot);o['room_id']=name;o['service_state']='requires_runtime';rooms.append({'id':name,'collection':c.name,'position':[x,y,z],'rotation':rot,'template':'en_suite_6x7'})
def corridor(c,x,y,z,w,d):
    box('Hall_Runner',(x,y,z+.115),(w,d,.025),navy,c,0)
    for j in range(max(1,int(d/5))):light('Hall_Light',(x,y-d/2+2+j*5,z+2.78),45,c,1)
# Remove old disconnected beds; replace with room assemblies without changing exterior dimensions.
for cname in ['UNIDA_06_HOTEL_SIMPLES','UNIDA_07_ALA_ESQUERDA','UNIDA_08_ALA_DIREITA','UNIDA_16_SUITES_PRIVATIVAS','UNIDA_19_AMPLIACAO_VERTICAL','UNIDA_20_RESORT_UNICO']:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if any(t in o.name for t in ['Bed_','Pillow']):bpy.data.objects.remove(o,do_unlink=True)
hotelrooms=collection('06_QUARTOS_HOTEL',6)
for j,x in enumerate([-9,-3,3,9]):addroom(hotelrooms,'H101_%d'%j,x,-16,3.65)
corridor(hotelrooms,0,-10.25,3.65,23,3.3)
for j,x in enumerate([-3,3]):addroom(hotelrooms,'H105_%d'%j,x,-3,3.65,math.pi)
for stage,x,label in [(7,-21,'J'),(8,21,'O'),(19,-21,'PJ'),(20,21,'PO')]:
    c=collection('%02d_QUARTOS_%s'%(stage,label),stage)
    for z in ([.45,3.65] if stage<19 else [6.85]):
        corridor(c,x,-3,z,2.65,35)
        for j,y in enumerate([-16,-9,-2,5,12]):
            for dx,r in [(-5,-math.pi/2),(5,math.pi/2)]:addroom(c,label+'_%s_%d_%s'%(z,j,dx),x+dx,y,z,r)
upper=collection('19_QUARTOS_CENTRO',19)
for j,x in enumerate([-9,-3,3,9]):addroom(upper,'PREMIUM_C%d'%j,x,-16,6.85)
corridor(upper,0,-10.25,6.85,23,3.3)
for j,x in enumerate([-3,3]):addroom(upper,'PREMIUM_REAR%d'%j,x,-3,6.85,math.pi)
suites=collection('16_QUARTOS_SPA',16)
for j,x in enumerate([33.4,40,46.6]):addroom(suites,'SPA_SUITE_%d'%j,x,16.8,3.65)
corridor(suites,40,22,3.65,19,2.4)
for x in [33.4,40,46.6]:sofa(suites,x,28,3.75,3);box('Suite_Coffee_Table',(x,26,4.10),(1.2,.8,.32),wood,suites)
# Lobby circulation stays clear on the central axis, between entry and rear restaurant.
lobby=collection('06_LOBBY',6)
base=bpy.data.collections['UNIDA_06_HOTEL_SIMPLES']
for o in list(base.objects):
    if any(t in o.name for t in ['Front_Reception','Lobby_Welcome','Lobby_Sofa']):bpy.data.objects.remove(o,do_unlink=True)
box('Lobby_Floor',(0,-9,.545),(23.65,23.6,.025),floor,lobby,0)
box('Reception_Base',(-5,-14,1.04),(5.6,1.15,1.05),wood,lobby,.06);box('Reception_Stone_Top',(-5,-14,1.60),(5.7,1.24,.11),ceramic,lobby,.025)
for j in range(37):box('Reception_Slat',(-7.65+j*.15,-14.59,1.06),(.045,.055,.86),wood,lobby)
text('Reception_Brand','MARÉ',(-5,-14.64,1.11),.37,lobby)
for x in [-6.6,-3.6]:box('Reception_Monitor',(x,-14.1,1.91),(.48,.07,.30),dark,lobby);box('Monitor_Foot',(x,-14.1,1.70),(.22,.16,.06),steel,lobby)
socket('Check_In',(-5,-16,1),'check_in_checkout',lobby)
for x in [-7,7]:
    sofa(lobby,x,-18,.55,3.1);box('Lobby_Coffee_Table',(x,-19.3,.90),(1.5,.65,.40),wood,lobby);plant(lobby,x+1.8,-18,.55)
box('Concierge_Desk',(7,-12,1.1),(2.7,.8,1.1),wood,lobby);socket('Concierge',(7,-13.5,1),'guest_requests',lobby)
box('Luggage_Rack',(-10,-9,1.1),(1.8,.6,1.15),brass,lobby)
for x in [-10.5,-9.9,-9.3]:box('Suitcase',(x,-9,1.0),(.45,.4,.70),navy,lobby,.07)
box('Lobby_Backdrop',(-5,-12.8,2.0),(6,.10,2.75),teal,lobby);text('Lobby_Logo','MARÉ HOTEL',(-5,-12.87,2.3),.35,lobby)
for x in [-9,-3,3,9]:light('Lobby_Ceiling_Light',(x,-16,3.35),110,lobby,2)
for x in [-10,10]:plant(lobby,x,-5,.55)
text('Restaurant_Direction','RESTAURANTE  →',(0,2.8,2.75),.18,lobby)
# Original restaurant and rear restaurant get matching food-service layouts.
def kitchen(c,x,y,z,width=7):
    box('Kitchen_Floor',(x,y,z+.10),(width,5.8,.03),floor,c,0)
    for xx in [x-width/2,x+width/2]:box('Kitchen_Wall',(xx,y,z+1.5),(.12,6,2.8),plaster,c)
    for dx in [-2,0,2]:
        box('Prep_Unit',(x+dx,y+1.6,z+.50),(1.8,.78,.86),steel,c,.025);box('Prep_Worktop',(x+dx,y+1.6,z+.98),(1.86,.84,.055),steel,c)
        box('Drawer_Line',(x+dx,y+1.18,z+.58),(1.67,.015,.015),dark,c)
        for h in [.25,.55,.8]:box('Drawer_Handle',(x+dx,y+1.16,z+h),(.27,.045,.024),steel,c)
    box('Commercial_Range',(x-2,y-1.8,z+.55),(1.6,.9,1),steel,c)
    for dx in [-.45,.45]:
        for dy in [-.23,.23]:cylinder('Range_Burner',(x-2+dx,y-1.8+dy,z+1.07),.14,.025,dark,c)
    box('Extraction_Hood',(x-2,y-1.8,z+2.10),(1.9,1.15,.35),steel,c)
    box('Extraction_Duct',(x-2,y-1.8,z+2.57),(.5,.45,.6),steel,c)
    box('Upright_Fridge',(x+2,y-1.8,z+1.25),(1.2,.85,2.3),steel,c,.035)
    for dx in [-.28,.28]:box('Fridge_Handle',(x+2+dx,y-2.25,z+1.35),(.035,.055,.60),steel,c)
    box('Pass_Counter',(x,y-2.8,z+.95),(2.8,.65,.12),steel,c);text('Kitchen_Pass','PASSE',(x,y-2.85,z+1.8),.15,c)
    socket('Cook',(x-2,y-.5,z+.5),'cook_orders',c);socket('Pass',(x,y-3.5,z+.5),'serve_orders',c);socket('Prep',(x,y+.5,z+.5),'prepare_food',c)
    light('Kitchen_Light',(x,y,z+2.85),180,c,3)
def restaurant(c,cy,z=0.45):
    # Wide central circulation, tables on both sides.
    for x in [-6,-2.8,2.8,6]:
        for y in [cy-2.5,cy+1]:table(c,x,y,z+.10)
    kitchen(c,6.1,cy+7,z,7)
    for x in [-7.5,0,7.5]:
        cylinder('Restaurant_Pendant',(x,cy,3.07+z),.30,.20,lamp,c);light('Dining_Light',(x,cy,2.95+z),90,c,2)
    box('Host_Stand',(-7.8,cy-6,z+.63),(1.3,.7,1.0),wood,c);socket('Restaurant_Host',(-7.8,cy-7,z+.5),'seat_guests',c)
    for x in [-8.5,8.5]:plant(c,x,cy-5,z+.10)
initial=collection('04_RESTAURANT_INTERIOR',4,5);restaurant(initial,-9)
rear=collection('06_REAR_RESTAURANT_INTERIOR',6);restaurant(rear,14)
# Remove loose prototype tables/kitchen instances so new floor plan is coherent.
for cname in ['UNIDA_04_RESTAURANTE_TRANSFORMADO','UNIDA_06_RESTAURANTE_NOS_FUNDOS']:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if any(t in o.name for t in ['Initial_Dining','Rear_Dining','Kitchen_At_Back']):bpy.data.objects.remove(o,do_unlink=True)
# Service wing: stockroom, staff break, operations, public washrooms.
operations=collection('09_OPERATIONS',9)
kitchen(operations,-5,30.5,.45,8)
for x in [3,6,9]:
    for z in [.85,1.45,2.05,2.65]:
        box('Store_Shelf',(x,33,z),(2,.55,.065),steel,operations)
        for dx in [-.6,0,.6]:box('Dry_Goods_Box',(x+dx,33,z+.17),(.4,.40,.3),wood,operations)
    for y in [32.73,33.27]:box('Rack_Post',(x-.95,y,1.75),(.045,.045,2.3),steel,operations)
socket('Stock_Delivery',(8,31,.6),'receive_inventory',operations);socket('Inventory',(5,31,.6),'stock_control',operations)
wc=collection('06_PUBLIC_WASHROOMS',6)
for x in [-9,-6]:
    bathroom(wc,x,-6,.55)
    box('WC_Privacy_Wall',(x-1.3,-5,1.97),(.12,4,2.8),plaster,wc)
    box('WC_Front',(x,-7.5,1.97),(2.5,.12,2.8),plaster,wc)
# Family rooms, gym, spa and dining occupy their unlocked attached structures.
family=collection('12_KIDS_INTERIOR',12)
for x in [17,25]:
    box('Play_Mat',(x,24,.59),(5,5,.055),coral if x==17 else navy,family);table(family,x,24,.55)
for j in range(6):
    x=15+j*2.2;box('Cubbies',(x,31,1.20),(1.8,.65,1.25),wood,family)
    for dx in [-.4,.4]:box('Toy_Basket',(x+dx,30.98,1.25),(.65,.5,.48),teal,family,.06)
socket('Kids_Activity',(21,24,.6),'organize_children_activity',family)
gym=collection('13_FITNESS_INTERIOR',13)
for j in range(4):
    x=15+j*3.5;box('Treadmill_Base',(x,20,3.92),(1.05,2.1,.32),dark,gym);box('Treadmill_Belt',(x,20,4.09),(.85,1.75,.035),steel,gym)
    for dx in [-.45,.45]:box('Treadmill_Post',(x+dx,20.85,4.62),(.065,.065,1.15),steel,gym)
    box('Treadmill_Console',(x,20.85,5.20),(1,.32,.10),dark,gym)
for x in [17,21,25]:box('Yoga_Mat',(x,26,3.77),(1.2,2.1,.035),navy,gym,.025)
box('Gym_Mirror',(21,32.7,5.12),(14,.03,2),mirror,gym);socket('Fitness_Class',(21,26,3.8),'fitness_activity',gym)
for x in [17,25]:light('Gym_Light',(x,24,6.50),150,gym,3)
spa=collection('14_SPA_INTERIOR',14)
for x in [34,42]:
    box('Treatment_Wall',(x+3,19,1.95),(.12,13,2.8),plaster,spa)
    box('Massage_Base',(x,18,1.05),(1.0,2.1,.9),wood,spa,.04);box('Massage_Cushion',(x,18,1.58),(1.08,2.25,.18),linen,spa,.08)
    box('Towel',(x,18.6,1.71),(.78,.58,.055),linen,spa);sink(spa,x,23,.55);plant(spa,x-2,14,.55)
    socket('Treatment_%s'%x,(x-1,18,.6),'spa_treatment',spa);light('Spa_Light',(x,18,3.22),70,spa,2)
box('Spa_Welcome',(47,29,1.08),(3,.8,1.06),wood,spa)
signature=collection('15_FINE_DINING_INTERIOR',15)
for x in [-7,-3,3,7]:
    for y in [10,15,20]:table(signature,x,y,3.75)
for x in [-8,0,8]:light('Fine_Dining_Light',(x,15,6.45),120,signature,2)
socket('Fine_Dining_Service',(0,17,3.8),'premium_dining',signature)
events=collection('17_EVENT_INTERIOR',17)
for x in [-7,0,7]:
    for y in [40,46]:table(events,x,y,.55)
box('Event_Stage',(0,50,.79),(8,2,.5),wood,events);box('Presentation_Screen',(0,51.8,2.0),(5,.05,2.0),linen,events)
for x in [-8,0,8]:light('Events_Light',(x,44,3.25),160,events,3)
socket('Event_Service',(0,49,.6),'event_setup',events)
laundry=collection('18_SERVICE_INTERIOR',18)
for j in range(5):
    x=-31+j*3.2;box('Washer_Body',(x,51,1.1),(1.3,1.0,1.2),steel,laundry,.04)
    o=cylinder('Washer_Glass_Door',(x,50.48,1.10),.37,.045,glass,laundry);o.rotation_euler.x=math.pi/2
    box('Washer_Control',(x,50.48,1.52),(.95,.025,.13),dark,laundry)
for x in [-29,-23,-17]:
    box('Linen_Sort_Table',(x,46,1.10),(2.3,1.2,1.10),wood,laundry)
    for z in [1.68,1.75,1.82]:box('Clean_Linen',(x,46,z),(1.5,.75,.06),linen,laundry)
socket('Laundry_Work',(-23,44,.6),'wash_and_fold',laundry);socket('Housekeeping_Store',(-17,45,.6),'clean_room_supply',laundry)
light('Laundry_Light',(-23,48,3.3),300,laundry,5)
# Upgrade fixtures and inspectable activity anchors on final roof.
roof=collection('20_ROOFTOP_SERVICE',20)
box('Rooftop_Bar',(21,2,10.65),(5,1.1,1.1),wood,roof);box('Rooftop_Stone_Top',(21,2,11.24),(5.1,1.2,.10),ceramic,roof)
for x in [19,21,23]:chair(roof,x,.7,10.12)
socket('Pool_Bar',(21,.5,10.2),'pool_bar_service',roof)
for c in allcols:
    if c.get('unlock_stage'):
        for o in c.objects:o['unlock_stage']=c['unlock_stage'];o['interior_revision']=3
def camera(name,loc,target,c,lens=24):
    d=bpy.data.cameras.new(name);d.lens=lens;d.clip_start=.05;d.clip_end=3000;o=bpy.data.objects.new(name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
camera('INTERIOR_CAMERA_LOBBY',(2.2,-19,2.05),(-5,-13.5,1.65),lobby,24)
camera('INTERIOR_CAMERA_ROOM',(-4.6,-12.9,5.18),(-3.1,-17.2,4.75),hotelrooms,22)
camera('INTERIOR_CAMERA_RESTAURANT',(-8.6,8,2.1),(1.5,16.5,1.5),rear,21)
camera('INTERIOR_CAMERA_KITCHEN',(9.0,18.8,2.2),(5.5,22.3,1.5),rear,22)
camera('INTERIOR_CAMERA_SPA',(31.5,13.2,2.1),(35,20,1.4),spa,22)
camera('INTERIOR_CAMERA_LAUNDRY',(-31,42,2.2),(-22,49,1.2),laundry,24)
report={'revision':3,'rooms':rooms,'interactions':stations,'runtime_implemented':False,'collections':[{'name':c.name,'objects':len(c.objects),'first':c.get('unlock_stage',0),'last':c.get('last_stage',20)} for c in allcols]}
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];bpy.context.scene['interior_manifest_json']=json.dumps(report,ensure_ascii=False)
bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=OUT+'Mare_Evolucao_Interiores_v3.blend')
print('INTERIORS_CREATED '+json.dumps({'rooms':len(rooms),'activity_anchors':len(stations),'collections':len(allcols),'file':bpy.data.filepath}))
