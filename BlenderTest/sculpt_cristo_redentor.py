import bpy,math,random
from mathutils import Vector
random.seed(1931)
s=bpy.context.scene
if s.get('cristo_detail_pass'):raise RuntimeError('Cristo already modeled')
root=bpy.data.collections['MAP_2000x1000_COMERCIO'];col=bpy.data.collections.new('CRISTO_REDENTOR_DETAILED');root.children.link(col)
origin=Vector((-350,1650,704))
def material(name,c,rough=.7):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
stone=material('CRISTO_Soapstone_Mosaic',(.62,.66,.62),.78)
nt=stone.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=55;tex.inputs['Detail'].default_value=3
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.39,.44,.41,1);r.color_ramp.elements[1].color=(.76,.79,.72,1);nt.links.new(tex.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color'])
vor=nt.nodes.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=170
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.018;nt.links.new(vor.outputs['Distance'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal'])
accent=material('CRISTO_Carved_Recess',(.30,.35,.32),.83);base=material('CRISTO_Pedestal_Granite',(.30,.32,.30),.84);floor=material('CRISTO_Mirante_Paving',(.49,.46,.41),.85);metal=material('CRISTO_Railing_Metal',(.12,.14,.13),.47)
def mesh(name,v,f,m=stone,smooth=True):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.materials.append(m);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=origin
    for p in me.polygons:p.use_smooth=smooth
    return ob
def box(name,p,d,m=stone,bevel=.08):
    x,y,z=p;a,b,c=[t/2 for t in d];v=[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    o=mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,False)
    if bevel:mod=o.modifiers.new('Stone edge finish','BEVEL');mod.width=bevel;mod.segments=3
    return o
def ellipsoid(name,p,scale,m=stone,segments=64,rings=40):
    v=[];f=[];x,y,z=p;a,b,c=scale
    for j in range(rings+1):
        t=math.pi*j/rings
        for i in range(segments):
            q=math.tau*i/segments;v.append((x+a*math.sin(t)*math.cos(q),y+b*math.sin(t)*math.sin(q),z+c*math.cos(t)))
    for j in range(rings):
        for i in range(segments):k=j*segments+i;f.append((k,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,k+segments))
    return mesh(name,v,f,m)
def tube(name,points,radius,m=stone):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=4
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.location=origin;cu.materials.append(m);return ob

# Summit terrace: complete paving, stairs, railings and an 8m architectural pedestal.
box('Mirante_Solid_Terrace',(0,0,-.3),(38,34,1),floor,.25)
for side in (-1,1):
    for y in range(-14,15,2):tube('Mirante_Railing_Post',[(side*18.3,y,.2),(side*18.3,y,1.4)],.045,metal)
    tube('Mirante_Railing_Handrail',[(side*18.3,-15,1.4),(side*18.3,15,1.4)],.065,metal)
    for x in range(-17,18,2):tube('Mirante_Railing_Post',[(x,side*15.8,.2),(x,side*15.8,1.4)],.045,metal)
    tube('Mirante_Railing_Handrail',[(-18.3,side*15.8,1.4),(18.3,side*15.8,1.4)],.065,metal)
for i in range(12):box('Mirante_Stair_'+str(i),(0,-17-i*.43,-.16-i*.18),(5,.5,.38),floor,.025)
box('Pedestal_Foundation',(0,0,.65),(8.5,7.8,1.3),base,.17)
box('Pedestal_Plinth',(0,0,1.6),(7.6,6.7,.65),stone,.12)
box('Pedestal_Chapel',(0,0,4.75),(6.4,5.5,5.7),base,.13)
box('Pedestal_Cornice',(0,0,7.78),(7.2,6.25,.44),stone,.08)
box('Chapel_Door_Recess',(0,-2.78,3.05),(1.5,.10,2.6),accent,.09)
for side in (-1,1):box('Chapel_Door_Jamb',(side*.93,-2.84,3.1),(.22,.25,3.1),stone,.03)
box('Chapel_Door_Lintel',(0,-2.84,4.72),(2.1,.25,.22),stone,.03)
for x in (-3.1,3.1):
    for y in (-2.7,2.7):box('Pedestal_Corner_Pilaster',(x,y,4.7),(.32,.34,5.4),stone,.02)

# Tunic loft. Deep geometry folds taper from the chest towards the hem.
v=[];f=[];N=144;R=150
for j in range(R+1):
    t=j/R;z=8.25+t*23.0
    w=2.45-.5*t+.90*math.exp(-((t-.91)/.10)**2);depth=1.30-.22*t
    for i in range(N):
        a=math.tau*i/N
        folds=.13*math.cos(a*18+t*1.5)+.065*math.cos(a*31-t*3)
        front=max(0,-math.sin(a));diagonal=.14*math.cos(a*11-t*10)*math.exp(-((t-.72)/.28)**2)*front
        v.append(((w+folds+diagonal)*math.cos(a),(depth+folds*.75+diagonal)*math.sin(a),z))
for j in range(R):
    for i in range(N):k=j*N+i;f.append((k,j*N+(i+1)%N,(j+1)*N+(i+1)%N,k+N))
f.extend([tuple(reversed(range(N))),tuple(R*N+i for i in range(N))]);mesh('Cristo_Tunic_Sculpted_Folds',v,f)
for side in (-1,1):ellipsoid('Cristo_Foot_'+str(side),(side*.93,-.83,8.32),(.63,1.40,.32))
ellipsoid('Cristo_Neck',(0,0,32.15),(.96,.87,1.65))

# Open arms with draped sleeves, cuffs, articulated hands and individually sculpted fingers.
for side in (-1,1):
    v=[];f=[];N=80;R=96
    for j in range(R+1):
        t=j/R;x=side*(2.2+t*10.5);z=30.25+.40*t;ry=1.10*(1-t)+.36*t;rz=2.45*(1-t)+.62*t
        for i in range(N):
            a=math.tau*i/N;fold=.105*math.cos(a*14+t*5)*(1-.65*t)
            v.append((x,(ry+fold)*math.cos(a),z-.6*(1-t)+(rz+fold)*math.sin(a)))
    for j in range(R):
        for i in range(N):k=j*N+i;face=(k,j*N+(i+1)%N,(j+1)*N+(i+1)%N,k+N);f.append(face if side==1 else tuple(reversed(face)))
    mesh('Cristo_Draped_Sleeve_'+str(side),v,f)
    ellipsoid('Cristo_Wrist_'+str(side),(side*12.68,-.06,30.72),(.50,.34,.39))
    ellipsoid('Cristo_Palm_'+str(side),(side*13.24,-.10,30.73),(.70,.28,.70))
    for finger in range(4):
        z=30.25+finger*.29;length=[.78,1.05,1.12,.92][finger];start=side*13.5
        pts=[(start,-.12,z),(start+side*length*.5,-.19,z+.035),(start+side*length,-.15,z+.015)]
        tube('Cristo_Finger_'+str(side)+'_'+str(finger),pts,.115)
        ellipsoid('Cristo_Fingertip',(start+side*length,-.15,z+.015),(.125,.118,.115),segments=24,rings=16)
        tube('Cristo_Finger_Nail',[(start+side*length*.80,-.267,z+.07),(start+side*length*.98,-.267,z+.07)],.013,accent)
    tube('Cristo_Thumb_'+str(side),[(side*13.05,-.18,30.18),(side*13.35,-.30,29.75),(side*13.75,-.28,29.55)],.18)
    for i in range(3):tube('Cristo_Palm_Carved_Line',[(side*(12.98+i*.15),-.377,30.30),(side*(13.02+i*.15),-.388,30.72),(side*(13.10+i*.15),-.36,31.08)],.016,accent)

# Sculpted head, calm eyes, brows, nose, lips, ears, beard and layered hair grooves.
ellipsoid('Cristo_Head_Core',(0,0,35.50),(1.36,1.08,2.14))
for side in (-1,1):
    ellipsoid('Cristo_Cheek_'+str(side),(side*.68,-.90,35.07),(.62,.25,.66))
    ellipsoid('Cristo_Ear_'+str(side),(side*1.33,.01,35.45),(.20,.26,.54),segments=40,rings=28)
    tube('Cristo_Ear_Carving',[(side*1.45,-.16,35.12),(side*1.48,-.22,35.62),(side*1.42,-.16,35.80)],.035,accent)
    # Shallow eyelid line and convex lids, all carved stone rather than painted pupils.
    x=side*.58
    tube('Cristo_Eyelid_Recess',[(x-side*.36,-1.049,35.94),(x,-1.151,35.99),(x+side*.34,-1.03,35.91)],.045,accent)
    tube('Cristo_Upper_Eyelid',[(x-side*.36,-1.043,36.01),(x,-1.14,36.11),(x+side*.34,-1.024,35.98)],.075)
    tube('Cristo_Brow_Ridge',[(x-side*.42,-.985,36.31),(x,-1.065,36.37),(x+side*.42,-.96,36.25)],.12)
ellipsoid('Cristo_Nose_Bridge',(0,-1.01,35.67),(.22,.29,.64))
ellipsoid('Cristo_Nose_Tip',(0,-1.30,35.15),(.26,.23,.22))
for side in (-1,1):ellipsoid('Cristo_Nostril_Wing',(side*.23,-1.16,35.13),(.16,.18,.15),segments=32,rings=24)
ellipsoid('Cristo_Chin',(0,-.69,33.93),(.66,.38,.38))
tube('Cristo_Closed_Mouth',[(-.43,-1.10,34.61),(0,-1.16,34.57),(.43,-1.10,34.61)],.036,accent)
tube('Cristo_Upper_Lip',[(-.42,-1.095,34.67),(-.12,-1.16,34.73),(0,-1.18,34.69),(.12,-1.16,34.73),(.42,-1.095,34.67)],.062)
tube('Cristo_Lower_Lip',[(-.38,-1.085,34.53),(0,-1.175,34.47),(.38,-1.085,34.53)],.078)
# Hair cap follows the skull; side hair extends to the shoulders.
v=[];f=[];N=100;R=40
for j in range(R+1):
    t=.04+(math.pi*.54-.04)*j/R
    for i in range(N):
        a=math.tau*i/N;rad=1+.025*math.cos(a*26+t*8)
        v.append((1.45*math.sin(t)*math.cos(a)*rad,1.16*math.sin(t)*math.sin(a)*rad+.10,35.6+2.4*math.cos(t)))
for j in range(R):
    for i in range(N):k=j*N+i;f.append((k,j*N+(i+1)%N,(j+1)*N+(i+1)%N,k+N))
mesh('Cristo_Carved_Hair_Cap',v,f)
for side in (-1,1):
    ellipsoid('Cristo_Side_Hair',(side*1.19,.49,34.70),(.46,.63,1.35))
    for j in range(12):
        x=side*(.95+j*.035);y=.03+j*.065
        tube('Cristo_Hair_Groove',[(x,y,36.0),(x+side*.17,y+.10,35.0),(x+side*.03,y+.06,33.55)],.017,accent)
for j in range(22):
    a=.15+(math.pi-.3)*j/21
    tube('Cristo_Beard_Carving',[(.96*math.cos(a),-.79,34.58),(.70*math.cos(a),-.90,34.08),(.34*math.cos(a),-.65,33.60)],.038)
# Chest relief and sweeping garment seams give the torso a readable Art Deco rhythm.
ellipsoid('Cristo_Sacred_Heart',(0,-1.34,27.25),(.35,.12,.46))
tube('Cristo_Heart_Cross',[(0,-1.48,27.55),(0,-1.48,28.04)],.045)
tube('Cristo_Heart_Crossbar',[(-.14,-1.48,27.88),(.14,-1.48,27.88)],.04)
for side in (-1,1):
    for j in range(6):
        z=28.8-j*.80
        tube('Cristo_Chest_Drape',[(side*2.3,-.48,z+.6),(side*1.5,-1.12,z+.2),(side*.40,-1.29,z-.4)],.055)
    for j in range(5):
        x=side*(.3+j*.39)
        tube('Cristo_Long_Robe_Ridge',[(x,-1.31,8.65),(x*.92,-1.33,15),(x*.78,-1.24,22)],.045)

for name,pos,target,lens in [('RIO_CRISTO_DETAIL',(-295,1550,755),(-350,1650,728),63),('RIO_CRISTO_FACE',(-332,1615,741),(-350,1650,739),90),('RIO_CITY_MOUNTAINS',(1250,-1900,900),(-250,600,300),36),('RIO_PEDESTRIAN_MOUNTAINS',(25,-348,2.1),(-350,1650,550),24)]:
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);root.objects.link(o);o.location=pos;data.lens=lens;data.clip_end=15000;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
s['cristo_detail_pass']=True;s['cristo_dimensions_reference']='30m statue + 8m pedestal; artistic mesh, official sanctuary reference';s['rio_geography']='adapted surroundings; preserved 2000x1000 city footprint'
bpy.context.view_layer.update();s.camera=bpy.data.objects['RIO_CRISTO_DETAIL'];s.cycles.samples=24;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Cristo_Montanhas_Vegetacao.blend')
s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/rio_cristo_detail.png';bpy.ops.render.render(write_still=True)
print('CRISTO_SAVED_RENDERED',len(col.objects))
