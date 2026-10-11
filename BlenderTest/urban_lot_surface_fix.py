import bpy
s=bpy.context.scene
for c in bpy.data.collections:
    if not c.name.startswith('MODULE_') or 'GROUNDED' not in c.name: continue
    name='URBAN_Lot_Surface_'+c.name
    if bpy.data.objects.get(name): continue
    ymin=-28 if 'COAST' in c.name else -100
    me=bpy.data.meshes.new(name)
    me.from_pydata([(-100,ymin,.04),(100,ymin,.04),(100,100,.04),(-100,100,.04)],[],[(0,1,2,3)])
    me.update()
    uv=me.uv_layers.new(name='UrbanMeters')
    for loop in me.loops:
        p=me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(p.x,p.y)
    me.materials.append(bpy.data.materials['URBAN_PBR_Sidewalk_Stone_Pavers'])
    o=bpy.data.objects.new(name,me)
    c.objects.link(o)
    o['purpose']='Continuous lot ground above coplanar site slabs, below roads and raised sidewalks'
s['urban_lot_surface_fix']=True
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Urban_Textures_v3.blend')
