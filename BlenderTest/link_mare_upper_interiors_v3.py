import bpy
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];glass=bpy.data.materials['MARE_Architectural_Glass'];floor=bpy.data.materials['INTERIOR_Travertine_Honed'];steel=bpy.data.materials['MARE_Brushed_Stainless']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat);o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;return o
guard=bpy.data.collections.new('INTERIOR_06_REAR_GUARD');guard['unlock_stage']=6;guard['last_stage']=14
for i in range(6,15):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(guard)
box('Early_Upper_Rear_Guard',(0,3,4.26),(4,.025,1.05),glass,guard);box('Early_Upper_Rear_Rail',(0,3,4.80),(4,.055,.055),steel,guard)
bridge=bpy.data.collections['INTERIOR_15_FINE_DINING_INTERIOR']
box('Upper_Restaurant_Connector',(0,4,3.69),(4.2,2.1,.08),floor,bridge)
box('Upper_Connector_Roof',(0,4,6.78),(4.3,2.15,.12),wood,bridge)
for x in [-2.08,2.08]:box('Upper_Connector_Glass',(x,4,5.15),(.025,2.1,2.8),glass,bridge)
roof=bpy.data.collections['INTERIOR_19_QUARTOS_CENTRO']
box('Premium_To_Rear_Roof_Deck',(0,4,6.91),(4.2,2.1,.12),wood,roof)
for x in [-2.08,2.08]:box('Premium_Connector_Rail',(x,4,7.51),(.04,2.1,1.1),glass,roof)
for cname in ['UNIDA_13_FITNESS_PISO_SUPERIOR','UNIDA_16_SUITES_PRIVATIVAS']:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if 'Side_Glass' not in o.name or abs(o.location.x-30)>.1:continue
        lo=o.location.y-o.dimensions.y/2;hi=o.location.y+o.dimensions.y/2;z=o.location.z
        for a,b in [(lo,22.2),(25.8,hi)]:
            if b>a:box('Fitness_Suites_Connection',(30,(a+b)/2,z),(.06,b-a,o.dimensions.z),glass,c)
        box('Fitness_Suites_Lintel',(30,24,z+1.22),(.12,3.6,.25),wood,c);bpy.data.objects.remove(o,do_unlink=True)
for c in [guard,bridge,roof]:
    for o in c.objects:o['unlock_stage']=c['unlock_stage'];o['interior_revision']=3
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3_1.blend')
print('UPPER_FLOOR_CONNECTIONS_SAVED')
