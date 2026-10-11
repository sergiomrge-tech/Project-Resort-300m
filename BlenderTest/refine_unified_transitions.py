import bpy,math
from mathutils import Vector
wood=bpy.data.materials['MARE_Teak_Existing_PBR'];cream=bpy.data.materials['MARE_Linen_Canvas'];steel=bpy.data.materials['MARE_Brushed_Stainless'];brass=bpy.data.materials['MARE_Brushed_Brass'];teal=bpy.data.materials['MARE_Painted_Teal'];glass=bpy.data.materials['MARE_Architectural_Glass'];curb=bpy.data.materials['URBAN_PBR_Curb_Cut_Concrete']
def box(name,loc,size,mat,c):
    x,y,z=[v/2 for v in size];vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();me.materials.append(mat)
    uv=me.uv_layers.new(name='WoodGrain');uv2=me.uv_layers.new(name='UrbanMeters')
    for f in me.polygons:
        n=max((abs(f.normal[k]),k) for k in range(3))[1];axes=[k for k in range(3) if k!=n]
        for li in f.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]]);uv2.data[li].uv=uv.data[li].uv
    o=bpy.data.objects.new(name,me);c.objects.link(o);o.location=loc;return o
def instance(name,source,c,loc):
    o=bpy.data.objects.new(name,None);c.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=source;o.location=loc;return o
p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.61,.76,.70,1);p.inputs['Metallic'].default_value=.035;p.inputs['Roughness'].default_value=.08;p.inputs['Transmission Weight'].default_value=.78
# Reuse dining furniture including the woven chairs, not just table tops.
dining=bpy.data.collections['UNIDA_DINING_EQUIPMENT'];src=bpy.data.collections['MARE_16_GASTRONOMIA']
for o in src.objects:
    if 'Chair' in o.name and o.name not in dining.objects:dining.objects.link(o)
initial=bpy.data.collections.new('UNIDA_INITIAL_RESTAURANT_TABLES')
for o in dining.objects:
    root=o
    while root.parent:root=root.parent
    if 101<root.location.y<105:initial.objects.link(o)
c=bpy.data.collections['UNIDA_04_RESTAURANTE_TRANSFORMADO'];instance('UNIDA_Initial_Dining',initial,c,(-40,-112,0))
rear=bpy.data.collections['UNIDA_06_RESTAURANTE_NOS_FUNDOS'];instance('UNIDA_Rear_Dining',dining,rear,(-40,-93,0))
for o in rear.objects:
    if o.name=='UNIDA_Kitchen_At_Back':o.location.y=26
# Real entrances and through-openings at the lobby-to-restaurant seam.
for name,y,w in [('UNIDA_04_RESTAURANTE_TRANSFORMADO',-20,20),('UNIDA_06_HOTEL_SIMPLES',-21,24),('UNIDA_06_HOTEL_SIMPLES',3,24),('UNIDA_06_RESTAURANTE_NOS_FUNDOS',5,24)]:
    c=bpy.data.collections[name]
    for o in list(c.objects):
        if 'Facade_Glass' in o.name and abs(o.location.y-y)<.15 and abs(o.location.x)<3.0 and o.location.z<3:bpy.data.objects.remove(o,do_unlink=True)
        elif 'Mullion' in o.name and abs(o.location.y-y)<.15 and abs(o.location.x)<.15 and o.location.z<3:bpy.data.objects.remove(o,do_unlink=True)
    for x in [-2.1,2.1]:box('UNIDA_Entrance_Frame',(x,y,1.9),(.14,.18,2.9),wood,c)
# Roof is replaced when the business changes type, and removed for the upper dining floor.
def tiledroof(name,x,y,w,d):
    c=bpy.data.collections.new(name);verts=[[] for _ in range(5)];faces=[[] for _ in range(5)];cols=round(w/.24);rows=round((d/2)/.42);z=3.68;rise=1.75
    for side in [-1,1]:
        for row in range(rows):
            yy=.04+row*(d/2-.08)/rows
            for col in range(cols):
                idx=(row+col)%5;vs=verts[idx];fs=faces[idx];off=len(vs);xx=x-w/2+(col+.5)*w/cols
                for length in [0,.50]:
                    py=yy+length
                    for k in range(9):a=k*math.pi/8;vs.append((xx+.12*math.cos(a),y+side*py,z+rise*(1-py/(d/2))+.095*math.sin(a)))
                for k in range(8):fs.append((off+k,off+k+1,off+k+10,off+k+9))
    for i in range(5):
        me=bpy.data.meshes.new(name);me.from_pydata(verts[i],[],faces[i]);me.update();me.materials.append(bpy.data.materials['MARE_Terracotta_%d'%i])
        for p in me.polygons:p.use_smooth=True
        o=bpy.data.objects.new(name+'_Curved_Tiles',me);c.objects.link(o)
    for side in [-1,1]:box(name+'_Eave',(x,y+side*d/2,z-.04),(w,.18,.20),wood,c)
    box(name+'_Ridge',(x,y,z+rise+.03),(w,.22,.18),wood,c)
    return c
roof1=tiledroof('UNIDA_RESTAURANT_ORIGINAL_ROOF',0,-9,20.8,22.8)
roof2=tiledroof('UNIDA_RESTAURANT_REAR_ROOF',0,15,24.8,20.8)
for i in range(4,6):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(roof1)
for i in range(6,15):bpy.data.scenes['MARE_UNIDA_ETAPA_%02d'%i].collection.children.link(roof2)
# Tiled restaurant gables have a supporting wall, no floating roof.
for roofc,x,y,w,d in [(roof1,0,-9,20.8,22.8),(roof2,0,15,24.8,20.8)]:
    for sign in [-1,1]:
        xx=x+sign*w/2;me=bpy.data.meshes.new('UNIDA_Gable');me.from_pydata([(xx,y-d/2,3.6),(xx,y+d/2,3.6),(xx,y,5.42)],[],[(0,1,2)]);me.update();me.materials.append(teal);o=bpy.data.objects.new('UNIDA_Supported_Gable',me);roofc.objects.link(o)
c=bpy.data.collections['UNIDA_04_RESTAURANTE_TRANSFORMADO']
for x in [-8,-4,0,4,8]:box('UNIDA_Restaurant_Awning',(x,-21.15,3.10),(3.6,2.3,.045),cream,c)
# Vertical circulation begins with the hotel and extends when floors are purchased.
def stairs(c,floor):
    for run in range(2):
        for step in range(8):
            top=floor+(run*8+step+1)*.2;yy=-5+step*.28 if run==0 else -2.76-step*.28;xx=7 if run==0 else 8.9
            box('UNIDA_Stair_Tread',(xx,yy,top-.10),(1.65,.30,.20),wood,c)
        for x in [6.15,9.75]:box('UNIDA_Stair_Rail_Post',(x,-2.6,floor+2.1),(.05,.05,1),steel,c)
    box('UNIDA_Stair_Mid_Landing',(7.95,-2.3,floor+1.5),(3.5,.7,.20),wood,c)
    box('UNIDA_Stair_Top_Landing',(8.9,-5.45,floor+3.1),(1.7,.65,.20),wood,c)
    for x in [6.15,9.75]:box('UNIDA_Stair_Landing_Rail',(x,-2.3,floor+2.50),(.05,.72,.06),brass,c)
stairs(bpy.data.collections['UNIDA_06_HOTEL_SIMPLES'],.45)
stairs(bpy.data.collections['UNIDA_19_AMPLIACAO_VERTICAL'],3.65)
stairs(bpy.data.collections['UNIDA_20_RESORT_UNICO'],6.85)
# Cut actual stair openings in the existing slabs with a local cutter.
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20']
bpy.context.view_layer.update()
for cname in ['UNIDA_06_HOTEL_SIMPLES','UNIDA_19_AMPLIACAO_VERTICAL']:
    c=bpy.data.collections[cname]
    for o in list(c.objects):
        if not ('Floor' in o.name or '_Roof' in o.name) or o.location.z<3:continue
        if abs(o.location.x)>1:continue
        cutter=box('UNIDA_TEMP_STAIR_OPENING',(7.9,-3.8,o.location.z),(4.0,4.1,1),wood,c)
        modifier=o.modifiers.new('Stair opening','BOOLEAN');modifier.operation='DIFFERENCE';modifier.object=cutter
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
for cname,z,h in [('UNIDA_06_HOTEL_SIMPLES',3.6,6.3),('UNIDA_19_AMPLIACAO_VERTICAL',8.45,3.2)]:
    c=bpy.data.collections[cname]
    for x in [-9.4,-6.6]:box('UNIDA_Lift_Shaft_Side',(x,.4,z),(.12,2.8,h),curb,c)
    box('UNIDA_Lift_Shaft_Back',(-8,1.8,z),(2.9,.12,h),curb,c)
    levels=[.45,3.65] if z<4 else [6.85,10.05]
    for floor in levels:
        box('UNIDA_Lift_Door',(-8,-1.0,floor+1.1),(1.25,.065,2.15),steel,c)
        box('UNIDA_Lift_Indicator',(-8,-1.045,floor+2.36),(.18,.02,.09),teal,c)
for o in bpy.data.collections['UNIDA_05_SANITARIOS_INTEGRADOS'].objects:
    if o.instance_collection:o.location.x=-19
camera=bpy.data.objects['UNIDA_Camera_Restaurant'];camera.location=(0,-57,16);camera.rotation_euler=(Vector((0,-7,2))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.context.window.scene=bpy.data.scenes['MARE_UNIDA_ETAPA_20'];bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Mare_Evolucao_Unificada_v2.blend')
print('Transformation details: restaurant roof, furniture, entrances, staircase and lift shafts')
