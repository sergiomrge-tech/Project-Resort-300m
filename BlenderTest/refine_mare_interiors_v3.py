import bpy,math,json
from mathutils import Vector
# Keep saved v2 intact; refine only the live v3 assembly.
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
report=json.loads(bpy.context.scene['interior_manifest_json'])
removed=[]
# A cross corridor through each guest wing connects core, stairs and outer hallway.
for c in bpy.data.collections:
    if not c.name.startswith('INTERIOR_') or not c.get('unlock_stage'):continue
    for o in list(c.objects):
        if o.get('room_id') and abs(o.location.y+9)<.01:
            removed.append(o['room_id']);bpy.data.objects.remove(o,do_unlink=True)
# Keep a center-to-rear spine instead of placing two rooms across it.
for cname in ['INTERIOR_06_QUARTOS_HOTEL','INTERIOR_19_QUARTOS_CENTRO']:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if o.get('room_id') and abs(o.location.y+3)<.01:
            removed.append(o['room_id']);bpy.data.objects.remove(o,do_unlink=True)
report['rooms']=[r for r in report['rooms'] if r['id'] not in removed]
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];glass=bpy.data.materials['MARE_Architectural_Glass'];plaster=bpy.data.materials['URBAN_PBR_IP_Ivory_Painted_Render'];steel=bpy.data.materials['MARE_Brushed_Stainless'];linen=bpy.data.materials['MARE_Linen_Canvas'];teal=bpy.data.materials['MARE_Painted_Teal'];brass=bpy.data.materials['MARE_Brushed_Brass']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat);o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;return o
def sign(c,body,loc):
    d=bpy.data.curves.new(body,'FONT');d.body=body;d.align_x='CENTER';d.size=.17;o=bpy.data.objects.new('INT_Wayfinding',d);c.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);d.materials.append(brass)
# Every shared glass seam receives an actual opening, with side panels and lintel.
def open_side(c,x,y,gap):
    for o in list(c.objects):
        if 'Side_Glass' not in o.name or abs(o.location.x-x)>.1:continue
        z=o.location.z;lo=o.location.y-o.dimensions.y/2;hi=o.location.y+o.dimensions.y/2
        if not lo<y<hi:continue
        for a,b in [(lo,y-gap/2),(y+gap/2,hi)]:
            if b>a:box('Connected_Glass_Side',(x,(a+b)/2,z),(.06,b-a,o.dimensions.z),glass,c)
        box('Connected_Lintel',(x,y,z+1.22),(.12,gap,.25),wood,c)
        bpy.data.objects.remove(o,do_unlink=True)
def open_front(c,y,x,gap):
    for o in list(c.objects):
        if 'Facade_Glass' not in o.name or abs(o.location.y-y)>.12 or abs(o.location.x-x)>gap/2+.3:continue
        bpy.data.objects.remove(o,do_unlink=True)
    for o in list(c.objects):
        if 'Mullion' in o.name and abs(o.location.y-y)<.14 and abs(o.location.x-x)<gap/2-.15:bpy.data.objects.remove(o,do_unlink=True)
for cname in ['UNIDA_06_HOTEL_SIMPLES','UNIDA_19_AMPLIACAO_VERTICAL']:
    c=bpy.data.collections[cname]
    for x in [-12,12]:open_side(c,x,-9,3.6)
    open_front(c,3,0,4)
for cname,x in [('UNIDA_07_ALA_ESQUERDA',-12),('UNIDA_08_ALA_DIREITA',12),('UNIDA_19_AMPLIACAO_VERTICAL',-12),('UNIDA_20_RESORT_UNICO',12)]:open_side(bpy.data.collections[cname],x,-9,3.6)
for cname,y,x in [('UNIDA_08_ALA_DIREITA',15,21),('UNIDA_12_FAMILIA',15,21),('UNIDA_13_FITNESS_PISO_SUPERIOR',15,21),('UNIDA_06_RESTAURANTE_NOS_FUNDOS',25,0),('UNIDA_09_COZINHA_E_OPERACAO',25,0),('UNIDA_09_COZINHA_E_OPERACAO',36,0),('UNIDA_17_EVENTOS_INTEGRADOS',36,0),('UNIDA_15_GASTRONOMIA_PISO_SUPERIOR',5,0)]:open_front(bpy.data.collections[cname],y,x,4)
for cname,x,y in [('UNIDA_12_FAMILIA',30,24),('UNIDA_14_SPA_ANEXADO',30,24),('UNIDA_17_EVENTOS_INTEGRADOS',-12,46),('UNIDA_18_LAVANDERIA_E_RECURSOS',-12,46)]:open_side(bpy.data.collections[cname],x,y,3.6)
# Room numbers are visible by the doors; instance IDs are preserved for game mapping.
for row in report['rooms']:
    c=bpy.data.collections[row['collection']];x,y,z=row['position'];a=row['rotation'];px=x-2.45*math.cos(a)-3.53*math.sin(a);py=y-2.45*math.sin(a)+3.53*math.cos(a)
    d=bpy.data.curves.new('Room number','FONT');d.body='%03d'%(report['rooms'].index(row)+101);d.size=.13;o=bpy.data.objects.new('INT_Room_Number',d);c.objects.link(o);o.location=(px,py,z+1.72);o.rotation_euler=(math.pi/2,0,a+math.pi);d.materials.append(brass)
# Room entry cameras stay inside the threshold, below real ceilings.
cam=bpy.data.objects['INTERIOR_CAMERA_ROOM'];cam.location=(-4.35,-12.85,5.20);cam.rotation_euler=(Vector((-3.35,-17.1,4.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
# Metadata only: activity anchors do not yet perform gameplay.
report['circulation_revision']='open cross-wing corridor at y=-9, central core rear spine, glazed seams opened'
report['room_count']=len(report['rooms']);bpy.context.scene['interior_manifest_json']=json.dumps(report,ensure_ascii=False)
for c in bpy.data.collections:
    if c.name.startswith('INTERIOR_') and c.get('unlock_stage'):
        for o in c.objects:o['unlock_stage']=c['unlock_stage'];o['interior_revision']=3
bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3.blend')
print('INTERIOR_CONNECTED_ROOMS '+str(len(report['rooms'])))
