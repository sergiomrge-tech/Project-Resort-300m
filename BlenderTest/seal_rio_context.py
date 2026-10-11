import bpy
s=bpy.context.scene;c=bpy.data.collections['RIO_MOUNTAINS_AND_FOREST']
def plane(name,x0,x1,y0,y1,z,m):
    me=bpy.data.meshes.new(name);me.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)]);me.materials.append(m);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);return o
water=bpy.data.materials.new('RIO_Atlantic_Water_Backdrop');water.use_nodes=True
nt=water.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.012,.095,.145,1);p.inputs['Roughness'].default_value=.24;p.inputs['Metallic'].default_value=.12;p.inputs['IOR'].default_value=1.333
geo=nt.nodes.new('ShaderNodeNewGeometry');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.04;nt.links.new(geo.outputs['Position'],scale.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=3;nt.links.new(scale.outputs[0],noise.inputs['Vector']);b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.25;b.inputs['Distance'].default_value=.08;nt.links.new(noise.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
plane('ATLANTIC_OCEAN_CONTEXT',-15000,15000,-15000,12000,-.30,water)
plane('MAINLAND_CONTEXT_GROUND',-4400,3600,-360,5500,-.20,bpy.data.materials['RIO_Granite_Atlantic_Forest'])
for co in bpy.data.collections:
    if not co.name.endswith('CONNECTED_ROADS_GROUNDED'):continue
    for o in co.objects:
        if o.type!='MESH' or not o.name.startswith('NATURAL_GROUNDED_Park_Foliage'):continue
        me=o.data
        for start in range(0,len(me.vertices),15):
            base=me.vertices[start+1].co.copy()
            for row in range(5):
                mid=me.vertices[start+row*3+1].co.copy();new=base+(mid-base)*1.65
                for k in range(3):
                    v=me.vertices[start+row*3+k];v.co=new+(v.co-mid)*2.4
        me.update()
s.camera=bpy.data.objects['RIO_CITY_MOUNTAINS'];s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/rio_city_mountains_final.png'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Cristo_Montanhas_Vegetacao_v2.blend');bpy.ops.render.render(write_still=True)
print('SEA_AND_TERRAIN_CONTEXT_RENDERED')
