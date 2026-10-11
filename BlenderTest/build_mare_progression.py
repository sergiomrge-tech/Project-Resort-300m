import bpy, math, random, json
from mathutils import Vector
random.seed(20261010)
OUT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
if bpy.data.scenes.get('MARE_ETAPA_01'): raise RuntimeError('MARE already exists; do not duplicate')
old=bpy.context.scene
modules=[]
base=bpy.data.collections.new('MARE_ORLA_PERMANENTE')
def collection(stage,title):
    c=bpy.data.collections.new('MARE_%02d_%s'%(stage,title));c['unlock_stage']=stage;modules.append(c);return c
def basic(name,color,rough=.5,metal=0,noise=0):
    m=bpy.data.materials.new('MARE_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if noise:
        n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=55;n.inputs['Detail'].default_value=3
        ramp=m.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*[v*.75 for v in color],1);ramp.color_ramp.elements[1].color=(*color,1)
        m.node_tree.links.new(n.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
        bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=noise;bump.inputs['Strength'].default_value=.3;m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
    return m
wood=bpy.data.materials['wooden_floor_02_material_Courtyard_Deck__IP_Teak'].copy();wood.name='MARE_Teak_Existing_PBR'
teal=basic('Painted_Teal',(.028,.20,.18),.46,noise=.0015)
brass=basic('Brushed_Brass',(.54,.32,.12),.27,.8)
steel=basic('Brushed_Stainless',(.47,.51,.52),.3,.85)
dark=basic('Charcoal',(.018,.025,.026),.4)
cream=basic('Linen_Canvas',(.83,.75,.57),.85,noise=.002)
stone=basic('Honed_Counter_Stone',(.20,.22,.20),.25,noise=.002)
ceramic=basic('Glazed_Ceramic',(.78,.82,.73),.19)
soil=basic('Planter_Soil',(.065,.035,.018),.98,noise=.018)
leaf=basic('Leaf_Green',(.035,.20,.055),.55,noise=.003)
leaflight=basic('Leaf_Sunlit',(.10,.30,.07),.5,noise=.002)
fruit=basic('Coconut_Husk',(.22,.11,.035),.8,noise=.009)
orange=basic('Citrus',(.93,.28,.01),.5,noise=.002)
water=basic('Pool_Water',(.035,.32,.37),.09,.16)
p=next(n for n in water.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=.5;p.inputs['IOR'].default_value=1.333
glass=basic('Clear_Glass',(.78,.90,.87),.09)
p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=.94;p.inputs['IOR'].default_value=1.45
window=bpy.data.materials['IP_Glass'].copy();window.name='MARE_Architectural_Glass'
plaster=bpy.data.materials['URBAN_PBR_IP_Ivory_Painted_Render']
pavers=bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers']
curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete']
sand=bpy.data.materials['sand_03_material_Beach__IP_Sand']
grass=basic('Coastal_Garden',(.20,.28,.10),.96,noise=.02)
lightmat=basic('Warm_Lamp_Glass',(1,.65,.25),.4)
p=next(n for n in lightmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Color'].default_value=(1,.55,.2,1);p.inputs['Emission Strength'].default_value=3
tiles=[basic('Terracotta_%d'%i,(.27+i*.012,.072+i*.008,.025+i*.004),.68,noise=.0025) for i in range(5)]

def mesh(name,verts,faces,mat,c,loc=(0,0,0),smooth=False):
    me=bpy.data.meshes.new('MARE_'+name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat)
    uv=me.uv_layers.new(name='UrbanMeters');uv2=me.uv_layers.new(name='UVMap')
    for f in me.polygons:
        axis=max((abs(f.normal[k]),k) for k in range(3))[1]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co
            co=(p.x+loc[0],p.y+loc[1]) if axis==2 else ((p.x+loc[0],p.z+loc[2]) if axis==1 else (p.y+loc[1],p.z+loc[2]))
            uv.data[li].uv=co;uv2.data[li].uv=co
        f.use_smooth=smooth
    o=bpy.data.objects.new('MARE_'+name,me);c.objects.link(o);o.location=loc;return o
def box(name,loc,size,mat,c,bevel=0):
    x,y,z=[v*.5 for v in size]
    vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    o=mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,c,loc)
    if bevel:
        b=o.modifiers.new('Crafted edge radius','BEVEL');b.width=bevel;b.segments=2
    return o
def lathe(name,profile,loc,mat,c,n=20):
    vs=[]
    for radius,z in profile:
        for i in range(n):a=2*math.pi*i/n;vs.append((radius*math.cos(a),radius*math.sin(a),z))
    fs=[]
    for j in range(len(profile)-1):
        for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    return mesh(name,vs,fs,mat,c,loc,True)
def cyl(name,loc,r,h,mat,c,n=16):return lathe(name,[(r,-h/2),(r,h/2)],loc,mat,c,n)
def beam(name,a,b,r,mat,c):
    d=Vector(b)-Vector(a);o=cyl(name,(Vector(a)+Vector(b))/2,r,d.length,mat,c,12);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def orb(name,loc,scale,mat,c):
    o=lathe(name,[(max(.001,math.sin(math.pi*j/10)),-math.cos(math.pi*j/10)) for j in range(11)],loc,mat,c,16);o.scale=scale;return o
def text(name,body,loc,size,mat,c,rot=(math.pi/2,0,0)):
    d=bpy.data.curves.new('MARE_'+name,'FONT');d.body=body;d.align_x='CENTER';d.size=size;d.extrude=.006;d.bevel_depth=.001
    o=bpy.data.objects.new('MARE_'+name,d);c.objects.link(o);o.location=loc;o.rotation_euler=rot;d.materials.append(mat);return o
def path(name,points,width,mat,c,z=.08):
    verts=[]
    for i,p in enumerate(points):
        prev=Vector(points[max(0,i-1)]);nxt=Vector(points[min(len(points)-1,i+1)]);d=(nxt-prev).normalized();normal=Vector((-d.y,d.x))
        verts.extend([(p[0]+normal.x*width/2,p[1]+normal.y*width/2,z),(p[0]-normal.x*width/2,p[1]-normal.y*width/2,z)])
    return mesh(name,verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)],mat,c)
def chair(c,x,y,z=.43,angle=0):
    root=bpy.data.objects.new('MARE_Chair_Pivot',None);c.objects.link(root);root.location=(x,y,z);root.rotation_euler.z=angle
    parts=[]
    parts.append(box('Chair_Cushion',(0,0,.44),(.49,.47,.08),cream,c,.025))
    for a in [-.20,.20]:
        for b in [-.20,.20]:parts.append(beam('Chair_Leg',(a,b,.02),(a,b,.44),.027,wood,c))
        parts.append(beam('Chair_Back_Upright',(a,.20,.42),(a,.24,.96),.027,wood,c))
        parts.append(beam('Chair_Arm',(a,-.20,.65),(a,.24,.65),.03,wood,c))
    for j in range(10):parts.append(beam('Chair_Cane_Back',(-.20,.23,.58+j*.033),(.20,.23,.58+j*.033),.006,cream,c))
    for j in range(10):parts.append(beam('Chair_Cane_Vertical',(-.18+j*.04,.231,.58),(-.18+j*.04,.231,.88),.005,cream,c))
    for o in parts:o.parent=root
    return root
def table(c,x,y,z=.43):
    cyl('Cafe_Tabletop',(x,y,z+.76),.52,.06,wood,c,32);cyl('Table_Brass_Rim',(x,y,z+.756),.53,.02,brass,c,32)
    cyl('Table_Center_Leg',(x,y,z+.38),.045,.73,dark,c);cyl('Table_Foot',(x,y,z+.055),.29,.08,dark,c)
    lathe('Cup',[(.038,0),(.045,.075),(.045,.08)],(x+.14,y,z+.80),ceramic,c)
    lathe('Small_Vase',[(.025,0),(.05,.09),(.022,.15)],(x-.1,y,z+.80),ceramic,c)
    for a in [0,2,4]:beam('Flower_Stem',(x-.1,y,z+.94),(x-.1+.07*math.cos(a),y+.07*math.sin(a),z+1.10),.004,leaf,c)
def planter(c,x,y,z=0,r=.4):
    lathe('Terracotta_Planter',[(r*.7,z),(r,z+.65),(r*1.04,z+.69),(r*.95,z+.72)],(x,y,0),tiles[2],c)
    cyl('Planter_Soil',(x,y,z+.68),r*.92,.04,soil,c)
    for i in range(9):
        a=i*2.4;end=(x+.45*math.cos(a),y+.45*math.sin(a),z+1.35+random.random()*.2)
        beam('Tropical_Stem',(x,y,z+.69),end,.009,leaf,c)
        o=orb('Tropical_Leaf',end,(.12,.035,.3),leaflight if i%3==0 else leaf,c);o.rotation_euler=(.6*math.sin(a),.6*math.cos(a),a)
def palm_geometry(c,x,y,h=8):
    pts=[(x+.3*(j/5)**2,y+.15*(j/5)**2,h*j/5) for j in range(6)]
    for j in range(5):beam('Palm_Trunk',pts[j],pts[j+1],.17-j*.015,wood,c)
    tip=Vector(pts[-1])
    for i in range(11):
        a=i*2*math.pi/11;last=tip
        for j in range(1,8):
            t=j/7;p=tip+Vector((math.cos(a)*3.4*t,math.sin(a)*3.4*t,1.3*math.sin(t*math.pi)-1.4*t*t))
            beam('Palm_Rachis',last,p,.025,leaf,c)
            for sign in [-1,1]:
                length=.65*math.sin(math.pi*t)+.1;side=Vector((-math.sin(a),math.cos(a),-.22))*length*sign
                v=[tuple(p),tuple(p+side+Vector((math.cos(a)*.35,math.sin(a)*.35,-.18))),tuple(p+Vector((math.cos(a)*.24,math.sin(a)*.24,0)))]
                mesh('Palm_Leaflet',v,[(0,1,2)],leaflight if i%3==0 else leaf,c)
            last=p
    for i in range(4):orb('Palm_Coconut',tip+Vector((.23*math.sin(i),.23*math.cos(i),-.25)),(.13,.13,.17),fruit,c)
def palm(c,x,y,h=8):
    prototype=bpy.data.collections.get('MARE_PALM_REUSABLE')
    if not prototype:
        prototype=bpy.data.collections.new('MARE_PALM_REUSABLE');palm_geometry(prototype,0,0,8)
    o=bpy.data.objects.new('MARE_Palm_Instance',None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=prototype;o.location=(x,y,0);o.scale=(h/8,)*3;o.rotation_euler.z=random.random()*math.tau
def lamp(c,x,y,z=.1,h=3.3):
    cyl('Lamp_Base',(x,y,z+.09),.16,.18,dark,c);cyl('Lamp_Post',(x,y,z+h/2),.055,h,dark,c)
    cyl('Lantern_Glass',(x,y,z+h),.14,.27,lightmat,c);cyl('Lantern_Cap',(x,y,z+h+.16),.22,.07,dark,c)
def roof(c,x,y,z,w,d):
    mesh('Roof_Underlay',[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y,z+1.05),(x-w/2,y,z+1.05),(x-w/2,y+d/2,z),(x+w/2,y+d/2,z)],[(0,1,2,3),(3,2,5,4)],dark,c)
    for j in [-1,1]:beam('Roof_Fascia',(x-w/2,y+j*d/2,z),(x+w/2,y+j*d/2,z),.09,wood,c)
    tilevs=[[] for _ in tiles];tilefs=[[] for _ in tiles]
    cols=round(w/.24);rows=round(d/2/.42)
    for side in [-1,1]:
        for row in range(rows):
            yy=.1+row*(d/2-.12)/rows
            for col in range(cols):
                idx=random.randrange(len(tiles));vs=tilevs[idx];fs=tilefs[idx];off=len(vs);xx=x-w/2+(col+.5)*w/cols
                for t in [0,.52]:
                    for k in range(9):
                        a=k*math.pi/8;py=min(d/2+.07,yy+t);vs.append((xx+.12*math.cos(a),y+side*py,z+1.05*(1-py/(d/2))+.10*math.sin(a)+.02))
                for k in range(8):fs.append((off+k,off+k+1,off+k+10,off+k+9))
    for i in range(5):mesh('Individual_Curved_Roof_Tiles_%d'%i,tilevs[i],tilefs[i],tiles[i],c,smooth=True)
    beam('Ridge_Cap',(x-w/2,y,z+1.12),(x+w/2,y,z+1.12),.13,tiles[3],c)
def deck(c,x,y,w,d,z=.42):
    box('Deck_Structure',(x,y,z-.16),(w,d,.3),dark,c)
    for i in range(round(w/.18)):
        xx=x-w/2+(i+.5)*w/round(w/.18);box('Individual_Teak_Board',(xx,y,z),(w/round(w/.18)-.008,d,.06),wood,c,.008)
    box('Deck_Edge',(x,y-d/2,z-.05),(w,.10,.18),wood,c,.015)
def pergola(c,x,y,w,d,z=.45):
    for xx in [-w/2+.18,w/2-.18]:
        for yy in [-d/2+.18,d/2-.18]:box('Pergola_Post',(x+xx,y+yy,z+1.5),(.16,.16,3),wood,c,.01)
    for i in range(round(w/.45)):box('Pergola_Rafter',(x-w/2+i*.45,y,z+3.12),(.10,d+.6,.16),wood,c,.01)
    for yy in [-d/2,d/2]:box('Pergola_Main_Beam',(x,y+yy,z+3),(w+.6,.16,.22),wood,c,.012)
def room_shell(c,x,y,w,d,title,stories=1):
    box(title+'_Plinth',(x,y,.22),(w+.8,d+.8,.4),curb,c,.06)
    for level in range(stories):
        z=.45+level*3.2
        box(title+'_Floor',(x,y,z),(w,d,.16),pavers,c,.02)
        box(title+'_BackWall',(x,y+d/2,z+1.5),(w,.18,3),plaster,c,.025)
        for sign in [-1,1]:box(title+'_SideWall',(x+sign*w/2,y,z+1.5),(.18,d,3),plaster,c,.025)
        for xx in range(round(w/2.7)+1):
            px=x-w/2+xx*w/max(1,round(w/2.7));box('Facade_Teak_Mullion',(px,y-d/2,z+1.5),(.12,.13,3),wood,c,.008)
        box('Facade_Glass',(x,y-d/2+.03,z+1.5),(w-.3,.035,2.7),window,c)
        box('Continuous_Window_Lintel',(x,y-d/2,z+2.94),(w,.2,.13),wood,c)
        if level:
            box('Guest_Balcony',(x,y-d/2-1,z),(w+1,2,.15),curb,c,.025)
            beam('Balcony_TopRail',(x-w/2,y-d/2-1.9,z+1.02),(x+w/2,y-d/2-1.9,z+1.02),.035,brass,c)
            for xx in range(round(w/.3)):box('Balcony_Baluster',(x-w/2+xx*.3,y-d/2-1.9,z+.52),(.026,.026,1),dark,c)
        box('Floor_Roof_Slab',(x,y,z+3.1),(w+.7,d+.7,.22),curb,c,.035)
    text(title+'_Name',title.replace('_',' ').upper(),(x,y-d/2-.16,2.55),.28,brass,c)
    for sign in [-1,1]:planter(c,x+sign*(w/2+1),y-d/2)
def bed(c,x,y,z=.55):
    box('Bed_Frame',(x,y,z+.23),(1.85,2.1,.38),wood,c,.04);box('Mattress',(x,y,z+.48),(1.8,2,.24),cream,c,.08)
    box('Headboard',(x,y+.98,z+.75),(1.95,.10,1.2),teal,c,.035)
    for xx in [-.45,.45]:box('Pillow',(x+xx,y+.62,z+.66),(.7,.43,.14),ceramic,c,.09)
    box('Bed_Runner',(x,y-.60,z+.62),(1.81,.50,.025),teal,c,.015)
def lounger(c,x,y,z=.3):
    box('Lounger_Frame',(x,y,z+.25),(.78,2,.16),wood,c,.04);box('Lounger_Cushion',(x,y-.2,z+.36),(.72,1.5,.12),cream,c,.06)
    o=box('Lounger_Back',(x,y+.66,z+.63),(.72,.75,.12),cream,c,.04);o.rotation_euler.x=-.5
    for xx in [-.30,.30]:
        for yy in [-.75,.75]:box('Lounger_Leg',(x+xx,y+yy,z+.10),(.08,.08,.22),wood,c,.008)

# Public waterfront is independent of purchased plots.
box('Land',(0,88,-.4),(360,270,.8),grass,base)
vs=[];fs=[]
for j in range(6):
    for i in range(81):
        x=-220+i*5.5;y=-48-j*13;z=-.02-j*.14+.06*math.sin(x*.04)
        vs.append((x,y,z))
for j in range(5):
    for i in range(80):a=j*81+i;fs.append((a,a+1,a+82,a+81))
mesh('Graded_Beach_Sand',vs,fs,sand,base,smooth=True)
box('Ocean',(0,-440,-.63),(2500,750,.12),bpy.data.materials['RIO_Atlantic_Water_Backdrop'],base)
prompts=[(-170+i*2,-38+1.4*math.sin((-170+i*2)*.022)) for i in range(171)]
path('Continuous_Curved_Promenade',prompts,8,pavers,base,.14)
for sign in [-1,1]:path('Continuous_Curved_Curb',[(x,y+sign*4.02) for x,y in prompts],.17,curb,base,.23)
path('Cycle_Lane',[(x,y-2.35) for x,y in prompts],1.7,teal,base,.155)
for x in range(-150,151,15):box('Cycle_Dash',(x,-40.35+1.4*math.sin(x*.022),.17),(2,.055,.012),cream,base)
for x in [-120,-75,-35,35,75,120]:
    y=-38+1.4*math.sin(x*.022)
    lamp(base,x,y+3.2)
    box('Bench_Seat',(x+2.5,y+2.6,.56),(2,.48,.12),wood,base,.025)
    for xx in [-.75,.75]:box('Bench_Support',(x+2.5+xx,y+2.6,.28),(.09,.35,.52),dark,base)
    box('Bench_Back',(x+2.5,y+2.82,.84),(2,.075,.39),wood,base,.02)
    cyl('Public_Recycling_Bin',(x-2,y+2.7,.55),.25,1,dark,base)
for x in [-90,0,90]:
    path('Accessible_Beach_Boardwalk',[(x,-42),(x,-54),(x,-68)],3.2,wood,base,.12)
    for side in [-1,1]:
        for y in range(-44,-69,-3):beam('Boardwalk_Rail_Post',(x+side*1.55,y,.08),(x+side*1.55,y,1.1),.035,wood,base)
        beam('Boardwalk_Handrail',(x+side*1.55,-43,1.1),(x+side*1.55,-68,1.1),.045,wood,base)
    for dx in [-2.5,2.5]:
        cyl('Beach_Shower_Post',(x+dx,-47,1.1),.045,2.2,steel,base);beam('Shower_Neck',(x+dx,-47,2.18),(x+dx,-47.35,2.18),.025,steel,base);cyl('Shower_Head',(x+dx,-47.35,2.14),.09,.025,steel,base)
for x in range(-155,156,20):palm(base,x,-29,7.2+random.random()*1.8)
# Vegetation kept outside the footprints reserved for every future purchase.
footprints=[(0,-16,8,8),(-11,-19,10,9),(0,-4,6,6),(15,-4,7,6),(14,-19,10,9),(-38,-19,16,10),(0,20,20,16),(70,132,18,14),(0,60,18,14),(-52,60,30,20),(-27,25,23,20),(-55,100,30,18),(45,42,18,16),(55,76,18,16),(-40,140,25,20),(40,108,28,20),(-73,179,28,20),(73,179,28,20),(0,148,32,26),(95,132,20,16),(0,94,30,22)]
for i in range(95):
    x=random.uniform(-115,115);y=random.uniform(-18,204)
    if any(abs(x-a)<w/2+7 and abs(y-b)<d/2+7 for a,b,w,d in footprints):continue
    if abs(abs(x)-25)<6 or any(abs(y-j)<5 for j in [10,55,120,195]):continue
    palm(base,x,y,6+random.random()*3)

# 01: detailed founding kiosk, retained in all twenty stages.
c=collection(1,'QUIOSQUE_ORIGINAL');x=0;y=-16;z=.45
deck(c,x,y,8,8,z)
for xx in [-2.9,2.9]:
    for yy in [-2.35,2.35]:
        box('Kiosk_Structural_Post',(xx,y+yy,1.92),(.18,.18,3.0),wood,c,.015)
        box('Post_Brass_Foot',(xx,y+yy,.58),(.205,.205,.22),brass,c,.012)
        for zz in [.60,3.25]:cyl('Post_Bolt',(xx,y+yy-.11,zz),.02,.025,steel,c).rotation_euler.x=math.pi/2
box('Back_Painted_Wall',(0,y+2.25,1.87),(5.8,.14,2.8),teal,c,.02)
for xx in [-2.9,2.9]:
    for j in range(18):box('Side_Vertical_Teak_Slat',(xx,y-2.25+j*.26,1.1),(.10,.23,1.2),wood,c,.01)
for j in range(34):box('Front_Teak_Batten',(-2.75+j*.165,y-2.2,.91),(.12,.09,.80),wood,c,.008)
box('Customer_Counter',(0,y-2.26,1.36),(5.9,.67,.09),stone,c,.025)
box('Counter_Brass_Nosing',(0,y-2.60,1.34),(5.95,.025,.08),brass,c,.009)
box('Accessible_Side_Counter',(-3.35,y-1.3,1.2),(.8,1,.06),stone,c,.025)
box('Service_Opening_Header',(0,y-2.3,2.95),(5.9,.16,.27),teal,c,.015)
box('Main_Sign_Backboard',(0,y-2.43,3.05),(3.2,.09,.62),wood,c,.03)
text('Mare_Brand','MARÉ',(0,y-2.49,2.94),.43,brass,c)
text('Kiosk_Subtitle','CAFÉ  •  COCO  •  PRAIA',(0,y-2.493,2.76),.085,cream,c)
roof(c,0,y,3.50,7.3,6.3)
for xx in [-2.9,0,2.9]:
    beam('Visible_Rafter',(xx,y-3.15,3.50),(xx,y,4.55),.07,wood,c);beam('Visible_Rafter',(xx,y,4.55),(xx,y+3.15,3.50),.07,wood,c)
beam('Ridge_Interior_Beam',(-3.3,y,4.45),(3.3,y,4.45),.10,wood,c)
for yy in [-3.14,3.14]:
    beam('Copper_Gutter',(-3.6,y+yy,3.47),(3.6,y+yy,3.47),.06,brass,c)
beam('Gutter_Downpipe',(3.42,y+3.12,3.47),(3.42,y+3.12,.55),.04,brass,c)
box('Rear_Workbench',(0,y+1.53,1.27),(5.25,.72,.09),steel,c,.02)
for xx in [-2.1,-.7,.7,2.1]:
    box('Prep_Cabinet',(xx,y+1.5,.83),(1.25,.68,.77),teal,c,.02)
    for zz in [.76,1.05]:
        box('Drawer_Front',(xx,y+1.14,zz),(1.18,.04,.23),wood,c,.01);beam('Drawer_Handle',(xx-.15,y+1.10,zz),(xx+.15,y+1.10,zz),.016,brass,c)
# Rear stone worktop split around a real sink cavity.
box('Sink_Left_Rim',(-2.2,y+.40,1.29),(.30,.65,.045),steel,c)
box('Sink_Right_Rim',(-1.3,y+.40,1.29),(.30,.65,.045),steel,c)
for yy in [.10,.70]:box('Sink_Rim',(-1.75,y+yy,1.29),(.65,.06,.045),steel,c)
box('Sink_Bowl_Bottom',(-1.75,y+.40,1.04),(.61,.53,.025),steel,c,.03)
for xx in [-2.06,-1.44]:box('Sink_Bowl_Side',(xx,y+.40,1.17),(.025,.56,.26),steel,c)
for yy in [.12,.68]:box('Sink_Bowl_Side',(-1.75,y+yy,1.17),(.64,.025,.26),steel,c)
beam('Faucet_Stem',(-1.75,y+.8,1.30),(-1.75,y+.8,1.72),.025,steel,c);beam('Faucet_Spout',(-1.75,y+.8,1.72),(-1.75,y+.45,1.72),.025,steel,c)
# Espresso machine, grinder, drip tray and porcelain cups.
box('Espresso_Base',(.30,y+1.4,1.39),(.85,.58,.13),steel,c,.035)
box('Espresso_Body',(.30,y+1.62,1.72),(.83,.30,.56),teal,c,.04)
box('Espresso_Control_Panel',(.30,y+1.45,1.83),(.73,.06,.16),steel,c,.015)
for xx in [.08,.50]:
    cyl('Espresso_Grouphead',(xx,y+1.31,1.65),.08,.09,steel,c)
    beam('Portafilter_Handle',(xx,y+1.25,1.63),(xx,y+.99,1.63),.026,dark,c)
    lathe('Espresso_Cup',[(.04,0),(.046,.065),(.043,.075)],(xx,y+1.13,1.46),ceramic,c)
    for dx in [-.035,0,.035]:cyl('Espresso_Button',(xx+dx,y+1.41,1.84),.014,.012,dark,c).rotation_euler.x=math.pi/2
for j in range(14):beam('Drip_Tray_Grid',(-.07+j*.055,y+1.05,1.47),(-.07+j*.055,y+1.33,1.47),.004,steel,c)
box('Grinder_Base',(1.12,y+1.5,1.53),(.27,.30,.40),dark,c,.025)
lathe('Coffee_Grinder_Hopper',[(.09,0),(.16,.18),(.16,.35),(.17,.37)],(1.12,y+1.5,1.73),glass,c)
cyl('Hopper_Lid',(1.12,y+1.5,2.11),.18,.025,dark,c)
for i in range(24):orb('Coffee_Bean',(1.12+random.uniform(-.09,.09),y+1.5+random.uniform(-.09,.09),1.94+random.uniform(-.08,.07)),(.013,.020,.012),fruit,c)
box('POS_Base',(2.05,y-2.26,1.43),(.3,.26,.08),dark,c,.025)
o=box('POS_Screen',(2.05,y-2.20,1.66),(.34,.035,.23),dark,c,.015);o.rotation_euler.x=-.2
text('POS_Display','MARÉ',(2.05,y-2.23,1.65),.07,cream,c)
# Back display shelving, bottles, cups, fruit and menu.
for zz in [2.05,2.48]:
    box('Floating_Teak_Shelf',(-.65,y+2.10,zz),(2.8,.30,.055),wood,c,.01)
    for xx in [-1.8,-.65,.45]:beam('Shelf_Bracket',(xx,y+2.2,zz-.18),(xx,y+1.98,zz),.015,brass,c)
    for j in range(12):
        xx=-1.85+j*.22
        lathe('Bottle',[(.055,0),(.055,.20),(.022,.26),(.022,.34),(.024,.35)],(xx,y+2.05,zz+.03),glass if j%3 else teal,c)
        cyl('Bottle_Cap',(xx,y+2.05,zz+.39),.024,.025,brass,c)
        cyl('Bottle_Label',(xx,y+2.05,zz+.18),.056,.08,cream,c)
box('Menu_Chalkboard',(-2.02,y+2.14,2.16),(1.15,.05,1.35),wood,c,.03)
box('Menu_Inset',(-2.02,y+2.10,2.16),(1.04,.02,1.22),dark,c)
text('Menu','CAFÉ DA PRAIA\n\nCOCO GELADO\nCAFÉ ESPECIAL\nSUCOS NATURAIS\nSANDUÍCHES',(-2.02,y+2.08,2.52),.12,cream,c)
box('Cold_Display_Cabinet',(2.15,y+.48,1.16),(.82,.75,1.4),teal,c,.035)
box('Cold_Display_Glass',(2.15,y+.09,1.35),(.71,.035,.98),glass,c)
for zz in [.98,1.34,1.68]:
    box('Refrigerator_Shelf',(2.15,y+.46,zz),(.70,.65,.025),steel,c)
    for xx in [1.94,2.15,2.36]:lathe('Refrigerated_Bottle',[(.045,0),(.045,.15),(.02,.22)],(xx,y+.35,zz),glass,c)
box('Fruit_Crate',(-.7,y-2.10,1.45),(.70,.35,.12),wood,c,.012)
for i in range(8):orb('Fresh_Coconut',(-.95+(i%4)*.16,y-2.1+(i//4)*.15,1.58),(.09,.08,.095),fruit,c)
for xx in [-1.35,1.3]:
    cyl('Bar_Stool_Seat',(xx,y-3.08,1.13),.23,.09,wood,c,24)
    for a in range(4):
        angle=a*math.pi/2;beam('Stool_Leg',(xx+.20*math.cos(angle),y-3.08+.20*math.sin(angle),.49),(xx+.16*math.cos(angle),y-3.08+.16*math.sin(angle),1.09),.023,dark,c)
    lathe('Stool_Foot_Ring',[(.20,0),(.20,.035)],(xx,y-3.08,.77),brass,c,24)
for xx in [-1.2,1.2]:
    beam('Pendant_Cable',(xx,y-1.1,3.50),(xx,y-1.1,2.60),.007,dark,c)
    lathe('Pendant_Woven_Shade',[(.16,0),(.24,.08),(.18,.27),(.06,.32)],(xx,y-1.1,2.55),cream,c)
    orb('Pendant_Bulb',(xx,y-1.1,2.62),(.055,.055,.07),lightmat,c)
for xx in [-4.7,4.7]:planter(c,xx,y-2,.1)
table(c,-5.3,y-1.0,.12)
chair(c,-5.3,y-1.8,.12,math.pi);chair(c,-5.3,y-.2,.12,0)
box('Entrance_Ramp',(-3.55,y-3.9,.24),(1.2,2.2,.20),wood,c,.012)
text('Historic_Plaque','DESDE O PRIMEIRO COCO',(.0,y-2.265,.83),.10,brass,c)
for k,loc in [('ORDER',(0,y-3.5,.48)),('PREP',(0,y+.6,.48)),('SUPPLY',(0,y+3.5,.12))]:
    o=bpy.data.objects.new('SOCKET_01_'+k,None);c.objects.link(o);o.location=loc;o.empty_display_type='ARROWS';o['interaction_role']=k

# 02--20: cumulative, individually purchasable art modules.
c=collection(2,'DECK_MESAS');deck(c,-11,-19,10,9)
for x in [-14,-8]:
    for y in [-21,-17]:table(c,x,y);chair(c,x,y-.9,.43,math.pi);chair(c,x,y+.9)
c=collection(3,'PREPARO_ESTOQUE');room_shell(c,0,-4,6,6,'Cozinha_de_apoio')
box('Commercial_Range',(0,-3,1),(1.5,.8,1),steel,c,.03)
for x in [-.45,.45]:
    for y in [-3.2,-2.8]:cyl('Range_Burner',(x,y,1.52),.14,.035,dark,c)
box('Extraction_Hood',(0,-3,2.5),(1.8,1,.45),steel,c,.02)
for x in [-2,2]:box('Storage_Rack',(x,-2,1.4),(.8,1.2,2),steel,c,.02)
c=collection(4,'SANITARIOS');room_shell(c,15,-4,7,6,'Sanitarios')
for x in [13,17]:
    box('Washbasin',(x,-3,1),(1,.55,.18),ceramic,c,.06);cyl('Tap',(x,-2.85,1.2),.022,.25,steel,c)
    box('Bathroom_Mirror',(x,-2.65,1.9),(.75,.025,.9),steel,c,.025)
c=collection(5,'LOUNGE_PERGOLA');deck(c,14,-19,10,9);pergola(c,14,-19,9,8)
for x in [11,17]:table(c,x,-19);chair(c,x,-20,.43,math.pi);chair(c,x,-18)
for y in [-22,-16]:box('Lounge_Sofa',(14,y,.85),(2.8,.9,.78),cream,c,.09)
c=collection(6,'BEACH_CLUB');deck(c,-38,-19,16,10)
for x in [-43,-33]:
    pergola(c,x,-18,4,4);box('Cabana_Curtain',(x-1.7,-18,1.85),(.025,3.4,2.7),cream,c)
    lounger(c,x-.5,-19,.43);lounger(c,x+.5,-19,.43)
c=collection(7,'RESTAURANTE');room_shell(c,0,20,20,16,'Restaurante_Mare');pergola(c,0,9.5,18,4,.12)
for x in [-6,0,6]:
    for y in [16,23]:table(c,x,y,.55);chair(c,x,y-1,.55,math.pi);chair(c,x,y+1,.55)
c=collection(8,'OPERACAO');room_shell(c,70,132,18,14,'Operacao_e_equipe')
for x in [65,70,75]:box('Utility_Cabinet',(x,135,1.4),(1.7,1,2.5),steel,c,.04)
box('Loading_Dock',(70,143,.52),(14,6,1),curb,c)
c=collection(9,'RECEPCAO');room_shell(c,0,60,18,14,'Recepcao_Concierge')
box('Reception_Desk',(0,57,1.02),(5,.9,1.08),wood,c,.07)
for x in [-6,6]:box('Lobby_Sofa',(x,59,.8),(2.8,1,.65),cream,c,.10)
for x in [-25,25]:path('Guest_Path',[(x,-27),(x,195)],3.2,pavers,c,.09)
for y in [10,55,120,195]:path('Cross_Garden_Path',[(-105,y),(105,y)],3,pavers,c,.09)
c=collection(10,'BANGALOS')
for x in [-60,-45]:
    for y in [56,68]:room_shell(c,x,y,8,8,'Bangalo');roof(c,x,y,3.65,9,9);bed(c,x,y+.8)
c=collection(11,'PISCINA');deck(c,-27,25,23,20,.20)
box('Pool_Basin',(-27,25,-.18),(16,10,1.2),teal,c,.08);box('Pool_Water',(-27,25,.24),(15.5,9.5,.035),water,c)
for y in [17,33]:
    for x in [-33,-27,-21]:lounger(c,x,y,.23)
for x in [-35,-19]:box('Pool_Coping',(x,25,.28),(.5,10.8,.12),curb,c,.03)
for y in [19.6,30.4]:box('Pool_Coping',(-27,y,.28),(16.5,.5,.12),curb,c,.03)
c=collection(12,'ALA_HOSPEDAGEM');room_shell(c,-55,100,30,18,'Suites_Jardim',2)
for z in [.55,3.75]:
    for x in [-65,-55,-45]:bed(c,x,101,z)
c=collection(13,'KIDS_CLUB');room_shell(c,45,42,18,16,'Clube_Infantil')
for x in [40,45,50]:box('Play_Table',(x,42,.7),(2,1.2,.5),teal,c,.1)
box('Play_Sandpit',(45,30,.2),(8,5,.35),wood,c,.03);box('Sandpit_Sand',(45,30,.40),(7.7,4.7,.07),sand,c)
c=collection(14,'ACADEMIA_YOGA');room_shell(c,55,76,18,16,'Fitness_e_Yoga')
for x in [50,54,58]:
    box('Treadmill_Base',(x,75,.55),(.8,1.8,.25),dark,c,.06);box('Treadmill_Belt',(x,75,.70),(.65,1.55,.03),teal,c)
    for dx in [-.34,.34]:beam('Treadmill_Upright',(x+dx,75.6,.6),(x+dx,75.6,1.65),.035,steel,c)
    box('Fitness_Console',(x,75.6,1.68),(.7,.15,.2),dark,c,.025)
for x in [50,53,56,59]:box('Yoga_Mat',(x,79,.55),(.8,1.9,.025),teal,c,.025)
c=collection(15,'SPA');room_shell(c,-40,140,25,20,'Spa_Mare')
for x in [-48,-40,-32]:
    box('Massage_Table',(x,141,1),(1,2,.35),cream,c,.06)
    for dx in [-.35,.35]:
        for dy in [-.75,.75]:box('Massage_Table_Leg',(x+dx,141+dy,.7),(.08,.08,.65),wood,c)
    box('Spa_Privacy_Screen',(x+3,141,1.65),(.08,5,2.4),wood,c)
c=collection(16,'GASTRONOMIA');room_shell(c,40,108,28,20,'Gastronomia_Autoral')
for x in [31,40,49]:
    for y in [103,112]:table(c,x,y,.55);chair(c,x,y-1,.55,math.pi);chair(c,x,y+1,.55)
c=collection(17,'VILLAS')
for x in [-73,73]:
    room_shell(c,x,179,28,20,'Villa_Premium');bed(c,x-7,180);bed(c,x+7,180)
    box('Villa_Plunge_Pool',(x,164,.25),(10,5,.08),water,c,.08)
    for dx in [-9,9]:lounger(c,x+dx,164,.12)
c=collection(18,'EVENTOS');room_shell(c,0,148,32,26,'Eventos_e_Celebracoes')
for x in [-10,0,10]:
    for y in [142,151]:table(c,x,y,.55)
box('Event_Stage',(0,156,.9),(12,4,.75),wood,c,.03)
c=collection(19,'SUSTENTABILIDADE');room_shell(c,95,132,20,16,'Lavanderia_e_Recursos')
for x in [89,93,97,101]:
    box('Laundry_Machine',(x,133,1),(1.5,1.2,1.4),steel,c,.05)
    o=cyl('Laundry_Door',(x,132.36,1.1),.37,.055,glass,c,24);o.rotation_euler.x=math.pi/2
    box('Solar_Panel',(x,132,3.8),(2.8,5,.12),teal,c,.025)
c=collection(20,'RESORT_CINCO_ESTRELAS');room_shell(c,0,94,30,22,'Mare_Resort',4)
for z in [.55,3.75,6.95,10.15]:
    for x in [-10,0,10]:bed(c,x,97,z)
pergola(c,0,94,24,17,13.45)
for x in [-8,0,8]:lounger(c,x,89,13.45)
for x in [-20,20]:palm(c,x,84,9)
text('Five_Star_Identity','MARÉ  •  RESORT',(0,82.8,13.1),.6,brass,c)

# Individual scene snapshots: no future-stage geometry in early stages.
def camera(name,loc,target,lens):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);base.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=4000;return o
hero=camera('MARE_CAMERA_QUIOSQUE',(12,-32,8.2),(0,-16,1.7),43)
interior=camera('MARE_CAMERA_BALCAO',(-5,-23,3.3),(.0,-15,1.7),35)
waterfront=camera('MARE_CAMERA_ORLA',(48,-80,23),(0,-19,1),40)
aerial=camera('MARE_CAMERA_RESORT',(-205,-210,225),(0,80,2),39)
ld=bpy.data.lights.new('MARE_Sun','SUN');ld.energy=2.6;ld.angle=math.radians(12);sun=bpy.data.objects.new('MARE_Sun',ld);base.objects.link(sun);sun.rotation_euler=(.40,-.5,-.65)
for i,c in enumerate(modules,1):
    for o in c.all_objects:
        o['module_id']='mare_%02d'%i;o['unlock_stage']=i;o['asset_author']='Project Resort procedural original art'
    sc=bpy.data.scenes.new('MARE_ETAPA_%02d'%i);sc.collection.children.link(base)
    for col in modules[:i]:sc.collection.children.link(col)
    sc.world=old.world.copy();sc.world.name='MARE_World_%02d'%i
    sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True
    sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
    sc.camera=hero if i<7 else (waterfront if i<10 else aerial)
    sc['progression_stage']=i;sc['max_stage']=20;sc['land_size_m']='240 x 240';sc['runtime_state']='Art and progression data prepared; purchase logic not integrated'
    sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
    sc['source_city_scene']=old.name
bpy.context.window.scene=bpy.data.scenes['MARE_ETAPA_01']
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'Mare_Quiosque_20Etapas_v1.blend')
print('MARE_BUILD_DONE',len(modules),'modules',len(base.objects),'waterfront objects',len(modules[0].objects),'kiosk objects')
