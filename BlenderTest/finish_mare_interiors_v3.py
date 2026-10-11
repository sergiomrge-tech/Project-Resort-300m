import bpy,math,json
from mathutils import Vector
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];linen=bpy.data.materials['MARE_Linen_Canvas'];steel=bpy.data.materials['MARE_Brushed_Stainless'];ceramic=bpy.data.materials['INTERIOR_Glazed_Ivory_Ceramic'];plaster=bpy.data.materials['URBAN_PBR_IP_Ivory_Painted_Render'];glass=bpy.data.materials['MARE_Architectural_Glass'];lamp=bpy.data.materials['INTERIOR_Warm_Lamp_Diffuser']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat);o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;return o
for cname,token in [('UNIDA_12_FAMILIA','Kids_Interior'),('UNIDA_13_FITNESS_PISO_SUPERIOR','Fitness_Interior'),('UNIDA_14_SPA_ANEXADO','Spa_Interior'),('UNIDA_15_GASTRONOMIA_PISO_SUPERIOR','Dining_Interior'),('UNIDA_17_EVENTOS_INTEGRADOS','Event_Interior'),('UNIDA_18_LAVANDERIA_E_RECURSOS','Laundry_Interior'),('UNIDA_05_SANITARIOS_INTEGRADOS','Hotel_Bathrooms'),('UNIDA_03_PREPARO_RESTAURANTE','Restaurant_Kitchen'),('UNIDA_09_COZINHA_E_OPERACAO','Service_Cabinet')]:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if token in o.name:bpy.data.objects.remove(o,do_unlink=True)
# Privacy enclosure around the hotel's public WC block, with a side entrance.
c=bpy.data.collections['INTERIOR_06_PUBLIC_WASHROOMS']
box('WC_Rear_Wall',(-7.5,-3.05,1.95),(5.6,.12,2.8),plaster,c)
for y,length in [(-6.8,1.4),(-3.95,1.8)]:box('WC_End_Wall',(-4.7,y,1.95),(.12,length,2.8),plaster,c)
box('WC_Entry_Lintel',(-4.7,-5.475,3.08),(.14,1.25,.5),wood,c)
# Lobby ceiling includes visible light fittings rather than invisible area lights alone.
c=bpy.data.collections['INTERIOR_06_LOBBY'];box('Lobby_Suspended_Ceiling',(0,-15,3.40),(23.4,11.8,.035),linen,c)
for x in [-9,-3,3,9]:
    box('Lobby_Diffuser',(x,-16,3.355),(.65,.65,.05),lamp,c)
    box('Lobby_Air_Return',(x,-11,3.36),(1.1,.25,.025),steel,c)
# Clear privacy vestibule width and add shower pipe support.
c=bpy.data.collections['INTERIOR_ASSET_ENSUITE_ROOM']
for o in c.objects:
    if 'Corridor_Wall' in o.name and o.location.x>0:o.location.x=.975;o.scale.x=3.95/4.2
box('Shower_Riser',(1.15,2.70,1.42),(.035,.035,1.65),steel,c)
box('Shower_Mixer',(1.15,2.64,1.08),(.18,.08,.08),steel,c)
box('Bath_Ceiling_Diffuser',(1.7,1.8,2.88),(.4,.4,.04),lamp,c)
d=bpy.data.lights.new('Bathroom tasklight','AREA');d.energy=35;d.color=(1,.86,.7);d.size=.5;o=bpy.data.objects.new('INT_Bath_Tasklight',d);c.objects.link(o);o.location=(1.7,1.8,2.83)
# Bowl and seat annuli: hollow center instead of the original capped cylinder.
for c in bpy.data.collections:
    if not c.name.startswith('INTERIOR_'):continue
    for o in list(c.objects):
        if 'WC_Bowl' not in o.name and 'WC_Seat' not in o.name:continue
        verts=[];faces=[];n=32;is_seat='WC_Seat' in o.name;r=.245 if is_seat else .24;depth=.045 if is_seat else .14;inner=.17 if is_seat else .16
        for rad,z in [(r,-depth/2),(r,depth/2),(inner,depth/2),(inner,-depth/2+.025)]:
            for j in range(n):a=j*math.tau/n;verts.append((rad*math.cos(a),rad*1.26*math.sin(a),z))
        for k in range(3):
            for j in range(n):a=k*n+j;b=k*n+(j+1)%n;faces.append((a,b,b+n,a+n))
        me=bpy.data.meshes.new('WC hollow bowl');me.from_pydata(verts,[],faces);me.update();me.materials.append(ceramic)
        for p in me.polygons:p.use_smooth=True
        o.data=me;o.scale=(1,1,1)
# Activity planning is metadata, never declared operational gameplay.
report=json.loads(bpy.context.scene['interior_manifest_json']);report['revision']=3;report['interior_scope']='all unlocked indoor modules furnished; gameplay anchors only';report['runtime_implemented']=False
bpy.context.scene['interior_manifest_json']=json.dumps(report,ensure_ascii=False)
for i in range(1,21):
    s=bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i];s['interior_revision']=3;s.cycles.max_bounces=8;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=6;s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False
bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3.blend')
print('INTERIOR_FIXTURE_FINISH_SAVED')
