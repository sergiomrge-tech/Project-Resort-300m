import bpy,math,json,random
from mathutils import Vector
random.seed(21)
OUT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
if bpy.data.scenes.get('MARE_UNIDA_ETAPA_01'):raise RuntimeError('Unified revision already exists')
old=bpy.context.scene
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];teal=bpy.data.materials['MARE_Painted_Teal'];steel=bpy.data.materials['MARE_Brushed_Stainless'];brass=bpy.data.materials['MARE_Brushed_Brass'];cream=bpy.data.materials['MARE_Linen_Canvas'];dark=bpy.data.materials['MARE_Charcoal'];plaster=bpy.data.materials['URBAN_PBR_IP_Ivory_Painted_Render'];curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete'];pavers=bpy.data.materials['URBAN_PBR_Retail_Concrete_Pavers'];glass=bpy.data.materials['MARE_Architectural_Glass'];water=bpy.data.materials['MARE_Pool_Water']
def col(name):return bpy.data.collections.new('UNIDA_'+name)
def box(name,loc,size,mat,c,edge=.012):
    x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    me=bpy.data.meshes.new('UNIDA_'+name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    uv=me.uv_layers.new(name='UrbanMeters');wg=me.uv_layers.new(name='WoodGrain')
    for f in me.polygons:
        n=max((abs(f.normal[k]),k) for k in range(3))[1];axes=[k for k in range(3) if k!=n]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;co=(p[axes[0]]+loc[axes[0]],p[axes[1]]+loc[axes[1]]);uv.data[li].uv=co;wg.data[li].uv=co
    o=bpy.data.objects.new('UNIDA_'+name,me);c.objects.link(o);o.location=loc
    if edge:b=o.modifiers.new('Finished corners','BEVEL');b.width=edge;b.segments=2
    return o
def label(name,body,loc,size,c):
    d=bpy.data.curves.new('UNIDA_'+name,'FONT');d.body=body;d.align_x='CENTER';d.size=size;d.extrude=.008
    o=bpy.data.objects.new('UNIDA_'+name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(brass);return o
def instance(name,source,c,loc=(0,0,0)):
    o=bpy.data.objects.new('UNIDA_'+name,None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=source;o.location=loc;return o
def subset(name,source,tokens):
    c=col(name)
    for o in source.objects:
        if any(t in o.name for t in tokens):c.objects.link(o)
    return c
def shell(c,title,x,y,w,d,floor=.45,levels=1,rooms=False):
    box(title+'_Foundation',(x,y,.22),(w,d,.44),curb,c,.035)
    for level in range(levels):
        z=floor+level*3.2
        box(title+'_Floor',(x,y,z),(w,d,.16),pavers,c)
        # Continuous hotel frontage: mullions, glazed doors and shared cornices.
        for sign in [-1,1]:
            wall_y=y+sign*d/2
            count=max(2,round(w/3))
            for j in range(count):
                px=x-w/2+(j+.5)*w/count
                box(title+'_Facade_Glass',(px,wall_y,z+1.5),(w/count-.14,.06,2.8),glass,c,0)
                box(title+'_Mullion',(px-w/count/2,wall_y-.02,z+1.5),(.12,.16,3),wood,c)
            box(title+'_Continuous_Lintel',(x,wall_y,z+2.98),(w,.22,.18),wood,c)
            if rooms:
                box(title+'_Balcony',(x,wall_y+sign*.95,z-.02),(w,1.9,.16),curb,c,.025)
                box(title+'_Balcony_Front',(x,wall_y+sign*1.8,z+.56),(w,.035,.95),glass,c,0)
                box(title+'_Balcony_Rail',(x,wall_y+sign*1.8,z+1.06),(w,.055,.07),brass,c)
        for sign in [-1,1]:
            # Side walls use pillars rather than an impassable solid seam between upgrades.
            xx=x+sign*w/2
            for yy in [y-d/2,y+d/2]:box(title+'_Structural_Pier',(xx,yy,z+1.45),(.30,.30,2.9),plaster,c)
            box(title+'_Side_Glass',(xx,y,z+1.5),(.06,d-.6,2.7),glass,c,0)
        box(title+'_Roof',(x,y,z+3.10),(w,d,.22),curb,c,.03)
        for yy in [y-d/2,y+d/2]:box(title+'_Roof_Fascia',(x,yy,z+3.15),(w,.18,.30),teal,c)
    label(title+'_Sign',title.replace('_',' ').upper(),(x,y-d/2-.13,floor+2.50),.27,c)
    if rooms:
        for level in range(levels):
            z=floor+level*3.2
            for j in range(max(2,round(w/6))):
                xx=x-w/2+(j+.5)*w/max(2,round(w/6));bed(c,xx,y,z)
def bed(c,x,y,z):
    box('Bed_Frame',(x,y,z+.25),(1.85,2.1,.38),wood,c,.025);box('Bed_Mattress',(x,y,z+.5),(1.8,2,.22),cream,c,.055)
    box('Bed_Headboard',(x,y+.98,z+.79),(1.95,.10,1.1),teal,c,.025)
    for xx in [-.45,.45]:box('Pillow',(x+xx,y+.6,z+.69),(.7,.42,.16),cream,c,.06)
    box('Bed_Runner',(x,y-.58,z+.63),(1.81,.5,.025),teal,c)
def corridor(c,name,a,b,width=2.2,covered=True):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.sqrt(dx*dx+dy*dy)
    if length<.1:return
    axis=0 if abs(dx)>abs(dy) else 1;cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2
    size=(length,width) if axis==0 else (width,length)
    box(name+'_Floor',(cx,cy,.43),(*size,.14),pavers,c)
    if covered:
        box(name+'_Roof',(cx,cy,3.55),(*size,.22),curb,c)
        for sign in [-1,1]:
            if axis==0:loc=(cx,cy+sign*width/2,2);dims=(length,.12,3)
            else:loc=(cx+sign*width/2,cy,2);dims=(.12,length,3)
            box(name+'_Glazed_Wall',loc,dims,glass,c,0)
        for p in [a,b]:box(name+'_Pier',(p[0],p[1],1.85),(.18,.18,2.8),wood,c)

# Correct close-up props before reusing them in the transformations.
kiosk=bpy.data.collections['MARE_01_QUIOSQUE_ORIGINAL']
for o in kiosk.objects:
    if any(o.name.startswith('MARE_'+n) for n in ['Menu_Chalkboard','Menu_Inset','Menu']):
        if o.location.x<0:o.location.x+=4.12
for o in list(kiosk.objects):
    if o.name.startswith('MARE_Cold_Display_Cabinet'):bpy.data.objects.remove(o,do_unlink=True)
for xx in [1.75,2.55]:box('Refrigerator_Side',(xx,-15.52,1.16),(.04,.75,1.4),teal,kiosk)
for zz in [.47,1.85]:box('Refrigerator_Slab',(2.15,-15.52,zz),(.82,.75,.05),teal,kiosk)
box('Refrigerator_Back',(2.15,-15.15,1.16),(.8,.035,1.35),dark,kiosk)
box('Refrigerator_Base',(2.15,-15.52,.60),(.82,.75,.25),teal,kiosk)

# Shared scenery, without the disconnected prototype campus.
context=col('ORLA_CONTINUA')
sourcebase=bpy.data.collections['MARE_ORLA_PERMANENTE']
for o in sourcebase.objects:
    if o.name.startswith('MARE_Land') or o.type=='CAMERA':continue
    if o.instance_collection and o.instance_collection.name=='MARE_PALM_REUSABLE' and -56<o.location.x<56 and -24<o.location.y<60:continue
    context.objects.link(o)
box('Continuous_Mainland',(0,930,-.4),(2500,1954,.8),bpy.data.materials['MARE_Coastal_Garden'],context,0)
box('Continuous_Sea',(0,-1550,-.66),(3000,3000,.12),bpy.data.materials['RIO_Atlantic_Water_Backdrop'],context,0)
def cam(name,loc,target,lens):
    d=bpy.data.cameras.new('UNIDA_'+name);o=bpy.data.objects.new('UNIDA_'+name,d);context.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=5000;return o
hero=cam('Camera_Kiosk',(12,-32,8.2),(0,-16,1.7),43)
front=cam('Camera_Restaurant',(35,-50,17),(0,-7,2),43)
hotelcam=cam('Camera_Hotel',(50,-62,25),(0,-1,3),43)
finalcam=cam('Camera_Unified_Resort',(-95,-110,105),(0,11,3),43)
shore=cam('Camera_Orla',(70,-90,16),(0,-11,3),42)

equipment=subset('FOUNDING_BAR_REUSABLE',kiosk,['Espresso','Grinder','Hopper','Coffee_Bean','POS','Sink','Faucet','Refrigerat','Cold_Display_Glass','Floating_Teak_Shelf','Shelf_Bracket','Bottle','Menu','Cup','Rear_Workbench','Prep_Cabinet','Drawer','Fruit_Crate','Fresh_Coconut','Customer_Counter','Counter_Brass','Front_Teak_Batten','Historic_Plaque','Pendant','Task_Light'])
prep=subset('KITCHEN_EQUIPMENT',bpy.data.collections['MARE_03_PREPARO_ESTOQUE'],['Commercial_Range','Range_Burner','Extraction_Hood','Storage_Rack'])
sanitary=subset('SANITARY_EQUIPMENT',bpy.data.collections['MARE_04_SANITARIOS'],['Washbasin','Tap','Mirror','WC_'])
kids=subset('KIDS_EQUIPMENT',bpy.data.collections['MARE_13_KIDS_CLUB'],['Play_Table','Play_Frame','Swing'])
gym=subset('GYM_EQUIPMENT',bpy.data.collections['MARE_14_ACADEMIA_YOGA'],['Treadmill','Fitness_Console','Yoga_Mat'])
spa=subset('SPA_EQUIPMENT',bpy.data.collections['MARE_15_SPA'],['Massage_Table','Spa_Privacy'])
dining=subset('DINING_EQUIPMENT',bpy.data.collections['MARE_16_GASTRONOMIA'],['Table','Cup','Vase','Flower'])
events=subset('EVENT_EQUIPMENT',bpy.data.collections['MARE_18_EVENTOS'],['Table','Cup','Vase','Flower','Event_Stage'])
laundry=subset('LAUNDRY_EQUIPMENT',bpy.data.collections['MARE_19_SUSTENTABILIDADE'],['Laundry_Machine','Laundry_Door','Solar_'])

# Replacements model the SAME business being renovated; asset subsets are reused.
earlydeck=col('02_DECK_QUIOSQUE');instance('Initial_Deck',bpy.data.collections['MARE_02_DECK_MESAS'],earlydeck,(2,3,0))
restaurantdeck=col('02_DECK_RESTAURANTE');instance('Restaurant_Terrace',bpy.data.collections['MARE_02_DECK_MESAS'],restaurantdeck,(2,-6,0))
earlyprep=col('03_PREPARO_QUIOSQUE');instance('Kitchen_Appendix',bpy.data.collections['MARE_03_PREPARO_ESTOQUE'],earlyprep,(0,-4,0));corridor(earlyprep,'First_Physical_Connection',(0,-12),(0,-11),2)
restaurantshell=col('04_RESTAURANTE_TRANSFORMADO');shell(restaurantshell,'Mare_Restaurante',0,-9,20,22)
restaurantbar=col('04_BAR_NO_RESTAURANTE');instance('Original_Bar_Inside_Restaurant',equipment,restaurantbar)
restaurantprep=col('03_PREPARO_RESTAURANTE');instance('Restaurant_Kitchen',prep,restaurantprep,(0,3,0))
earlywc=col('05_SANITARIOS_RESTAURANTE');instance('Restaurant_Bathrooms',bpy.data.collections['MARE_04_SANITARIOS'],earlywc,(-1.5,3,0))
hotelbase=col('06_HOTEL_SIMPLES');shell(hotelbase,'Mare_Hotel',0,-9,24,24,levels=2,rooms=True)
box('Front_Reception_Desk',(0,-15,1.04),(5,1,1.15),wood,hotelbase,.04)
label('Lobby_Welcome','RECEPÇÃO  •  MARÉ',(0,-15.52,1.04),.22,hotelbase)
rearrestaurant=col('06_RESTAURANTE_NOS_FUNDOS');shell(rearrestaurant,'Restaurante_Mare',0,15,24,20)
instance('Founding_Bar_Moved_To_Rear',equipment,rearrestaurant,(0,31,0));instance('Kitchen_At_Back',prep,rearrestaurant,(0,28,0));corridor(rearrestaurant,'Hotel_Restaurant_Link',(0,3),(0,5),4)
hotelwc=col('05_SANITARIOS_INTEGRADOS');instance('Hotel_Bathrooms',sanitary,hotelwc,(-7,4,0))
left=col('07_ALA_ESQUERDA');shell(left,'Ala_Jardim',-21,-3,18,36,levels=2,rooms=True)
right=col('08_ALA_DIREITA');shell(right,'Ala_Orla',21,-3,18,36,levels=2,rooms=True)
technical=col('09_COZINHA_E_OPERACAO');shell(technical,'Operacao',0,30.5,24,11)
for x in [-8,0,8]:box('Service_Cabinet',(x,31,1.4),(1.7,1,2.5),steel,technical)
pool=col('10_PISCINA_PATIO');instance('Pool_Courtyard',bpy.data.collections['MARE_11_PISCINA'],pool,(1,2,0));corridor(pool,'Wing_To_Pool',(-21,15),(-21,17),4);corridor(pool,'Restaurant_To_Pool',(-12,21),(-14.5,21),3)
club=col('11_LOUNGE_ORLA');instance('Connected_Beach_Lounge',bpy.data.collections['MARE_06_BEACH_CLUB'],club,(-2,3,0));corridor(club,'Wing_To_Beach_Lounge',(-30,-16),(-32,-16),5)
family=col('12_FAMILIA');shell(family,'Clube_Infantil',21,24,18,18);instance('Kids_Interior',kids,family,(-24,-18,0))
fitness=col('13_FITNESS_PISO_SUPERIOR');shell(fitness,'Fitness_Yoga',21,24,18,18,3.65);instance('Fitness_Interior',gym,fitness,(-34,-52,3.2))
wellness=col('14_SPA_ANEXADO');shell(wellness,'Spa_Mare',40,21,20,24);instance('Spa_Interior',spa,wellness,(80,-119,0))
signature=col('15_GASTRONOMIA_PISO_SUPERIOR');shell(signature,'Gastronomia_Autoral',0,15,24,20,3.65);instance('Dining_Interior',dining,signature,(-40,-93,3.2))
suites=col('16_SUITES_PRIVATIVAS');shell(suites,'Suites_Privativas',40,21,20,24,3.65,rooms=True)
celebration=col('17_EVENTOS_INTEGRADOS');shell(celebration,'Eventos',0,44,24,16);instance('Event_Interior',events,celebration,(0,-104,0))
resources=col('18_LAVANDERIA_E_RECURSOS');shell(resources,'Lavanderia',-23,48,22,16);instance('Laundry_Interior',laundry,resources,(-118,-84,0))
upgrade=col('19_AMPLIACAO_VERTICAL');shell(upgrade,'Suites_Premium_Centro',0,-9,24,24,6.85,rooms=True);shell(upgrade,'Suites_Premium_Jardim',-21,-3,18,36,6.85,rooms=True)
finish=col('20_RESORT_UNICO');shell(finish,'Suites_Premium_Orla',21,-3,18,36,6.85,rooms=True)
# One continuous crown and one arrival canopy visually bind the three guest wings.
box('Unified_Front_Crown',(0,-21.15,9.99),(60.4,.32,.48),teal,finish,.04)
box('Unified_Front_Brass_Line',(0,-21.34,9.85),(60.5,.025,.035),brass,finish)
box('Arrival_Canopy',(0,-26.5,3.6),(13,9,.27),curb,finish,.04)
for x in [-5.9,5.9]:
    for y in [-29.9,-23.1]:box('Arrival_Column',(x,y,1.85),(.32,.32,3.4),plaster,finish,.025)
label('Final_Identity','MARÉ RESORT',(0,-21.36,8.72),1.0,finish)
for x in [-25,25]:
    box('Roof_Garden_Bed',(x,24,6.98),(4,12,.42),wood,finish)
    box('Roof_Garden_Green',(x,24,7.22),(3.8,11.8,.07),bpy.data.materials['MARE_Coastal_Garden'],finish)
for x in [-5.5,5.5]:
    box('Entry_Planter',(x,-31,.5),(2,1.2,1),wood,finish)
    box('Entry_Planter_Green',(x,-31,1.05),(1.8,1,.16),bpy.data.materials['MARE_Coastal_Garden'],finish)
box('Orla_To_Arrival',(0,-33.5,.16),(4,4,.2),pavers,finish)

stages={7:left,8:right,9:technical,10:pool,11:club,12:family,13:fitness,14:wellness,15:signature,16:suites,17:celebration,18:resources,19:upgrade,20:finish}
for number,c in stages.items():
    c['unlock_stage']=number;c['module_id']='mare_unified_%02d'%number
    for o in c.objects:o['unlock_stage']=number;o['module_id']=c['module_id']
for i in range(1,21):
    scene=bpy.data.scenes.new('MARE_UNIDA_ETAPA_%02d'%i);scene.collection.children.link(context)
    if i<4:
        scene.collection.children.link(kiosk)
        if i>=2:scene.collection.children.link(earlydeck)
        if i>=3:scene.collection.children.link(earlyprep)
    elif i<6:
        for c in [restaurantshell,restaurantbar,restaurantdeck,restaurantprep]:scene.collection.children.link(c)
        if i>=5:scene.collection.children.link(earlywc)
    else:
        for c in [hotelbase,rearrestaurant,hotelwc]:scene.collection.children.link(c)
        for stage,c in stages.items():
            if i>=stage:scene.collection.children.link(c)
    scene.world=bpy.data.worlds['MARE_World_01'];scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.camera=hero if i<4 else (front if i<6 else (hotelcam if i<10 else finalcam))
    scene['progression_stage']=i;scene['architectural_revision']=2;scene['same_business_transforms']=True;scene['founding_bar_reused']=True;scene['restaurant_location']='rear' if i>=6 else 'original plot';scene['runtime_state']='Blender assembly only, not integrated gameplay'
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_06']
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=OUT+'Mare_Evolucao_Unificada_v2.blend')
print('UNIFIED_20_STAGES_READY: kiosk -> restaurant -> hotel with rear restaurant -> connected resort')
