import bpy, math, random
from mathutils import Vector
random.seed(91)
ROOT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
old=bpy.data.scenes['RESORT_IPANEMA_2x2KM']
s=bpy.data.scenes.new('RESORT_2x1KM_COMERCIO')
bpy.context.window.scene=s; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
s.world=old.world.copy()
root=bpy.data.collections.new('MAP_2000x1000_COMERCIO'); s.collection.children.link(root)
coast=bpy.data.collections.new('MODULE_COAST_RETAIL_200m')
for ob in bpy.data.collections['MODULE_COAST_200m'].objects: coast.objects.link(ob)
retail=bpy.data.collections.new('RETAIL_INTERIORS_AND_FACADES'); coast.children.link(retail)
batch={}
wood=bpy.data.materials['IP_Teak']; metal=bpy.data.materials['IP_Bronze']; stone=bpy.data.materials['IP_Limestone']; paving=bpy.data.materials['checkered_pavement_tiles']; leaf=bpy.data.materials['IP_Leaf']; fabric=bpy.data.materials['IP_Linen']; white=bpy.data.materials['IP_Ivory']; dark=bpy.data.materials['IP_Window_Recess']; coral=bpy.data.materials['IP_Coral_Plaster']; sage=bpy.data.materials['IP_Sage_Plaster']; ochre=bpy.data.materials['IP_Ochre_Plaster']
def mat(name,c,rough=.6,emission=0,transmission=0):
    m=bpy.data.materials.new('SHOP_'+name); m.use_nodes=True; m.diffuse_color=(*c,1)
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Transmission Weight'].default_value=transmission
    if emission:
        bs.inputs['Emission Color'].default_value=(*c,1); bs.inputs['Emission Strength'].default_value=emission
    return m
clear=mat('Clear_Display_Glass',(.96,.99,1),.065,transmission=1)
bs=next(n for n in clear.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Roughness'].default_value=.012; bs.inputs['IOR'].default_value=1.1
out=next(n for n in clear.node_tree.nodes if n.type=='OUTPUT_MATERIAL'); transparent=clear.node_tree.nodes.new('ShaderNodeBsdfTransparent'); transparent.inputs['Color'].default_value=(.98,.99,1,1)
mix=clear.node_tree.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.82
clear.node_tree.links.new(bs.outputs['BSDF'],mix.inputs[1]); clear.node_tree.links.new(transparent.outputs[0],mix.inputs[2]); clear.node_tree.links.new(mix.outputs[0],out.inputs['Surface'])
cream=mat('Lettering',(.94,.85,.66),.45,emission=.35)
warm=mat('Warm_Luminaires',(1,.70,.36),.4,emission=5)
navy=mat('Midnight_Teal',(.025,.12,.14))
red=mat('Berry',(.28,.047,.06))
blue=mat('Ocean_Blue',(.025,.23,.37))
orange=mat('Product_Orange',(.72,.25,.045))
green=mat('Product_Green',(.25,.50,.12))
yellow=mat('Product_Yellow',(.91,.66,.08))
def geom(name,v,f,m):
    vv,ff,mm=batch.setdefault((name,m.name),([],[],m)); off=len(vv); vv.extend(v); ff.extend(tuple(i+off for i in face) for face in f)
def box(name,p,d,m):
    x,y,z=p; a,b,c=[t*.5 for t in d]
    v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    geom(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def cylinder(name,p,r,h,m,n=24):
    x,y,z=p; v=[]
    for zz in (z-h/2,z+h/2):
        for i in range(n): v.append((x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),zz))
    geom(name,v,[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def label(text,p,size,m):
    cu=bpy.data.curves.new('RETAIL_TEXT_'+text,'FONT'); cu.body=text; cu.size=size; cu.align_x='CENTER'; cu.extrude=.004
    ob=bpy.data.objects.new('RETAIL_SIGN_'+text,cu); retail.objects.link(ob); ob.location=p; ob.rotation_euler=(math.pi/2,0,0); cu.materials.append(m)
def canopy(cx,y,w,m):
    # Sloping awning with individual fabric stripes, open underside and front valance.
    for j in range(14):
        x0=cx-w/2+j*w/14; x1=x0+w/14
        geom('Striped_Awnings',[(x0,y-.2,3.25),(x1,y-.2,3.25),(x1,y-1.65,2.98),(x0,y-1.65,2.98)],[(0,1,2,3)],m if j%2 else fabric)
    box('Awning_Valance',(cx,y-1.65,2.86),(w,.04,.24),m)
def chair(cx,y):
    box('Cafe_Seats',(cx,y,.88),(.45,.45,.12),wood)
    box('Cafe_Seatbacks',(cx,y+.18,1.16),(.45,.09,.5),wood)
    for dx in (-.16,.16):
        for dy in (-.16,.16): box('Cafe_Chairlegs',(cx+dx,y+dy,.65),(.045,.045,.5),metal)

frontages=[
    ('Resort_Aurora',-64,-26,57,26,6),
    ('Hotel_Atlantico',-2,-24,27,30,3),
    ('Casa_Coral',46,-24,18,30,2),
    ('Residencial_Sal',70,-24,20,30,2),
    ('Galeria_Mar',87,-24,12,30,1)]
brands=[('CAFE DA ORLA','cafe',navy),('PADARIA SOL','bakery',ochre),('SABOR DO MAR','restaurant',coral),('LOBBY AURORA','lobby',navy),('BRISA SURF','surf',blue),('GELATO TROPICAL','icecream',sage),('BISTRO ATLANTICO','restaurant',red),('MERCADO PRAIA','market',sage),('ARTE & MAR','gift',ochre),('FARMACIA ORLA','pharmacy',navy),('BOUTIQUE BRISA','boutique',red),('CASA DO CAFE','cafe',navy),('EMPORIO SAL','market',sage),('GALERIA ARTES','gift',coral)]
shopindex=0; commerces=0
for prefix,x,front,w,depth,units in frontages:
    for ob in list(coast.objects):
        if ob.name.startswith(prefix+'_') and any(tag in ob.name for tag in ('_Shops__','_ShopMullions__','_Awning__','_Portal__','_Base__')): coast.objects.unlink(ob)
        if ob.name.startswith(prefix+'_Shell__'):
            coast.objects.unlink(ob); cp=ob.copy(); cp.data=ob.data.copy(); cp.name='RETAIL_'+prefix+'_UPPER_STRUCTURE'; coast.objects.link(cp)
            for v in cp.data.vertices:
                if v.co.z<1: v.co.z=3.85
            cp.data.update()
    # Close the rear and sides of the opened ground floor with plausible shop depth.
    box('Building_Ground_Rear',(x,front+depth-.16,2.05),(w,.32,3.8),white)
    for dx in (-w/2+.12,w/2-.12): box('Building_Ground_Sides',(x+dx,front+depth/2,2.05),(.24,depth,3.8),white)
    box('Shop_Ceiling',(x,front+depth/2,3.75),(w,depth,.2),white)
    box('Retail_Forecourt',(x,front-2,.39),(w,4,.16),paving)
    unitw=(w-.7)/units
    for i in range(units):
        cx=x-w/2+.35+(i+.5)*unitw
        name,kind,color=brands[shopindex]; shopindex+=1
        if kind!='lobby': commerces+=1
        box('Shop_InteriorFloor',(cx,front+3.1,.43),(unitw-.10,6.2,.16),wood)
        box('Shop_Backwalls',(cx,front+6.1,2.05),(unitw,.18,3.25),white)
        for dx in (-unitw/2+.08,unitw/2-.08): box('Shop_Partitions',(cx+dx,front+3.1,2.06),(.16,6.2,3.28),white)
        doorx=cx+unitw*.31; doorw=1.18
        # Glass is fully transmissive; doors and display bays have modeled frames/handles.
        box('Shop_DisplayGlass',(cx-unitw*.13,front-.16,1.60),(unitw*.65-.22,.024,2.14),clear)
        box('Shop_DoorGlass',(doorx,front-.16,1.60),(doorw,.025,2.14),clear)
        for xx in (cx-unitw/2+.11,doorx-doorw/2-.08,doorx+doorw/2+.04): box('Shop_VerticalFrames',(xx,front-.21,1.64),(.07,.09,2.4),metal)
        for z in (.50,2.78): box('Shop_HorizontalFrames',(cx,front-.21,z),(unitw-.1,.10,.08),metal)
        box('Shop_DoorHandle',(doorx-.38,front-.29,1.5),(.034,.075,.36),metal)
        box('Shop_Threshold',(doorx,front-.18,.48),(1.35,.7,.08),stone)
        box('Storefront_Fascia',(cx,front-.28,3.10),(unitw-.16,.18,.6),color)
        canopy(cx,front,unitw-.18,color)
        label(name,(cx,front-1.685,2.79),min(.29,(unitw-.5)/max(1,len(name)*.65)),cream)
        label('ABERTO',(doorx,front-.23,2.0),.10,cream)
        cylinder('Ceiling_Lights',(cx,front+2.8,3.51),.38,.055,warm,32)
        label(name,(cx,front+5.985,2.75),.24,color)
        lightdata=bpy.data.lights.new('SHOP_INTERIOR_LIGHT','AREA'); lightdata.energy=95; lightdata.color=(1,.85,.67); lightdata.shape='DISK'; lightdata.size=2
        light=bpy.data.objects.new('RETAIL_INTERIOR_LIGHT',lightdata); retail.objects.link(light); light.location=(cx,front+2.485,3.46)
        box('Shop_ServiceCounter',(cx-unitw*.16,front+3.7,.95),(unitw*.52,.85,.94),wood)
        box('Counter_StoneTop',(cx-unitw*.16,front+3.7,1.46),(unitw*.54,.92,.10),stone)
        box('Cash_Register',(cx+unitw*.03,front+3.7,1.64),(.35,.27,.25),dark)
        if kind in ('market','pharmacy','gift','boutique'):
            for z in (.85,1.40,1.95,2.50):
                box('Display_Shelving',(cx,front+5.65,z),(unitw*.76,.46,.065),wood)
                for j in range(9):
                    xx=cx-unitw*.34+j*unitw*.085
                    box('Packaged_Products',(xx,front+5.57,z+.18),(.18,.15,.30),[orange,green,yellow,fabric][j%4])
            for j in range(4):
                xx=cx-unitw*.27+j*.43
                box('Window_DisplayPedestals',(xx,front+.65,.84),(.34,.38,.65),stone)
                if kind=='boutique':
                    box('Fashion_Display',(xx,front+.65,1.55),(.38,.10,.7),[coral,sage,blue,fabric][j])
                    box('Fashion_Display',(xx,front+.65,1.03),(.26,.12,.32),wood)
                else: box('Window_Products',(xx,front+.65,1.36),(.21,.19,.38),[orange,green,yellow,fabric][j])
        elif kind=='surf':
            for j in range(5):
                xx=cx-unitw*.32+j*.55
                # Rounded board silhouette with elliptical outline and real thickness.
                v=[]; n=32
                for yy in (front+.5,front+.59):
                    for t in range(n):
                        a=t*math.tau/n; v.append((xx+.22*math.sin(a),yy,1.60+1.02*math.cos(a)))
                geom('Surfboards',v,[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(t,(t+1)%n,(t+1)%n+n,t+n) for t in range(n)],[blue,orange,fabric,green,yellow][j])
        else:
            if kind in ('cafe','bakery','icecream'):
                box('Pastry_DisplayBase',(cx-unitw*.22,front+.65,.80),(unitw*.43,.6,.58),wood)
                box('Pastry_DisplayGlass',(cx-unitw*.22,front+.65,1.27),(unitw*.43,.6,.38),clear)
                for j in range(7): cylinder('Pastries',(cx-unitw*.40+j*.32,front+.65,1.09),.11,.08,ochre,16)
                box('Coffee_Machine',(cx-unitw*.27,front+3.7,1.70),(.62,.45,.45),metal)
            for dx in (-unitw*.22,unitw*.16):
                cylinder('Indoor_Tables',(cx+dx,front+2,.92),.045,.9,metal)
                cylinder('Indoor_Tabletops',(cx+dx,front+2,1.40),.43,.07,wood)
                chair(cx+dx-.62,front+2); chair(cx+dx+.62,front+2)
            if prefix=='Resort_Aurora' and kind in ('cafe','restaurant','icecream'):
                tx=cx-unitw*.2
                cylinder('Terrace_Tables',(tx,front-2.1,.92),.04,.9,metal)
                cylinder('Terrace_Tabletops',(tx,front-2.1,1.40),.5,.07,wood)
                chair(tx-.72,front-2.1); chair(tx+.72,front-2.1)
        # Small planted pot and menu board on the display side, away from door path.
        potx=cx-unitw*.39
        cylinder('Shop_Pots',(potx,front-.7,.71),.18,.43,wood)
        for j in range(7):
            a=j*math.tau/7; p=Vector((potx,front-.7,.98)); tip=p+Vector((.23*math.cos(a),.23*math.sin(a),.3))
            geom('Shop_Plants',[tuple(p),tuple(tip+Vector((.06,0,0))),tuple(tip),tuple(tip-Vector((.06,0,0)))],[(0,1,2,3)],leaf)
        if kind in ('cafe','restaurant','bakery','icecream'):
            box('Menu_Boards',(cx-unitw*.33,front-1.95,1.05),(.46,.09,.78),dark)
            label('MENU',(cx-unitw*.33,front-2.01,1.16),.11,cream)

for (name,mname),(v,f,m) in batch.items():
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.materials.append(m); me.update()
    ob=bpy.data.objects.new('RETAIL_'+name+'__'+mname,me); retail.objects.link(ob)
    uv=me.uv_layers.new(name='WorldMeters')
    for p in me.polygons:
        axis=0
        if abs(p.normal.y)>abs(p.normal.x): axis=1
        if abs(p.normal.z)>abs(p.normal[axis]): axis=2
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(co.y*.25,co.z*.25) if axis==0 else ((co.x*.25,co.z*.25) if axis==1 else (co.x*.25,co.y*.25))
        if name in ('Ceiling_Lights','Shop_Pots','Indoor_Tables','Indoor_Tabletops','Terrace_Tabletops','Pastries'): p.use_smooth=True
    if name in ('Shop_ServiceCounter','Counter_StoneTop','Window_DisplayPedestals'):
        mod=ob.modifiers.new('Shop_Soft_Edges','BEVEL'); mod.width=.025; mod.segments=3

# Reduce depth by selecting three inland rows and recentering geometry, without scaling buildings.
for ob in old.objects:
    if ob.type=='EMPTY' and ob.instance_type=='COLLECTION':
        if ob.name.startswith('CITY_SECTOR_') and int(ob.name.split('_')[-1])>2: continue
        cp=ob.copy(); cp.name='COMPACT_'+ob.name; root.objects.link(cp); cp.location.y+=500
        if ob.name.startswith('COAST_SECTOR_'): cp.instance_collection=coast
    elif ob.type=='LIGHT':
        cp=ob.copy(); root.objects.link(cp)
    elif ob.type=='MESH':
        cp=ob.copy(); cp.name='COMPACT_'+ob.name; root.objects.link(cp)
        if ob.name.startswith('Exact_Site_'):
            cp.data=ob.data.copy(); cp.name='SITE_2000x1000_METERS'
            for v in cp.data.vertices: v.co.y*=.5
            cp.data.update()
        elif ob.name.startswith('Atlantic_Water'): cp.location.y+=500
        else: cp.location.y-=500

for name,loc,target,lens in [
    ('COMPACT_AERIAL',(1800,-1850,1800),(0,0,0),43),
    ('COMPACT_DISTRICT',(190,-610,190),(-30,-280,3),36),
    ('RETAIL_WALK',(-182,-330,1.72),(-171,-315,1.95),26),
    ('RETAIL_CAFE',(-187,-320,1.72),(-182,-316,1.65),29),
    ('RETAIL_SHOPS',(-80,-331,1.72),(-50,-314,2.0),28)]:
    data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); root.objects.link(ob); ob.location=loc; data.lens=lens; data.clip_end=15000
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
s.camera=bpy.data.objects['RETAIL_WALK']
try: s.render.engine='CYCLES'
except TypeError: s.render.engine=[i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items][0]
s.cycles.samples=32; s.cycles.use_denoising=True; s.cycles.max_bounces=8
s.render.resolution_x=1600; s.render.resolution_y=900; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX'; s.view_settings.exposure=.25
s['map_size_m']='2000 x 1000'; s['sector_count']=40; s['coastal_business_count']=commerces*10; s['coastal_reception_count']=10
s['businesses_per_coastal_sector']=commerces; s['note']='Commercial facades and display interiors; no gameplay interactions implemented.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'Resort_Ipanema_2x1km_Comercio.blend')
print('SAVED_COMPACT_RETAIL',s.name,'sectors',len([o for o in s.objects if o.instance_type=='COLLECTION']),'businesses',commerces*10)
print('MAP_SIZE',bpy.data.objects['SITE_2000x1000_METERS'].dimensions[:])
