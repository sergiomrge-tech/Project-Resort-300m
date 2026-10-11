import bpy, math, random
from mathutils import Vector,noise
random.seed(910)
s=bpy.context.scene
if s.get('rio_landscape_pass'):raise RuntimeError('Landscape pass already applied')
root=bpy.data.collections['MAP_2000x1000_COMERCIO']
land=bpy.data.collections.new('RIO_MOUNTAINS_AND_FOREST');root.children.link(land)
def mat(name,color,rough=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
    return m
leaf=mat('RIO_Leaf_Waxy',(.045,.19,.025),.43)
p=next(n for n in leaf.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.065
nt=leaf.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=9;n.inputs['Detail'].default_value=3
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.018,.075,.012,1);r.color_ramp.elements[1].color=(.17,.34,.055,1);nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
leaflight=leaf.copy();leaflight.name='RIO_Leaf_Young';p2=next(n for n in leaflight.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
rr=next(n for n in leaflight.node_tree.nodes if n.type=='VALTORGB');rr.color_ramp.elements[1].color=(.22,.39,.07,1)
bark=mat('RIO_Bark_Fibrous',(.14,.095,.055),.87)
nt=bark.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=16;tex.inputs['Detail'].default_value=4
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.3;b.inputs['Distance'].default_value=.05;nt.links.new(tex.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
def mesh(c,name,v,f,m,smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.materials.append(m);me.update();ob=bpy.data.objects.new(name,me);c.objects.link(ob)
    for p in me.polygons:p.use_smooth=smooth
    return ob
def component_ids(o):
    par=list(range(len(o.data.vertices)))
    def find(i):
        while par[i]!=i:par[i]=par[par[i]];i=par[i]
        return i
    for e in o.data.edges:a,b=e.vertices;par[find(a)]=find(b)
    g={}
    for i in range(len(par)):g.setdefault(find(i),[]).append(i)
    return list(g.values())
def leafblade(v,f,p,axis,length,width):
    axis=Vector(axis).normalized();side=axis.cross(Vector((0,0,1)))
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();base=Vector(p);off=len(v)
    # Curved lanceolate leaf with pointed tip and a raised central vein.
    for i in range(5):
        t=i/4;cen=base+axis*(t*length)+Vector((0,0,math.sin(t*math.pi)*length*.12));w=math.sin(math.pi*t)**.8*width
        v.extend([tuple(cen-side*w),tuple(cen+Vector((0,0,width*.09))),tuple(cen+side*w)])
    for i in range(4):
        k=off+i*3;f.extend([(k,k+3,k+4,k+1),(k+1,k+4,k+5,k+2)])
def canopy_from_lobes(c,o):
    v=[];f=[]
    for ids in component_ids(o):
        ps=[o.data.vertices[i].co for i in ids];lo=Vector(tuple(min(p[k] for p in ps) for k in range(3)));hi=Vector(tuple(max(p[k] for p in ps) for k in range(3)));cen=(lo+hi)/2;rad=(hi-lo)/2
        for j in range(17):
            a=random.random()*math.tau;zz=random.uniform(-.9,.9);rr=math.sqrt(1-zz*zz);u=Vector((math.cos(a)*rr,math.sin(a)*rr,zz))
            pos=cen+Vector((u.x*rad.x*.82,u.y*rad.y*.82,u.z*rad.z*.82))
            leafblade(v,f,pos,u+Vector((0,0,.25)),random.uniform(.18,.32),random.uniform(.05,.09))
    ob=mesh(c,'NATURAL_'+o.name,v,f,leaf,True);ob.location=o.location;return ob
variants={o.instance_collection.name:o.instance_collection for o in s.objects if o.instance_collection and o.instance_collection.name.endswith('GROUNDED')}
plantstats={}
for c in variants.values():
    count=0
    for o in list(c.objects):
        if o.type!='MESH':continue
        if 'Trees_Foliage__' in o.name or 'Park_Foliage__' in o.name:
            new=canopy_from_lobes(c,o);count+=len(new.data.vertices)//15;c.objects.unlink(o)
        elif 'Palms_Leaflets__' in o.name:
            v=[];f=[]
            for poly in o.data.polygons:
                ids=list(poly.vertices)
                if len(ids)!=4:continue
                p=[o.data.vertices[i].co for i in ids];base=(p[0]+p[1])/2;tip=(p[2]+p[3])/2;axis=tip-base
                leafblade(v,f,base,axis,axis.length,.058)
            new=mesh(c,'NATURAL_'+o.name,v,f,leaf,True);new.location=o.location;c.objects.unlink(o);count+=len(v)//15
        elif any(t in o.name for t in ['GardenLeaves','ShrubLeaves','Shrubs__']):
            new=o.copy();new.data=o.data.copy();new.name='NATURAL_'+o.name;new.data.materials.clear();new.data.materials.append(leaflight if 'Sunlit' in o.name else leaf);c.objects.unlink(o);c.objects.link(new)
        elif any(t in o.name for t in ['Trees_Trunks','Trees_Branches','GardenTrees','Park_Trunks','Palms_Trunks']):
            new=o.copy();new.data=o.data.copy();new.name='NATURAL_'+o.name;new.data.materials.clear();new.data.materials.append(bark);c.objects.unlink(o);c.objects.link(new)
    plantstats[c.name]=count

# Granite / forest blend follows actual slope, with mineral variation and fine relief.
terrain=mat('RIO_Granite_Atlantic_Forest',(.18,.21,.13),.87);nt=terrain.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Normal'],sep.inputs[0])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.35;r.color_ramp.elements[0].color=(.31,.285,.245,1);r.color_ramp.elements[1].position=.8;r.color_ramp.elements[1].color=(.038,.105,.024,1);nt.links.new(sep.outputs['Z'],r.inputs[0])
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=4;n.inputs['Detail'].default_value=5;n.inputs['Roughness'].default_value=.73
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.35;nt.links.new(r.outputs[0],mix.inputs[1]);nt.links.new(n.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.38;b.inputs['Distance'].default_value=.65;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
mountains=[('CORCOVADO',-350,1650,650,720,704,'dome'),('PEDRA_DA_GAVEA',-2000,950,680,620,842,'table'),('DOIS_IRMAOS_WEST',-1320,450,370,430,490,'dome'),('DOIS_IRMAOS_EAST',-1080,650,330,350,350,'dome'),('TIJUCA_NORTH_EAST',850,1800,750,700,570,'dome'),('FOREST_FOOTHILLS',150,1020,1200,510,210,'dome')]
def elevation(x,y,spec):
    name,cx,cy,rx,ry,h,kind=spec;dx=(x-cx)/rx;dy=(y-cy)/ry;rho=math.sqrt(dx*dx+dy*dy)
    if rho>=1:return -.15
    if kind=='table':
        t=max(0,min(1,(rho-.17)/.83));base=h*(1-t*t*(3-2*t))
    else:base=h*max(0,1-rho*rho)**.72
    if rho<.055:return h
    erosion=noise.noise_vector(Vector((x*.012,y*.012,4))).z*24*math.sin(math.pi*rho)**.8
    return max(0,base+erosion)
forestpoints=[]
for spec in mountains:
    name,cx,cy,rx,ry,h,kind=spec;N=151;v=[];f=[]
    for j in range(N):
        y=cy-ry+2*ry*j/(N-1)
        for i in range(N):
            x=cx-rx+2*rx*i/(N-1);v.append((x,y,elevation(x,y,spec)))
    for j in range(N-1):
        for i in range(N-1):
            k=j*N+i;f.append((k,k+1,k+1+N,k+N))
    ob=mesh(land,name+'_TERRAIN',v,f,terrain,True);ob['inspired_landmark']=name;ob['peak_height_m']=h;ob['geographic_accuracy']='artistic adapted placement; not GIS reconstruction'
    for j in range(230):
        x=cx+random.uniform(-rx*.92,rx*.92);y=cy+random.uniform(-ry*.92,ry*.92);z=elevation(x,y,spec)
        slope=math.sqrt(((elevation(x+2,y,spec)-elevation(x-2,y,spec))/4)**2+((elevation(x,y+2,spec)-elevation(x,y-2,spec))/4)**2)
        if z>3 and slope<1.25 and not (name=='CORCOVADO' and math.hypot(x-cx,y-cy)<55):forestpoints.append((x,y,z))

# A reusable forest tree: curved branches and hundreds of leaf blades, not spherical crowns.
forest=bpy.data.collections.new('RIO_FOREST_TREE_SOURCE')
v=[];f=[]
def rod(v,f,a,b,r,n=9):
    a=Vector(a);b=Vector(b);q=(b-a).to_track_quat('Z','Y');off=len(v)
    for p in (a,b):
        for i in range(n):v.append(tuple(p+q@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),0))))
    f.extend([tuple(off+i for i in reversed(range(n))),tuple(off+n+i for i in range(n))]);f.extend((off+i,off+(i+1)%n,off+(i+1)%n+n,off+i+n) for i in range(n))
rod(v,f,(0,0,-.1),(.15,0,9),.24,12)
for j in range(9):
    a=j*math.tau/9;end=(math.cos(a)*2.6,math.sin(a)*2.6,7+random.random()*3);rod(v,f,(0,0,4.5),end,.08)
mesh(forest,'RIO_Forest_Trunk_Branches',v,f,bark,True);v=[];f=[]
for i in range(650):
    a=random.random()*math.tau;t=random.random()**.5;z=random.uniform(6.5,10.5);p=(math.cos(a)*3.1*t,math.sin(a)*3.1*t,z)
    leafblade(v,f,p,(math.cos(a),math.sin(a),random.uniform(-.5,.8)),.36,.11)
mesh(forest,'RIO_Forest_Leaf_Crown',v,f,leaf,True)
for i,p in enumerate(forestpoints):
    o=bpy.data.objects.new('Atlantic_Forest_Tree_'+str(i),None);o.instance_type='COLLECTION';o.instance_collection=forest;land.objects.link(o);o.location=p;o.rotation_euler.z=random.random()*math.tau;scale=random.uniform(.65,1.4);o.scale=(scale,scale,scale)
s['rio_landscape_pass']=True;s['rio_forest_instance_count']=len(forestpoints);s['rio_city_leaf_counts']=str(plantstats)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Vegetacao_Montanhas.blend')
print('LANDSCAPE_SAVED',len(forestpoints),plantstats)
