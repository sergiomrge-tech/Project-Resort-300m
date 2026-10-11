import bpy, math, random
from mathutils import Vector
random.seed(20261009)
ROOT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
source=bpy.data.collections['IPANEMA_NEW_MAP_200x200']
previous=bpy.context.scene
scene=bpy.data.scenes.new('RESORT_IPANEMA_2x2KM')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.world=previous.world.copy()
mapcol=bpy.data.collections.new('MAP_2000x2000_METERS'); scene.collection.children.link(mapcol)
landscape=bpy.data.collections.new('INFRASTRUCTURE_AND_BOUNDARY'); mapcol.children.link(landscape)
stone=bpy.data.materials['IP_Limestone']; grass=bpy.data.materials['IP_Groundcover']; water=bpy.data.materials['IP_Water']; wood=bpy.data.materials['IP_Teak']; asphalt=bpy.data.materials['asphalt_03']; paving=bpy.data.materials['checkered_pavement_tiles']; leaf=bpy.data.materials['IP_Leaf']; leaf2=bpy.data.materials['IP_Leaf_Sunlit']; trunk=bpy.data.materials['IP_Bark']; fabric=bpy.data.materials['IP_Linen']; metal=bpy.data.materials['IP_Bronze']
batch={}
def geom(name,v,f,m,collection):
    key=(collection.name,name,m.name)
    vv,ff,mm,cc=batch.setdefault(key,([],[],m,collection)); off=len(vv); vv.extend(v); ff.extend(tuple(i+off for i in face) for face in f)
def box(name,p,d,m,collection):
    x,y,z=p; a,b,c=[t*.5 for t in d]
    v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    geom(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,collection)
def plant(x,y,h,collection):
    box('Park_Trunks',(x,y,h*.4),(.25,.25,h*.8),trunk,collection)
    for j in range(36):
        p=Vector((x+random.uniform(-1.7,1.7),y+random.uniform(-1.7,1.7),h+random.uniform(-1.1,1.1)))
        # Faceted lobes with enough segments to retain rounded silhouette.
        v=[]; n=12; k=8
        for a in range(k+1):
            ph=math.pi*a/k
            for b in range(n):
                t=b*math.tau/n; v.append(tuple(p+Vector((.55*math.sin(ph)*math.cos(t),.5*math.sin(ph)*math.sin(t),.6*math.cos(ph)))))
        geom('Park_Foliage',v,[(a*n+b,a*n+(b+1)%n,(a+1)*n+(b+1)%n,(a+1)*n+b) for a in range(k) for b in range(n)],leaf if j%4 else leaf2,collection)

coast=bpy.data.collections.new('MODULE_COAST_200m')
urban=bpy.data.collections.new('MODULE_GARDEN_DISTRICT_200m')
market=bpy.data.collections.new('MODULE_MARKET_DISTRICT_200m')
# Asset collections are referenced by instances and intentionally not linked directly into the map scene.
coast['module_size_m']=200; urban['module_size_m']=200; market['module_size_m']=200
exclude=('Beach__','Sea__','Beach_Kiosk','Parasols_','Loungers_')
for ob in source.objects:
    if ob.type not in ('MESH','FONT') or ob.hide_render: continue
    if ob.name.startswith('Galeria_Mar_') or ob.name=='Sign_GALERIA MAR': ob.location.x=-5
    if ob.name.startswith('Mercado_Local_') or ob.name=='Sign_MERCADO LOCAL': ob.location.x=-3
    coast.objects.link(ob)
    if not ob.name.startswith(exclude):
        urban.objects.link(ob); market.objects.link(ob)

# Complete inland strips with useful landscape / commercial amenities, never inland beaches.
for c in (urban,market):
    box('Inland_Garden', (0,-84,.27),(200,31,.26),grass,c)
    box('Park_Path',(0,-78,.48),(200,3,.14),paving,c)
    for x in (-70,-20,30,80): box('Park_CrossPath',(x,-84,.48),(3,30,.14),paving,c)
    for x in range(-88,89,16):
        plant(x,-91,5.0+random.random()*1.2,c)
        box('Park_Benches',(x,-79.7,.8),(1.8,.6,.14),wood,c)
        box('Park_Benches',(x,-79.4,1.15),(1.8,.1,.55),wood,c)
    for x in (-55,45):
        box('Reflecting_Pond',(x,-88,.41),(22,12,.13),water,c)
        for dx in (-11.3,11.3): box('Pond_Coping',(x+dx,-88,.46),(.5,13,.2),stone,c)
        for dy in (-6.3,6.3): box('Pond_Coping',(x,-88+dy,.46),(23,.5,.2),stone,c)
    for x in (-66,-30):
        for y in (10,20,30,40):
            box('Pool_Loungers',(x,y,.65),(.8,2,.18),wood,c)
            box('Pool_Loungers',(x,y-.2,.8),(.7,1.4,.12),fabric,c)
    # Fixed service and perimeter road network.
    for x in (-97,97): box('Perimeter_Road',(x,0,.13),(6,200,.26),asphalt,c)
    for y in (-97,97): box('Perimeter_Road',(0,y,.13),(194,6,.26),asphalt,c)

for x in (-75,-35,5,45,85):
    box('Market_Stall',(x,-73,1.1),(4,2,1.4),wood,market)
    box('Market_Canopy',(x,-73,2.3),(5,3,.2),fabric,market)
    for dx in (-1.7,1.7): box('Market_Supports',(x+dx,-73,1.65),(.09,.09,1.7),metal,market)

# The coastal district connects to the grid at its northern edge and end streets.
box('Coast_Connector',(0,97,.15),(200,6,.3),asphalt,coast)
for x in (-97,97): box('Coast_EndStreet',(x,28,.16),(6,144,.3),asphalt,coast)

box('Exact_Site_2000x2000',(0,0,-.8),(2000,2000,1.6),stone,landscape)
box('Atlantic_Water_Within_Map',(0,-945,.115),(2000,110,.21),water,landscape)
box('North_Linear_Park',(0,955,.26),(2000,90,.35),grass,landscape)
box('North_Park_Path',(0,925,.5),(2000,5,.15),paving,landscape)
box('North_Park_Path',(0,980,.5),(2000,5,.15),paving,landscape)
for x in range(-970,971,35):
    plant(x,947,7+random.random()*2,landscape); plant(x+8,966,6+random.random()*2,landscape)
    if x%5==0: box('North_Park_Benches',(x,929,.8),(1.8,.6,.14),wood,landscape)
for x in range(-900,901,200): box('Park_NorthSouth_Path',(x,950,.5),(5,90,.15),paving,landscape)

for (cname,name,mname),(v,f,m,c) in batch.items():
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.materials.append(m); me.update()
    ob=bpy.data.objects.new(name+'__'+mname,me); c.objects.link(ob)
    uv=me.uv_layers.new(name='WorldMeters')
    for p in me.polygons:
        axis=0
        if abs(p.normal.y)>abs(p.normal.x): axis=1
        if abs(p.normal.z)>abs(p.normal[axis]): axis=2
        for i in p.loop_indices:
            co=me.vertices[me.loops[i].vertex_index].co
            uv.data[i].uv=(co.y*.25,co.z*.25) if axis==0 else ((co.x*.25,co.z*.25) if axis==1 else (co.x*.25,co.y*.25))
        if name=='Park_Foliage': p.use_smooth=True

sectors=[]
for ix in range(10):
    x=-900+ix*200
    ob=bpy.data.objects.new('COAST_SECTOR_%02d'%ix,None); mapcol.objects.link(ob); ob.instance_type='COLLECTION'; ob.instance_collection=coast; ob.location=(x,-790,0)
    ob['sector_size_m']=200; ob['district']='coastal'; sectors.append(ob)
    for iy in range(8):
        y=-590+iy*200
        c=market if (ix+iy)%3==0 else urban
        ob=bpy.data.objects.new('CITY_SECTOR_%02d_%02d'%(ix,iy),None); mapcol.objects.link(ob); ob.instance_type='COLLECTION'; ob.instance_collection=c; ob.location=(x,y,0)
        # Alternate inland orientation: same proportions, varied frontage and route directions.
        ob.rotation_euler.z=math.pi if (ix+iy)%2 else 0
        ob['sector_size_m']=200; ob['district']='market' if c==market else 'garden'; sectors.append(ob)

sun_data=bpy.data.lights['IP_Sun'].copy(); sun=bpy.data.objects.new('CITY_SUN',sun_data); mapcol.objects.link(sun); sun.rotation_euler=bpy.data.objects['IP_Sun'].rotation_euler
for name,loc,target,lens in [
    ('CITY_AERIAL',(2100,-2850,2300),(0,0,0),44),
    ('CITY_DISTRICT',(190,-1110,190),(-30,-780,3),36),
    ('CITY_WALK',(-141,-846,1.8),(-164,-803,8),29),
    ('CITY_POOL',(-125,-785,2.1),(-151,-765,3.5),25)]:
    data=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,data); mapcol.objects.link(ob); ob.location=loc; data.lens=lens; data.clip_end=15000
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['CITY_AERIAL']
try: scene.render.engine='CYCLES'
except TypeError: scene.render.engine=[i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items][0]
scene.cycles.samples=24; scene.cycles.use_denoising=True; scene.cycles.max_bounces=5
scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'; scene.view_settings.exposure=.25
scene['map_size_m']='2000 x 2000'; scene['sector_count']=90; scene['layout_seed']=20261009
scene['layout_note']='10 coastal sectors, 80 inland sectors, Atlantic margin and north linear park. Shared geometry, buildings at original scale.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'Resort_Ipanema_2x2km.blend')
print('CITY_SAVED',len(sectors),'sectors',len(scene.objects),'direct objects')
print('SITE_BOUNDARY',bpy.data.objects['Exact_Site_2000x2000__IP_Limestone'].dimensions[:])
print('SOURCE_POLYGONS',sum(len(o.data.polygons) for o in source.objects if o.type=='MESH'))
