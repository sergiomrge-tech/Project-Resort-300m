import bpy,math
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];linen=bpy.data.materials['MARE_Linen_Canvas'];navy=bpy.data.materials['INTERIOR_Deep_Sea_Fabric'];ceramic=bpy.data.materials['INTERIOR_Glazed_Ivory_Ceramic'];steel=bpy.data.materials['MARE_Brushed_Stainless'];lamp=bpy.data.materials['INTERIOR_Warm_Lamp_Diffuser'];floor=bpy.data.materials['INTERIOR_Travertine_Honed']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    for nameuv in ['WoodGrain','UrbanMeters']:
        uv=me.uv_layers.new(name=nameuv)
        for f in me.polygons:
            axis=max((abs(f.normal[j]),j) for j in range(3))[1];ax=[j for j in range(3) if j!=axis]
            for li in f.loop_indices:v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[ax[0]],v[ax[1]])
    o=bpy.data.objects.new('INT_'+name,me);c.objects.link(o);o.location=loc;m=o.modifiers.new('Finishing','BEVEL');m.width=.012;m.segments=2;return o
# Close side glazing-to-roof gaps in the retained shells.
for c in bpy.data.collections:
    if not c.name.startswith('UNIDA_'):continue
    for o in list(c.objects):
        if o.type!='MESH' or not o.data.materials or o.data.materials[0].name!='MARE_Architectural_Glass':continue
        if o.dimensions.x<.2 and o.dimensions.y>3 and o.dimensions.z>2.5:
            box('Window_Head_Trim',(o.location.x,o.location.y,o.location.z+o.dimensions.z/2+.065),(.14,o.dimensions.y,.15),wood,c)
spa=bpy.data.collections['INTERIOR_14_SPA_INTERIOR']
box('Spa_Timber_Floor',(40,21,.556),(19.6,23.6,.045),wood,spa)
for x in [34,42]:
    box('Spa_Quiet_Rug',(x,18,.59),(3.8,4.7,.028),navy,spa)
    box('Treatment_Storage',(x-1.9,21.3,1.25),(.85,.60,1.35),wood,spa)
    for z in [1.99,2.06,2.13]:box('Spa_Stacked_Towels',(x-1.9,21.3,z),(.68,.43,.06),linen,spa)
    box('Treatment_Tray',(x+.75,18.1,1.15),(.48,.75,.06),wood,spa)
    for y in [17.85,18.2]:box('Oil_Bottle',(x+.75,y,1.25),(.06,.06,.14),ceramic,spa)
    for xx in [x-2.6,x+2.6]:box('Spa_Wall_Sconce',(xx,20,2.5),(.10,.24,.36),lamp,spa)
    box('Treatment_Hamper',(x-1.9,16.0,.85),(.7,.7,.65),wood,spa)
    box('Hamper_Linen',(x-1.9,16.0,1.20),(.66,.66,.045),linen,spa)
for cname in ['UNIDA_13_FITNESS_PISO_SUPERIOR','UNIDA_18_LAVANDERIA_E_RECURSOS']:
    for o in bpy.data.collections[cname].objects:
        if '_Floor' in o.name and o.type=='MESH':o.data.materials[0]=floor
laundry=bpy.data.collections['INTERIOR_18_SERVICE_INTERIOR']
for x in [-31,-27]:
    box('Laundry_Cart',(x,42,.90),(1.1,.8,.60),steel,laundry)
    for dx in [-.46,.46]:
        for dy in [-.30,.30]:box('Cart_Caster',(x+dx,42+dy,.59),(.13,.10,.13),navy,laundry)
    for z in [1.23,1.31,1.39]:box('Cart_Linen',(x,42,z),(.96,.66,.075),linen,laundry)
    box('Laundry_Supply_Shelf',(x,54,1.4),(2,.5,.10),wood,laundry)
    for j in range(4):box('Detergent',(x-.6+j*.4,54,1.65),(.18,.22,.40),ceramic,laundry)
for c in [spa,laundry]:
    for o in c.objects:o['unlock_stage']=c['unlock_stage'];o['interior_revision']=3
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];bpy.context.scene.camera=bpy.data.objects['UNIDA_Camera_Unified_Resort'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3_1.blend')
print('SPA_AND_LAUNDRY_FINISH_SAVED')
