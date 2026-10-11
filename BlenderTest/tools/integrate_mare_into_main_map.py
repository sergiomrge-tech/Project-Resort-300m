import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
city=bpy.data.scenes['RESORT_2x1KM_COMERCIO'];bpy.context.window.scene=city
source=bpy.data.collections['MAP_2000x1000_COMERCIO']
integrated=bpy.data.collections.new('MAIN_CITY_WITH_MARE_LOT')
for c in source.children:integrated.children.link(c)
for o in source.objects:integrated.objects.link(o)
sector=next(o for o in integrated.objects if o.name=='COMPACT_COAST_SECTOR_03')
coast=bpy.data.collections.new('COAST_SECTOR_03_RESERVED_MARE')
plot=(-95,16,-29,64)
stats={'removed_objects':0,'removed_components':0,'removed_faces':0}
def inplot(x,y):return plot[0]<x<plot[1] and plot[2]<y<plot[3]
def protected(o):return any(t in o.name for t in ['Site_','Ground','Forecourt','Promenade','Urban_Sidewalk','Coastal_Avenue','Cycleway','Street','Curb','Avenue','LaneMark','Beach','Sea','Paving','Sidewalk'])
for o in sector.instance_collection.all_objects:
    if o.hide_render:continue
    if protected(o):coast.objects.link(o);continue
    if o.type not in ['MESH','FONT']:
        if inplot(o.matrix_world.translation.x,o.matrix_world.translation.y):stats['removed_objects']+=1;continue
        coast.objects.link(o);continue
    if o.type=='FONT':
        p=o.matrix_world.translation
        if inplot(p.x,p.y):stats['removed_objects']+=1;continue
        coast.objects.link(o);continue
    # Remove connected components wholly belonging to the reserved lot, keeping the other shops intact.
    bm=bmesh.new();bm.from_mesh(o.data);seen=set();delete=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];component=[];seen.add(v)
        while stack:
            a=stack.pop();component.append(a)
            for e in a.link_edges:
                q=e.other_vert(a)
                if q not in seen:seen.add(q);stack.append(q)
        points=[o.matrix_world @ v.co for v in component]
        x=sum(v.x for v in points)/len(points);y=sum(v.y for v in points)/len(points);top=max(v.z for v in points)
        if inplot(x,y) and top>.5:delete.extend(component);stats['removed_components']+=1
    if not delete:coast.objects.link(o);bm.free();continue
    before=len(bm.faces);bmesh.ops.delete(bm,geom=delete,context='VERTS');stats['removed_faces']+=before-len(bm.faces)
    if not bm.faces:stats['removed_objects']+=1;bm.free();continue
    cp=o.copy();cp.data=o.data.copy();cp.name='MARE_LOT_CLEARED_'+o.name;bm.to_mesh(cp.data);bm.free();coast.objects.link(cp)
cp=sector.copy();cp.name='COAST_SECTOR_03_WITH_MARE_LOT';cp.instance_collection=coast;integrated.objects.unlink(sector);integrated.objects.link(cp)
offset=Matrix.Translation(Vector((-340,-295,0)))
# Fit only the arrival ramps to the existing sidewalk; no resort building is scaled.
for c in bpy.data.collections:
    if not c.name.startswith('UNIDA_'):continue
    for o in c.objects:
        if o.type=='MESH' and any(t in o.name for t in ['Entrance_Ramp','Arrival_Forecourt']):
            cpdata=o.data.copy();o.data=cpdata
            for v in cpdata.vertices:
                if v.co.y<-31:v.co.y=-31
            cpdata.update()
stage_data=[]
for i in range(1,21):
    s=bpy.data.scenes.new('RESORT_MAIN_MARE_%02d'%i);s.world=city.world;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.collection.children.link(integrated)
    art=bpy.data.collections.new('MAIN_MARE_STAGE_%02d'%i)
    for c in bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children:
        if c.name!='UNIDA_ORLA_CONTINUA':art.children.link(c)
    inst=bpy.data.objects.new('MARE_CONNECTED_BUSINESS_STAGE_%02d'%i,None);inst.instance_type='COLLECTION';inst.instance_collection=art;inst.matrix_world=offset;s.collection.objects.link(inst)
    s['map_size_m']='2000 x 1000';s['resort_stage']=i;s['resort_offset_blender']=list(offset.translation);s['source_city_preserved']=True;s['runtime_integrated']=False
    s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';stage_data.append({'stage':i,'scene':s.name})
final=bpy.data.scenes['RESORT_MAIN_MARE_20'];bpy.context.window.scene=final
for name,loc,target,lens in [('INTEGRATED_CITY_AERIAL',(-560,-650,340),(-330,-275,5),42),('INTEGRATED_RESORT_WALK',(-343,-357,1.75),(-340,-311,5),27)]:
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);final.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=10000
final.camera=bpy.data.objects['INTEGRATED_CITY_AERIAL'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Resort_Main_Map_Mare_Integrated_v4.blend'))
report={'file':bpy.data.filepath,'map_m':[2000,1000],'sectors':40,'replacement_sector':'03','reserved_local_plot':list(plot),'resort_translation':[-340,-295,0],'building_scale':[1,1,1],'stats':stats,'stages':stage_data,'city_source_scene_preserved':True,'note':'Resort assembly excludes the standalone sea/mainland/promenade to avoid overlap. Existing public waterfront retained.'}
(ROOT/'main_map_mare_integration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('MAIN_MAP_INTEGRATED '+json.dumps(report))
