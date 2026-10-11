import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
city=bpy.data.collections['MAIN_CITY_WITH_MARE_LOT']
districts=[o.instance_collection for o in city.objects if o.name.startswith('V7_') and o.instance_collection]
unique={c.name:c for c in districts};invalid=[];pools=[];front=[]
legacy=['Casa_Coral_','Residencial_Sal_','Galeria_Mar_','Hotel_Atlantico_','Cafe_Jardim_','Mercado_Local_','Vila_Amarela_','Resort_Aurora_','Aurora_Suites_','Spa_Tropical_','Garden_Villa_','RETAIL_']
for name,c in unique.items():
 for ob in c.all_objects:
  n=ob.name.replace('MARE_LOT_CLEARED_','').replace('GROUNDED_','').replace('CLEAR_ROAD_','')
  if any(t in n.lower() for t in ['pool_','reflecting_pond','pond_coping']):pools.append([name,ob.name])
  if name.startswith('V7_HOUSES_DISTRICT') and any(n.startswith(t) for t in legacy):invalid.append([name,ob.name])
  if 'COAST_BUILDINGS' in name and ('Shell__' in n or 'UPPER_STRUCTURE' in n):front.append({'district':name,'object':ob.name,'scale':list(ob.scale),'height':ob.dimensions.z})
units=[]
for c in unique.values():
 lots=[o for o in c.objects if o.get('usage')]
 for i,a in enumerate(lots):
  for b in lots[i+1:]:
   if abs(a.location.x-b.location.x)<15.2 and abs(a.location.y-b.location.y)<12.8:invalid.append(['house_overlap',a.name,b.name])
site=bpy.data.objects['SITE_2000x1000_METERS'];scene=bpy.data.scenes['RESORT_MAIN_MARE_20']
for i in range(1,21):
 s=bpy.data.scenes['RESORT_MAIN_MARE_%02d'%i]
 if s.get('city_revision')!=7 or city.name not in s.collection.children:invalid.append(['stage_not_updated',i])
images_missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.users and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
report={'file':bpy.data.filepath,'map_dimensions_m':list(site.dimensions),'sectors':len(districts),'city_pool_objects':pools,'inland_legacy_building_objects':invalid,'front_row_buildings':front,'missing_images':images_missing,'stages':20,'runtime_verified':False}
assert not pools,pools
assert not invalid,invalid
assert not images_missing,images_missing
assert abs(site.dimensions.x-2000)<.01 and abs(site.dimensions.y-1000)<.01
(root/'city_houses_v7_audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('MAP_AUDIT',json.dumps({'sectors':len(districts),'dimensions':list(site.dimensions),'city_pools':len(pools),'invalid':len(invalid),'front_row_parts':len(front),'missing_images':len(images_missing)}),flush=True)
