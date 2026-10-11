import bpy
c=bpy.data.collections['INTERIOR_14_SPA_INTERIOR'];steel=bpy.data.materials['MARE_Brushed_Stainless']
def box(name,loc,size):
    x,y,z=[v/2 for v in size];me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(steel);o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc
for x in [34,42]:
    for y in [17.85,18.35]:box('INT_Tray_Table_Leg',(x+.75,y,.855),(.035,.035,.56))
    for xx in [x-2.6,x+2.6]:box('INT_Spa_Lantern_Suspension',(xx,20,2.99),(.035,.035,.9))
for o in c.objects:
    if 'Spa_Wall_Sconce' in o.name:o.name=o.name.replace('Wall_Sconce','Pendant_Lantern')
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Interiores_v3_1.blend')
