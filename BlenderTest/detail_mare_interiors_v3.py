import bpy,math,json
from mathutils import Vector
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];steel=bpy.data.materials['MARE_Brushed_Stainless'];ceramic=bpy.data.materials['INTERIOR_Glazed_Ivory_Ceramic'];teal=bpy.data.materials['MARE_Painted_Teal'];dark=bpy.data.materials['MARE_Charcoal'];linen=bpy.data.materials['MARE_Linen_Canvas'];coral=bpy.data.materials['INTERIOR_Coral_Upholstery'];brass=bpy.data.materials['MARE_Brushed_Brass']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat);o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;m=o.modifiers.new('Edge finish','BEVEL');m.width=.015;m.segments=2;return o
def ring(name,loc,radius,height,mat,c):
    vs=[];fs=[];n=28
    for r,z in [(radius,0),(radius,height),(radius-.02,height),(radius-.02,.025)]:
        for j in range(n):a=j*math.tau/n;vs.append((r*math.cos(a),r*math.sin(a),z))
    for k in range(3):
        for j in range(n):a=k*n+j;b=k*n+(j+1)%n;fs.append((a,b,b+n,a+n))
    fs.append(tuple(range(3*n,4*n)));me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat)
    for p in me.polygons:p.use_smooth=len(p.vertices)==4
    o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;return o
for cname,x,y in [('INTERIOR_04_RESTAURANT_INTERIOR',6.1,-2),('INTERIOR_06_REAR_RESTAURANT_INTERIOR',6.1,21),('INTERIOR_09_OPERATIONS',-5,30.5)]:
    c=bpy.data.collections[cname]
    for dx,dy in [(-2-.45,-1.8-.23),(-2+.45,-1.8+.23)]:
        ring('Cooking_Pot',(x+dx,y+dy,1.55),.17,.20,steel,c)
        box('Pot_Handle',(x+dx+.22,y+dy,1.71),(.20,.05,.05),dark,c)
    box('Cutting_Board',(x-2,y+1.6,1.465),(.8,.45,.035),wood,c)
    for j in range(5):ring('Produce',(x-2.25+j*.12,y+1.55,1.49),.045,.055,coral,c)
    box('Prep_Knife',(x-1.6,y+1.6,1.49),(.03,.27,.01),steel,c)
    for j in range(10):box('Hood_Grease_Filter',(x-2-.75+j*.16,y-1.8,2.37),(.10,.75,.025),dark,c)
    for dx in [-.4,.4]:
        box('Service_Tray',(x+dx,y-2.8,1.48),(.65,.40,.025),steel,c)
        ring('Plated_Bowl',(x+dx,y-2.8,1.50),.13,.055,ceramic,c)
    box('Kitchen_Order_Rail',(x,y-2.8,2.1),(2.3,.035,.035),steel,c)
    for dx in [-.7,-.2,.3,.8]:box('Order_Ticket',(x+dx,y-2.81,2.0),(.17,.018,.22),linen,c)
    for o in list(c.objects):
        if 'Prep_Worktop' in o.name and abs(o.location.x-x)<.01:bpy.data.objects.remove(o,do_unlink=True)
    for dx,w in [(-.63,.6),(.63,.6)]:box('Sink_Worktop_Side',(x+dx,y+1.6,1.43),(w,.84,.055),steel,c)
    for dy in [-.31,.31]:box('Sink_Worktop_Rim',(x,y+1.6+dy,1.43),(.70,.19,.055),steel,c)
    box('Dish_Basin_Bottom',(x,y+1.6,1.39),(.65,.42,.025),steel,c)
    box('Dish_Faucet_Stem',(x,y+1.96,1.66),(.045,.045,.44),steel,c);box('Dish_Faucet_Spout',(x,y+1.80,1.88),(.045,.35,.045),steel,c)
# Management is present from the first hotel, tucked to the right of the rear spine.
c=bpy.data.collections.new('INTERIOR_06_ADMINISTRATION');c['unlock_stage']=6
for i in range(6,21):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(c)
box('Manager_Desk',(3,0,1.30),(2.5,.85,.10),wood,c)
for x in [1.9,4.1]:box('Desk_Pedestal',(x,0,.93),(.42,.75,.68),wood,c)
box('Management_Monitor',(3,.14,1.62),(.58,.06,.36),dark,c)
box('Management_Keyboard',(3,-.12,1.37),(.45,.16,.025),dark,c)
chair=bpy.data.objects.new('INT_Manager_Chair',None);c.objects.link(chair);chair.instance_type='COLLECTION';chair.instance_collection=bpy.data.collections['INTERIOR_ASSET_DINING_CHAIR'];chair.location=(3,.85,.55);chair.rotation_euler.z=math.pi
for x in [4.9,5.9]:
    box('Records_Cabinet',(x,1.8,1.40),(.85,.52,1.7),wood,c)
    for z in [1.05,1.5,1.95]:box('Cabinet_Handle',(x,1.52,z),(.25,.035,.025),brass,c)
o=bpy.data.objects.new('GAME_Management_Desk',None);c.objects.link(o);o.location=(3,-1,.6);o['interaction_type']='manage_staff_and_finances';o['runtime_implemented']=False
# Staff break and lockers share the service wing with stores, clear of the center passage.
c=bpy.data.collections['INTERIOR_09_OPERATIONS']
box('Staff_Table',(6,28,1.31),(3,1.3,.10),wood,c)
for x in [4.7,7.3]:box('Staff_Table_Leg',(x,28,.94),(.10,1.1,.7),wood,c)
for x in [5,7]:
    for y,a in [(26.9,0),(29.1,math.pi)]:
        o=bpy.data.objects.new('INT_Staff_Chair',None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=bpy.data.collections['INTERIOR_ASSET_DINING_CHAIR'];o.location=(x,y,.55);o.rotation_euler.z=a
for j in range(5):
    x=3+j*1.5;box('Staff_Locker',(x,35.25,1.55),(1.15,.5,2),teal,c)
    for k in range(5):box('Locker_Vent',(x,34.98,2.05+k*.04),(.5,.015,.015),dark,c)
    box('Locker_Handle',(x+.35,34.98,1.45),(.04,.035,.18),steel,c)
# Better diagnostic angle includes preparation, cooking and pass stations in one view.
cam=bpy.data.objects['INTERIOR_CAMERA_KITCHEN'];cam.location=(6.5,18.5,2.3);cam.rotation_euler=(Vector((4.5,21.1,1.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];report=json.loads(bpy.context.scene['interior_manifest_json']);report['room_count']=59;report['extra_facilities']=['management office','staff break','staff lockers','cooking/preparation/pass/dishwashing']
bpy.context.scene['interior_manifest_json']=json.dumps(report,ensure_ascii=False);bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3_1.blend')
print('DETAIL_AND_STAFF_FACILITIES_SAVED')
