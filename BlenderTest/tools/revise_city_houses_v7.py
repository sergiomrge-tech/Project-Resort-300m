import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
OUT=ROOT/'Resort_Main_Map_Mare_Houses_v7.blend'
random.seed(7010)
city=bpy.data.collections['MAIN_CITY_WITH_MARE_LOT']
stats={'inland_sectors':0,'coastal_sectors':0,'houses':0,'shops':0,'removed_pool_objects':0,'removed_legacy_building_objects':0,'variants':20}
materials=bpy.data.materials
def material(name,fallback=None): return materials.get(name) or materials[fallback]
paints=[material('URBAN_PBR_'+n+'_Painted_Render',n) for n in ['IP_Coral_Plaster','IP_Teal_Plaster','IP_Sage_Plaster','IP_Ochre_Plaster','IP_Ivory']]
stone=material('URBAN_PBR_Facade_Cast_Concrete','IP_Limestone')
paving=material('URBAN_PBR_Sidewalk_Stone_Pavers','IP_Limestone')
wood=materials['IP_Teak'];metal=materials['IP_Bronze'];dark=materials['IP_Window_Recess'];glass=materials['IP_Glass'];grass=materials['IP_Groundcover'];leaf=materials['IP_Leaf'];terra=materials['IP_Terracotta'];paint=materials['IP_Road_Paint'];asphalt=material('asphalt_03','IP_Asphalt')
roof=terra.copy();roof.name='HOUSES_V7_Terracotta_Roof';roof.use_nodes=True
p=next(n for n in roof.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.78
nt=roof.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=4;nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.20,.075,.035,1);ramp.color_ramp.elements[1].color=(.55,.24,.105,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.012;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
signmat=materials['SHOP_Lettering'];warm=materials['SHOP_Warm_Luminaires'];teal=materials['SHOP_Midnight_Teal'];clear=materials.get('SHOP_Clear_Display_Glass') or glass

class Builder:
 def __init__(self,c):self.c=c;self.batch={}
 def geo(self,name,v,f,m):
  vv,ff,mm=self.batch.setdefault((name,m.name),([],[],m));off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in face) for face in f)
 def box(self,name,p,d,m):
  x,y,z=p;a,b,c=[s/2 for s in d];v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)];self.geo(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
 def cylinder(self,name,p,r,h,m,n=16):
  x,y,z=p;v=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),zz) for zz in [z-h/2,z+h/2] for i in range(n)];self.geo(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
 def text(self,text,p,size,m):
  data=bpy.data.curves.new('V7_Sign_'+text,'FONT');data.body=text;data.align_x='CENTER';data.size=size;data.extrude=.006;data.materials.append(m);o=bpy.data.objects.new('V7_Sign_'+text,data);self.c.objects.link(o);o.location=p;o.rotation_euler=(math.pi/2,0,0)
 def finish(self):
  for (name,mname),(v,f,m) in self.batch.items():
   me=bpy.data.meshes.new('V7_'+name);me.from_pydata(v,[],f);me.materials.append(m);me.update()
   for uvname in ['UrbanMeters','WorldMeters','UVMap','WoodGrain']:
    layer=me.uv_layers.new(name=uvname)
    for face in me.polygons:
     axis=max(range(3),key=lambda i:abs(face.normal[i]))
     for li in face.loop_indices:
      co=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(co.x,co.y) if axis==2 else ((co.x,co.z) if axis==1 else (co.y,co.z))
   o=bpy.data.objects.new('V7_'+name+'__'+mname,me);self.c.objects.link(o)
   if name in ['Roof_Tiles','Rain_Downpipes','Door_Handles','Planters']:
    for face in me.polygons:face.use_smooth=True
   if name in ['Facade_Trim','Shop_Counters','Window_Shutters','Wood_Doors','Balcony_Deck']:
    mod=o.modifiers.new('Rounded craftsmanship','BEVEL');mod.width=.018;mod.segments=2

shopnames=['PADARIA DO BAIRRO','MERCADO DA VILA','HORTIFRUTI BRISA','CAFÉ DO JARDIM','FARMÁCIA SOL','BARBEARIA MARÉ','LAVANDERIA AZUL','OFICINA DE BICICLETAS','PAPELARIA COLORIDA','ARTESANATO LOCAL','SORVETERIA TROPICAL','PET SHOP AMIGOS']
templates=[]
for k in range(20):
 shop=k>=8;floors=2 if k%3==0 or k in [2,5,10,14] else 1
 c=bpy.data.collections.new('V7_HOME_%02d_%s'%(k,'SHOP' if shop else 'RESIDENTIAL'));templates.append(c);c['floors']=floors;c['kind']='shop_home' if shop else 'home';c['shop_name']=shopnames[k-8] if shop else '';c['width_m']=15.2;c['depth_m']=12.8
 b=Builder(c);plaster=paints[k%5];top=.58+3.15*floors
 b.box('Foundation',(0,0,.30),(15.2,12.8,.6),stone);b.box('Interior_Floor',(0,0,.57),(14.6,12.2,.08),wood)
 b.box('Rear_Wall',(0,6.2,(.58+top)/2),(15,.28,top-.58),plaster)
 for x in [-7.36,7.36]:b.box('Side_Walls',(x,0,(.58+top)/2),(.28,12.5,top-.58),plaster)
 if shop:
  for x in [-7.2,-2.45,2.45,7.2]:b.box('Front_Piers',(x,-6.21,2.03),(.32,.30,2.9),plaster)
  b.box('Front_Upper_Lintel',(0,-6.21,3.38),(15,.30,.7),plaster)
  b.box('Shop_Sill',(-2.8,-6.23,.78),(8.8,.26,.38),stone)
  b.box('Display_Glass',(-2.8,-6.255,1.98),(8.45,.035,2.08),clear)
  b.box('Shop_Door_Glass',(4.65,-6.26,1.82),(3.7,.035,2.46),clear)
  for x in [-7.1,-2.6,1.6,2.8,4.65,6.6]:b.box('Shop_Window_Frames',(x,-6.29,1.9),(.07,.11,2.55),metal)
  b.cylinder('Door_Handles',(3.12,-6.36,1.70),.035,.34,metal)
  b.box('Shop_Counters',(-2,-2.8,1.1),(4.8,.85,1.03),wood);b.box('Stone_Countertop',(-2,-2.8,1.65),(5,.95,.09),stone)
  b.box('Cash_Register',(-.25,-2.8,1.82),(.48,.38,.25),dark)
  for z in [1,1.7,2.4]:
   b.box('Product_Shelves',(-1.4,5.64,z),(10,.52,.08),wood)
   for j in range(14):b.box('Shop_Products',(-5.8+j*.67,5.48,z+.18),(.30,.25,.28),paints[(j+k)%5])
  if k-8 in [0,3,10]:
   for x in [-5,0]:
    b.cylinder('Cafe_Table_Legs',(x,-4.3,.99),.06,.80,metal);b.cylinder('Cafe_Table_Tops',(x,-4.3,1.43),.65,.08,wood)
    for dx in [-.9,.9]:
     b.box('Cafe_Seats',(x+dx,-4.3,.98),(.5,.5,.12),wood);b.box('Cafe_Backrests',(x+dx,-4.08,1.29),(.5,.10,.56),wood)
     for lx in [-.18,.18]:b.box('Cafe_Chairlegs',(x+dx+lx,-4.3,.73),(.06,.34,.5),metal)
  b.box('Store_Sign_Fascia',(0,-6.44,3.23),(14.2,.20,.58),teal)
  b.text(shopnames[k-8],(0,-6.56,3.09),min(.36,12.5/(len(shopnames[k-8])*.65)),signmat)
  b.geo('Shop_Striped_Awning',[(-7.15,-6.35,3.59),(7.15,-6.35,3.59),(7.15,-7.9,3.12),(-7.15,-7.9,3.12)],[(0,1,2,3)],plaster)
  for j in range(20):
   x=-7.15+j*.715;b.geo('Awning_Light_Stripes',[(x,-6.35,3.60),(x+.34,-6.35,3.60),(x+.34,-7.9,3.13),(x,-7.9,3.13)],[(0,1,2,3)],materials['IP_Linen'])
  b.cylinder('Interior_Luminaire',(0,-1,3.48),.44,.09,warm)
 else:
  b.box('Domestic_Front_Wall',(0,-6.2,(.58+top)/2),(15,.28,top-.58),plaster)
  b.box('Wood_Doors',(0,-6.39,1.78),(1.35,.12,2.40),wood)
  for x in [-.78,.78]:b.box('Facade_Trim',(x,-6.46,1.80),(.16,.16,2.70),stone)
  b.box('Facade_Trim',(0,-6.46,3.12),(1.7,.16,.18),stone)
  b.cylinder('Door_Handles',(.45,-6.51,1.67),.035,.22,metal)
  b.box('Front_Porch',(0,-7.10,.5),(6,1.85,.16),paving)
  b.text(str(100+k*7),(1.45,-6.50,2.15),.24,metal)
 for level in range(floors):
  if shop and level==0:continue
  z=2.1+level*3.15
  for x in [-4.9,4.9]:
   b.box('Window_Recess',(x,-6.37,z),(2.32,.08,1.55),dark);b.box('Window_Glass',(x,-6.42,z),(2.09,.028,1.36),glass)
   for dx in [-1.14,0,1.14]:b.box('Window_Frames',(x+dx,-6.46,z),(.085,.08,1.56),metal)
   for zz in [z-.77,z+.77]:b.box('Facade_Trim',(x,-6.47,zz),(2.43,.16,.12),stone)
   if k%2==0:
    for dx in [-1.5,1.5]:
     b.box('Window_Shutters',(x+dx,-6.45,z),(.48,.10,1.52),wood)
     for j in range(8):b.box('Shutter_Louvres',(x+dx,-6.53,z-.65+j*.18),(.44,.065,.035),metal)
 if floors==2:
  b.box('Upper_Floor_Slab',(0,0,3.70),(14.8,12.3,.16),stone)
  b.box('Balcony_Deck',(0,-6.94,3.77),(6.6,1.45,.16),stone)
  for x in [-3.2,0,3.2]:b.box('Balcony_Posts',(x,-7.56,4.3),(.065,.065,1),metal)
  b.box('Balcony_Handrail',(0,-7.56,4.80),(6.5,.09,.075),wood)
  for x in [j*.4-3 for j in range(16)]:b.box('Balcony_Balusters',(x,-7.56,4.28),(.035,.035,.99),metal)
 # Tile roof: curved individual tiles and ridge caps, proper eaves and drainpipes.
 eave=top+.16;rise=1.90
 b.geo('Gable_Roof_Base',[(-7.95,-6.95,eave),(7.95,-6.95,eave),(7.95,0,eave+rise),(-7.95,0,eave+rise),(-7.95,6.95,eave),(7.95,6.95,eave)],[(0,1,2,3),(3,2,5,4)],roof)
 for side in [-1,1]:
  for row in range(14):
   y0=side*(row*.50);y1=side*min(6.97,row*.50+.56)
   for col in range(44):
    x0=-7.94+col*.36;verts=[]
    for yy in [y0,y1]:
     for seg in range(5):
      a=math.pi*seg/4;xx=x0+.36*seg/4;zz=eave+rise*(1-abs(yy)/6.95)+.018+.048*math.sin(a);verts.append((xx,yy,zz))
    b.geo('Roof_Tiles',verts,[(i,i+1,i+6,i+5) for i in range(4)],roof)
 for side in [-1,1]:
  b.box('Rain_Gutters',(0,side*7.0,eave-.08),(16.2,.12,.13),metal)
  for x in [-7.28,7.28]:b.cylinder('Rain_Downpipes',(x,side*6.4,(eave+.6)/2),.052,eave-.6,metal)
  # Close the triangular gable walls at either building side.
 for x in [-7.36,7.36]:b.geo('Gable_Walls',[(x,-6.3,top),(x,6.3,top),(x,0,eave+rise-.06)],[(0,1,2)],plaster)
 for j in range(33):
  x0=-8+j*.49;b.geo('Roof_Ridge_Caps',[(x0,-.20,eave+rise),(x0+.55,-.20,eave+rise),(x0+.55,0,eave+rise+.12),(x0,0,eave+rise+.12),(x0,.20,eave+rise),(x0+.55,.20,eave+rise)],[(0,1,2,3),(3,2,5,4)],roof)
 if k%4==0:
  for x in [-3.6,-1.25,1.1]:
   y=2.0;z=eave+rise*(1-y/6.95)+.08;b.geo('Solar_Panels',[(x,y-.6,z+.17),(x+1.85,y-.6,z+.17),(x+1.85,y+1,z-.26),(x,y+1,z-.26)],[(0,1,2,3)],dark)
 b.box('Private_Access_Path',(0,-7.65,.47),(2.4,3,.12),paving)
 for x in [-6.1,6.1]:
  b.cylinder('Planters',(x,-7.24,.83),.38,.62,terra)
  for j in range(12):
   angle=j*math.tau/12;tip=(x+.45*math.cos(angle),-7.24+.45*math.sin(angle),1.60+j%3*.13);b.geo('Planter_Leaves',[(x,-7.24,1.12),(tip[0]+.09,tip[1],tip[2]),tip,(tip[0]-.09,tip[1],tip[2])],[(0,1,2,3)],leaf)
 b.finish()
 print('HOUSE_TEMPLATE',k,floors,shop,flush=True)

build_prefixes=('Casa_Coral_','Residencial_Sal_','Galeria_Mar_','Hotel_Atlantico_','Cafe_Jardim_','Mercado_Local_','Vila_Amarela_','Resort_Aurora_','Aurora_Suites_','Spa_Tropical_','Garden_Villa_','RETAIL_')
rear_prefixes=('Cafe_Jardim_','Mercado_Local_','Vila_Amarela_','Aurora_Suites_','Spa_Tropical_','Garden_Villa_')
remove_tags=('Pool_','Pond_','Reflecting_Pond','Courtyard_Deck','Villa_Path','Praca_','Restaurant_Terrace','Restaurant_Tables','Restaurant_Seats','Cafe_Tables','Cafe_Tabletops','Cafe_Seats','Cafe_Chair','Garden_Walkway','Garden_Crosswalk','GardenBeds','GardenTrees','GardenLeaves','Garden_Bench','ShrubLeaves','Aurora_SideFrames','Aurora_Sunscreens')
clones={};lot_records=[]
def slots(inland,reserved):
 rows=[(-16,False),(6,True),(37,False),(54,True),(84,False)] if inland else [(19,False),(48,True),(83,False)]
 lots=[]
 for y,face_north in rows:
  for x in [-81,-55,-29,-3]:
   if reserved and -95<x<16 and y<73:continue
   lots.append((x,y,face_north))
 for y,face_north in ([(-16,False),(8,True),(52,False),(81,True)] if inland else [(52,False),(81,True)]):
  for x in [43,64,85]:lots.append((x,y,face_north))
 return lots
def crop_front_palms(o,c):
 cp=o.copy();cp.data=o.data.copy();cp.name='V7_PRESERVED_ORLA_'+o.name
 bm=bmesh.new();bm.from_mesh(cp.data)
 kill=[f for f in bm.faces if (o.matrix_world@f.calc_center_median()).y>-27]
 if kill:bmesh.ops.delete(bm,geom=kill,context='FACES')
 if not bm.faces:bm.free();return
 bm.to_mesh(cp.data);bm.free();c.objects.link(cp)
def make_district(source,inland,reserved):
 key=(source.name,inland,reserved)
 if key in clones:return clones[key]
 c=bpy.data.collections.new('V7_'+('HOUSES_DISTRICT' if inland else 'COAST_BUILDINGS_HOUSES')+('_MARE_LOT' if reserved else '')+'_'+str(len(clones)));clones[key]=c
 for child in source.children:
  if not inland:c.children.link(child)
 for o in source.objects:
  name=o.name
  if any(t in name for t in remove_tags):
   if 'Pool_' in name or 'Pond' in name:stats['removed_pool_objects']+=1
   continue
  original=name.replace('MARE_LOT_CLEARED_','').replace('GROUNDED_','').replace('CLEAR_ROAD_','')
  if original.startswith(build_prefixes if inland else rear_prefixes):stats['removed_legacy_building_objects']+=1;continue
  if original.startswith('Sign_') and (inland or any(t in name for t in ['JARDIM','LOCAL','AMARELA','SUITES','SPA','VILLA','PRACA'])):continue
  if any(t in name for t in ['Trees_','Palms_','Shrubs__','Planter_','Benches_']):crop_front_palms(o,c);continue
  c.objects.link(o)
 lots=slots(inland,reserved)
 b=Builder(c)
 if inland:
  for y in [20,68]:
   b.box('Neighbourhood_Road',(-34,y,.11),(118,6,.22),asphalt)
   for dy in [-4,4]:b.box('Neighbourhood_Sidewalk',(-34,y+dy,.40),(118,2,.18),paving)
   for dy in [-3.1,3.1]:b.box('Neighbourhood_Curb',(-34,y+dy,.30),(118,.20,.30),stone)
   for x in range(-86,13,9):b.box('Neighbourhood_Lane_Marks',(x,y,.226),(4,.10,.012),paint)
   for j in range(7):b.box('Neighbourhood_Crosswalk',(17,y-2.4+j*.75,.229),(3,.38,.013),paint)
 else:
  rear_y=71 if reserved else 65
  b.box('Rear_Residential_Lane',(-35,rear_y,.11),(118,6,.22),asphalt)
  for dy in [-4,4]:b.box('Rear_Residential_Sidewalk',(-35,rear_y+dy,.40),(118,2,.18),paving)
  for dy in [-3.1,3.1]:b.box('Rear_Residential_Curb',(-35,rear_y+dy,.3),(118,.20,.30),stone)
  for x in range(-86,13,9):b.box('Rear_Residential_Road_Marks',(x,rear_y,.226),(4,.10,.012),paint)
 for i,(x,y,north) in enumerate(lots):
  # Domestic streets alternate with varied local shop frontages.
  isshop=(i%3==0 or (inland and i%7==0));variant=(8+(i+len(clones)*3)%12) if isshop else (i+len(clones))%8
  ob=bpy.data.objects.new('V7_LOT_%02d_%s'%(i,shopnames[variant-8] if isshop else 'CASA'),None);c.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=templates[variant];ob.location=(x,y,0);ob.rotation_euler.z=math.pi if north else 0
  ob['usage']='commerce_home' if isshop else 'residential';ob['floors']=templates[variant]['floors'];ob['plot_bounds']=[x-8.1,y-9.2,x+8.1,y+9.2]
  b.box('Garden_Lot_Grass',(x,y,.27),(18.8,19,.16),grass)
  lot_records.append({'district':c.name,'name':ob.name,'position':[x,y],'shop':isshop,'floors':ob['floors']})
  tree_source=bpy.data.collections.get('RIO_FOREST_TREE_SOURCE')
  if tree_source and i%2==0:
   t=bpy.data.objects.new('V7_GARDEN_TREE_%02d'%i,None);c.objects.link(t);t.instance_type='COLLECTION';t.instance_collection=tree_source;t.location=(x-9.65,y+1.3,.38);t.scale=(.28,.28,.28)
 b.finish();c['lots']=len(lots);c['shops']=sum(o.get('usage')=='commerce_home' for o in c.objects);c['no_city_pools']=True
 print('DISTRICT_READY',c.name,'lots',len(lots),'shops',c['shops'],flush=True)
 return c

replacement_names=[]
for ob in list(city.objects):
 if not ob.instance_collection:continue
 inland=ob.name.startswith('COMPACT_CITY_SECTOR_');coast=ob.name.startswith('COMPACT_COAST_SECTOR_') or ob.name=='COAST_SECTOR_03_WITH_MARE_LOT'
 if not (inland or coast):continue
 reserved=ob.name=='COAST_SECTOR_03_WITH_MARE_LOT';new=make_district(ob.instance_collection,inland,reserved)
 cp=ob.copy();cp.name='V7_'+ob.name;cp.instance_collection=new;city.objects.unlink(ob);city.objects.link(cp)
 stats['inland_sectors' if inland else 'coastal_sectors']+=1;stats['houses']+=new['lots'];stats['shops']+=new['shops'];replacement_names.append(cp.name)

# The shared city collection is used by all 20 integrated resort stages.
for i in range(1,21):
 scene=bpy.data.scenes['RESORT_MAIN_MARE_%02d'%i];scene['city_revision']=7;scene['city_layout']='High-rise waterfront; inland houses and local commerce; scattered city pools removed';scene['map_size_m']='2000 x 1000'
final=bpy.data.scenes['RESORT_MAIN_MARE_20'];bpy.context.window.scene=final
def camera(name,position,target,lens):
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);final.collection.objects.link(ob);ob.location=position;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_end=10000;return ob
cameras=[camera('V7_CITY_AERIAL',(-550,-810,420),(-100,60,0),43),camera('V7_NEIGHBOURHOOD_WALK',(-180,-72,1.75),(-155,-45,2.3),30),camera('V7_BEHIND_WATERFRONT',(-330,-172,42),(-260,-230,4),38)]
final.camera=cameras[0];final.render.engine='CYCLES';final.cycles.samples=24;final.cycles.use_denoising=True;final.render.resolution_x=1600;final.render.resolution_y=900;final.render.resolution_percentage=100;final.render.image_settings.file_format='PNG';final.view_settings.view_transform='AgX'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 final.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
except Exception:final.cycles.device='CPU'
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'file':str(OUT),'map_m':[2000,1000],'all_20_stages_updated':True,'resort_preserved':True,'front_row_building_scale_preserved':True,'city_pools_removed':True,'resort_pools_preserved':True,'stats':stats,'shop_categories':shopnames,'districts':[{'name':c.name,'lots':c['lots'],'shops':c['shops']} for c in clones.values()],'lots':lot_records}
(ROOT/'city_houses_v7_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('MAP_REVISION_SAVED',json.dumps(stats),flush=True)
captures=ROOT/'BlenderCaptures_Houses_v7';captures.mkdir(exist_ok=True)
for cam,name in zip(cameras,['aerial','neighbourhood','waterfront_rear']):
 final.camera=cam;final.render.filepath=str(captures/('blender_'+name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)
final.camera=cameras[0];bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
print('REVISION_COMPLETE',str(OUT),flush=True)
