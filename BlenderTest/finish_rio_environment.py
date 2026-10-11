import bpy,math,random
from mathutils import Vector,noise
from mathutils.bvhtree import BVHTree
random.seed(842)
s=bpy.context.scene;land=bpy.data.collections['RIO_MOUNTAINS_AND_FOREST']
for c in bpy.data.collections:
    if not (c.name.endswith('CONNECTED_ROADS_GROUNDED') or c.name=='RIO_FOREST_TREE_SOURCE'):continue
    for o in c.objects:
        if o.type!='MESH' or not any(t in o.name for t in ['NATURAL_GROUNDED_Trees_Foliage','NATURAL_Park_Foliage','NATURAL_GROUNDED_Palms_Leaflets','RIO_Forest_Leaf_Crown']):continue
        me=o.data
        for start in range(0,len(me.vertices),15):
            if start+14>=len(me.vertices):continue
            base=me.vertices[start+1].co.copy();lf=1.15 if 'Palms' in o.name else 1.65
            for row in range(5):
                mid=me.vertices[start+row*3+1].co.copy();midnew=base+(mid-base)*lf
                for k in range(3):
                    v=me.vertices[start+row*3+k];v.co=midnew+(v.co-mid)*2.4
        me.update()
for o in land.objects:
    if o.type!='MESH' or o.name not in ['CORCOVADO_TERRAIN','PEDRA_DA_GAVEA_TERRAIN']:continue
    cor=o.name.startswith('CORCOVADO');cx,cy,rx,ry,h=(-350,1650,650,720,704) if cor else (-2000,950,680,620,842)
    for v in o.data.vertices:
        x,y,z=v.co;dx=(x-cx)/rx;dy=(y-cy)/ry;rho=math.sqrt(dx*dx+dy*dy)
        if rho>=.995:v.co.z=-.15;continue
        if cor:
            dy=dy/(.8 if dy<0 else 1.03);q=abs(dx)**2.3+abs(dy)**2;z=h*max(0,1-q)**(.43 if dy<0 else .94)
            if math.hypot(x-cx,y-cy)<45:z=h
        else:
            z=h*(.72*math.exp(-(rho/.57)**7)+.28*math.exp(-(rho/.83)**2))
            if rho<.15:z=h
        if rho>.07:z+=noise.noise_vector(Vector((x*.025,y*.025,2))).z*12
        v.co.z=z
    o.data.update()
m=bpy.data.materials['RIO_Granite_Atlantic_Forest'];nt=m.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');geo=next(n for n in nt.nodes if n.type=='NEW_GEOMETRY')
waves=nt.nodes.new('ShaderNodeTexNoise');waves.inputs['Scale'].default_value=1;waves.inputs['Detail'].default_value=5;waves.inputs['Roughness'].default_value=.8
mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.09,.07,.015);nt.links.new(geo.outputs['Position'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],waves.inputs['Vector'])
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.5;b.inputs['Distance'].default_value=1.8;nt.links.new(waves.outputs['Fac'],b.inputs['Height']);old=next(n for n in nt.nodes if n.type=='BUMP' and n!=b);nt.links.new(old.outputs[0],b.inputs['Normal']);nt.links.new(b.outputs[0],p.inputs['Normal'])
bvhs=[]
for o in land.objects:
    if o.type=='MESH' and o.name.endswith('_TERRAIN'):bvhs.append(BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
def hit(x,y):
    best=None
    for tree in bvhs:
        p,n,idx,d=tree.ray_cast(Vector((x,y,1300)),Vector((0,0,-1)),1400)
        if p is not None and (best is None or p.z>best[0].z):best=(p,n)
    return best
forest=bpy.data.collections['RIO_FOREST_TREE_SOURCE']
for o in list(land.objects):
    if o.instance_collection==forest:
        surface=hit(o.location.x,o.location.y)
        if surface is not None:o.location.z=surface[0].z-.08
added=0
for i in range(11500):
    x=random.uniform(-2640,1560);y=random.uniform(525,2450)
    if math.hypot(x+350,y-1650)<60:continue
    surface=hit(x,y)
    if surface is None:continue
    p,n=surface
    if p.z<8 or n.z<.57:continue
    ob=bpy.data.objects.new('Atlantic_Forest_Dense_'+str(added),None);land.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=forest;ob.location=(x,y,p.z-.08);scale=random.uniform(1.3,2.1);ob.scale=(scale,scale,scale);ob.rotation_euler.z=random.random()*math.tau;added+=1
s['rio_added_dense_forest_trees']=added
bpy.context.view_layer.update();s.camera=bpy.data.objects['RIO_CITY_MOUNTAINS'];s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/rio_city_mountains_final.png'
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Cristo_Montanhas_Vegetacao_v2.blend')
bpy.ops.render.render(write_still=True)
print('ENVIRONMENT_FINISHED_DENSE_TREES',added)
