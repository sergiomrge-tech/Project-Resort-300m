import bpy, math, os, random
from mathutils import Vector
random.seed(23)

ROOT = r"D:\ProjectResort_300m_CompactPass\BlenderTest"
os.makedirs(ROOT, exist_ok=True)
scene = bpy.data.scenes.new("RESORT_Test_200x200m")
bpy.context.window.scene = scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(ROOT, "resort_200x200_v11_overview.png")
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.75
scene.world = bpy.data.worlds.new("WLD-CoastalSky")
scene.world.use_nodes = True
wn=scene.world.node_tree.nodes; wn.clear()
sky=wn.new("ShaderNodeTexSky"); sky.sky_type="MULTIPLE_SCATTERING"; sky.sun_elevation=math.radians(48); sky.sun_rotation=math.radians(125); sky.air_density=1.05
# Procedural soft cloud banks layered over a clear tropical sky.
tc_world=wn.new("ShaderNodeTexCoord")
cloud_noise=wn.new("ShaderNodeTexNoise"); cloud_noise.inputs["Scale"].default_value=4.2; cloud_noise.inputs["Detail"].default_value=4.0; cloud_noise.inputs["Roughness"].default_value=0.68
scene.world.node_tree.links.new(tc_world.outputs["Generated"],cloud_noise.inputs["Vector"])
cloud_ramp=wn.new("ShaderNodeValToRGB"); cloud_ramp.color_ramp.elements[0].position=0.60; cloud_ramp.color_ramp.elements[0].color=(0,0,0,1); cloud_ramp.color_ramp.elements[1].position=0.72; cloud_ramp.color_ramp.elements[1].color=(1,1,1,1)
scene.world.node_tree.links.new(cloud_noise.outputs["Fac"],cloud_ramp.inputs["Fac"])
cloud_mix=wn.new("ShaderNodeMixRGB"); cloud_mix.blend_type="MIX"; cloud_mix.inputs[2].default_value=(0.82,0.89,0.96,1)
scene.world.node_tree.links.new(cloud_ramp.outputs["Color"],cloud_mix.inputs[0]); scene.world.node_tree.links.new(sky.outputs["Color"],cloud_mix.inputs[1])
bg=wn.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value=0.14
scene.world.node_tree.links.new(cloud_mix.outputs["Color"],bg.inputs["Color"])
# Keep the sky visually bright for the camera without over-lighting the materials.
cam_bg=wn.new("ShaderNodeBackground"); cam_bg.inputs["Strength"].default_value=1.0
scene.world.node_tree.links.new(cloud_mix.outputs["Color"],cam_bg.inputs["Color"])
light_path=wn.new("ShaderNodeLightPath")
world_mix=wn.new("ShaderNodeMixShader")
scene.world.node_tree.links.new(light_path.outputs["Is Camera Ray"],world_mix.inputs[0])
scene.world.node_tree.links.new(bg.outputs["Background"],world_mix.inputs[1])
scene.world.node_tree.links.new(cam_bg.outputs["Background"],world_mix.inputs[2])
wo=wn.new("ShaderNodeOutputWorld"); scene.world.node_tree.links.new(world_mix.outputs[0],wo.inputs["Surface"])
col = bpy.data.collections.new("COL-Resort-200x200")
scene.collection.children.link(col)

def mat(name, color, rough=0.7, metal=0.0, noise=0.0):
    m=bpy.data.materials.new("MAT-"+name); m.diffuse_color=(*color,1); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); bs=nt.nodes.new("ShaderNodeBsdfPrincipled"); out=nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bs.outputs["BSDF"],out.inputs["Surface"]); bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough; bs.inputs["Metallic"].default_value=metal
    if noise:
        tc=nt.nodes.new("ShaderNodeTexCoord")
        tex=nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value=3.8 if any(k in name for k in ("Lime","Paint")) else (18.0 if "Sand" in name else 42.0)
        tex.inputs["Detail"].default_value=5.0; tex.inputs["Roughness"].default_value=0.72
        nt.links.new(tc.outputs["Object"],tex.inputs["Vector"])
        ramp=nt.nodes.new("ShaderNodeValToRGB")
        lo=tuple(max(0,c*0.78) for c in color)+(1,); hi=tuple(min(1,c*1.12+0.006) for c in color)+(1,)
        ramp.color_ramp.elements[0].color=lo; ramp.color_ramp.elements[1].color=hi
        nt.links.new(tex.outputs["Fac"],ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
        bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=min(0.22,noise*1.45); bump.inputs["Distance"].default_value=0.025
        nt.links.new(tex.outputs["Fac"],bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m

sand=mat("Warm_Sand",(0.68,0.48,0.25),0.92,0,0.18)
wet=mat("Wet_Sand",(0.38,0.31,0.22),0.85,0,0.08)
water=mat("Atlantic_Teal",(0.018,0.16,0.22),0.24,0.12)
foam=mat("Sea_Foam",(0.75,0.88,0.84),0.35)
pave=mat("Limestone_Promenade",(0.43,0.37,0.27),0.82,0,0.16)
pave2=mat("Paving_Accent",(0.15,0.29,0.24),0.75,0,0.12)
asphalt=mat("Warm_Asphalt",(0.105,0.12,0.12),0.82,0,0.2)
roadline=mat("Road_Marking",(0.92,0.82,0.57),0.65)
concrete=mat("Concrete",(0.29,0.30,0.27),0.86,0,0.12)
wall1=mat("Ivory_Lime",(0.62,0.46,0.28),0.72,0,0.1)
wall2=mat("Seafoam_Paint",(0.08,0.29,0.23),0.65,0,0.1)
wall3=mat("Coral_Lime",(0.48,0.15,0.095),0.72,0,0.1)
wall4=mat("Butter_Paint",(0.57,0.32,0.12),0.7,0,0.1)
wall5=mat("Deep_Teal",(0.035,0.15,0.16),0.65,0,0.1)
glass=mat("Blue_Tinted_Glass",(0.018,0.085,0.12),0.2,0.28)
next(n for n in glass.node_tree.nodes if n.bl_idname=="ShaderNodeBsdfPrincipled").inputs["Transmission Weight"].default_value=0.22
metal=mat("Anodized_Bronze",(0.22,0.17,0.11),0.34,0.78)
dark=mat("Shadow_Reveal",(0.055,0.075,0.073),0.82)
leaf=mat("Palm_Leaf",(0.10,0.31,0.16),0.82)
leaf2=mat("Palm_Leaf_Light",(0.27,0.43,0.19),0.78)
trunk=mat("Palm_Fiber",(0.38,0.23,0.12),0.9)
plant=mat("Shrub_Green",(0.12,0.31,0.17),0.88)

BATCH={}
def link(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj); return obj

def batch_geometry(n, verts, faces, material):
    v,f=BATCH.setdefault(material,([],[])); offset=len(v); v.extend(verts)
    f.extend(tuple(offset+i for i in face) for face in faces)

def mesh_from_geometry(n, verts, faces, material):
    me=bpy.data.meshes.new(n+"Mesh"); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new("GEO-"+n,me); col.objects.link(ob); return ob

def box(n, loc, dims, material, bevel=0.0):
    x,y,z=loc; hx,hy,hz=(v/2 for v in dims)
    verts=[(x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y+hy,z-hz),(x-hx,y+hy,z-hz),
           (x-hx,y-hy,z+hz),(x+hx,y-hy,z+hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    if bevel>=0.14:
        o=mesh_from_geometry(n,verts,faces,material); mod=o.modifiers.new("Soft_Edges","BEVEL"); mod.width=bevel; mod.segments=2
        o.modifiers.new("Weighted_Corner_Normals","WEIGHTED_NORMAL"); return o
    batch_geometry(n,verts,faces,material)

def cyl(n, loc, radius, depth, material, vertices=12, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=(radius if r2 is None else r2), depth=depth, location=loc)
    o=link(bpy.context.object); o.name="GEO-"+n
    if material:o.data.materials.append(material)
    return o

def mesh_obj(n, verts, faces, material):
    batch_geometry(n,verts,faces,material)

def flush_batch():
    for material,(verts,faces) in BATCH.items():
        mesh_from_geometry("Batch_"+material.name,verts,faces,material)

# 200 x 200 m ground plane, with an 8 m promenade and a 9 m building forecourt.
box("Site_200x200m",(0,0,-0.8),(200,200,1.6),wet,0.0)
box("Beach_Sand",(0,-77.5,0.05),(200,29,0.1),sand)
box("Wet_Shoreline",(0,-62.4,0.10),(200,1.2,0.12),wet)
box("Atlantic_Water",(0,-96,0.0),(200,8.0,0.16),water)
for y in (-92.0,-91.55,-91.1):
    box("Foam_Ribbon",(0,y,0.10),(200,0.16,0.025),foam,0.02)
# Fine bands/tiles across the promenade
box("Promenade_8m",(0,-61.0,0.14),(200,8,0.22),pave)
for x in range(-96,101,4):
    box("Promenade_Joint",(x,-61.0,0.26),(0.035,7.8,0.012),concrete)
box("Promenade_Sea_Edge",(0,-65.05,0.32),(200,0.35,0.42),concrete,0.08)
box("Promenade_Inland_Edge",(0,-56.95,0.32),(200,0.28,0.40),concrete,0.08)
# Nine-metre landscaped forecourt between promenade and building fronts
box("Waterfront_Forecourt",(0,-52.45,0.13),(200,8.7,0.2),pave2)
# Road and sidewalks behind the coastal building row
box("Service_Street",(0,-14,0.02),(200,11,0.18),asphalt)
box("Service_North_Sidewalk",(0,-7.4,0.13),(200,2.2,0.22),pave)
box("Service_South_Sidewalk",(0,-20.6,0.13),(200,2.2,0.22),pave)
# Main boulevard with two carriageways and landscaped median
box("Avenida_Carriageway",(0,37,0.0),(200,23,0.2),asphalt)
box("Median_Planting",(0,37,0.18),(200,2.1,0.35),plant,0.15)
for x in range(-96,101,12):
    box("Avenida_Dashed_Line",(x,37,0.12),(5.5,0.13,0.025),roadline)
for y in (25.6,48.4):
    box("Avenida_Curb",(0,y,0.20),(200,0.32,0.36),concrete,0.07)
# City block paving and green pocket park
box("North_Civic_Square",(0,69,0.0),(200,17,0.2),pave)
box("Pocket_Park",(0,84,0.0),(200,13,0.2),plant)
for x in range(-90,91,15):
    box("North_Park_Path",(x,84,0.13),(2.8,13,0.12),pave,0.05)

# Waterfront architecture: 6 mid-rise mixed-use buildings, frontage faces the sea.
facades=[wall1,wall2,wall3,wall4,wall1,wall5]
centers=[-82,-49,-16,17,50,83]
widths=[27,27,27,27,27,27]
heights=[23,28,25,31,24,29]
front=-48.0
for bi,(cx,w,h,wm) in enumerate(zip(centers,widths,heights,facades)):
    depth=24 if bi%2==0 else 27
    cy=front+depth/2
    box("Waterfront_Building_%02d"%bi,(cx,cy,h/2),(w,depth,h),wm,0.16)
    # arcade/retail plinth with display glazing and stone surround
    box("Retail_Base",(cx,front-0.09,0.42),(w+0.18,0.25,0.78),wall5,0.05)
    for j in range(4):
        wx=cx-w*0.43+j*(w*0.86/3)
        box("Shopfront_Glass",(wx,front-0.145,2.12),(w*0.19,0.08,2.65),glass,0.025)
        box("Shopfront_Mullion",(wx-w*0.095,front-0.205,2.12),(0.12,0.12,2.78),metal,0.02)
        box("Shopfront_Mullion",(wx+w*0.095,front-0.205,2.12),(0.12,0.12,2.78),metal,0.02)
    box("Entry_Canopy",(cx,front-0.95,3.62),(w*0.48,1.75,0.20),metal,0.06)
    box("Sign_Band",(cx,front-0.28,3.25),(w*0.75,0.08,0.27),wall4,0.025)
    # repeated upper-floor windows with deep reveals, sills, and bronze frames
    cols_n=5; rows=max(4,int((h-4.7)//3.2))
    for r in range(rows):
        z=5.35+r*3.15
        if z+1.55>h-1.8: continue
        for c in range(cols_n):
            wx=cx-w*0.38+c*(w*0.76/(cols_n-1))
            ww=2.25 if c in (1,3) else 1.95
            box("Window_Recess",(wx,front-0.085,z),(ww+0.34,0.11,2.08),dark,0.025)
            box("Window_Glass",(wx,front-0.17,z),(ww,0.07,1.72),glass,0.025)
            for dx in (-ww/2-0.10,ww/2+0.10):
                box("Window_Jamb",(wx+dx,front-0.26,z),(0.16,0.25,2.12),metal,0.025)
            box("Window_Head",(wx,front-0.26,z+1.0),(ww+0.34,0.25,0.15),metal,0.025)
            box("Stone_Sill",(wx,front-0.34,z-1.02),(ww+0.52,0.48,0.18),wall4,0.04)
            box("Window_Mullion",(wx,front-0.265,z),(0.08,0.18,1.7),metal,0.018)
            if c in (1,3) and r%2==0:
                box("Balcony_Slab",(wx,front-1.05,z-1.05),(ww+0.72,1.55,0.20),concrete,0.05)
                box("Balcony_Rail_Top",(wx,front-1.77,z-0.25),(ww+0.6,0.09,0.08),metal,0.03)
                for k in range(7):
                    xx=wx-(ww+0.6)/2+k*(ww+0.6)/6
                    box("Balcony_Baluster",(xx,front-1.77,z-0.68),(0.045,0.055,0.8),metal,0.015)
                box("Balcony_Rail_End",(wx-(ww+0.6)/2,front-1.1,z-0.65),(0.08,1.35,0.8),metal,0.02)
                box("Balcony_Rail_End",(wx+(ww+0.6)/2,front-1.1,z-0.65),(0.08,1.35,0.8),metal,0.02)
    # Facade articulation: pilasters and slim floor bands add a finer architectural rhythm.
    for px in (-w*0.47,w*0.47):
        box("Facade_Pilaster",(cx+px,front-0.18,h/2),(0.38,0.34,h-0.85),wall4,0.14)
    for r in range(1,int(h//3.15)):
        zz=4.7+r*3.15
        box("Floor_Belt_Course",(cx,front-0.12,zz),(w+0.3,0.24,0.12),wall4,0.04)
    # layered cornice, parapet, rooftop service volumes
    box("Crown_Cornice",(cx,cy,h-0.48),(w+0.55,depth+0.55,0.48),wall4,0.10)
    box("Roof_Parapet",(cx,cy,h+0.25),(w,depth,0.45),wm,0.08)
    box("Roof_Service",(cx+w*0.24,cy+depth*0.20,h+1.35),(w*0.30,depth*0.22,2.25),wall5,0.08)
    box("Roof_Pergola",(cx-w*0.20,front+depth*0.62,h+0.85),(w*0.38,2.4,0.12),metal,0.04)
    for k in range(6):
        box("Pergola_Slat",(cx-w*0.39+k*w*0.076,front+depth*0.62,h+1.08),(0.08,2.4,0.12),metal,0.025)

# A true metre scale coastal palm: tapered segmented trunk and curved blade mesh.
def palm(x,y,height=8.5, lean=0.45):
    seg=12; verts=[]; faces=[]
    for i in range(seg+1):
        t=i/seg; z=0.35+t*(height-0.35); cx=x+lean*t*t; rad=0.34*(1-t)+0.11
        for j in range(8):
            a=2*math.pi*j/8; verts.append((cx+rad*math.cos(a),y+rad*math.sin(a),z))
    for i in range(seg):
        for j in range(8):
            a=i*8+j; b=i*8+(j+1)%8; faces.append((a,b,b+8,a+8))
    mesh_obj("Palm_Trunk",verts,faces,trunk)
    crown=(x+lean,y,height)
    for li in range(14):
        a=2*math.pi*li/14+0.24; dx,dy=math.cos(a),math.sin(a)
        length=5.0+random.random()*1.1; rise=-0.30+random.random()*0.30
        vv=[]; ff=[]; steps=12
        for s in range(steps+1):
            t=s/steps; px=crown[0]+dx*length*t; py=crown[1]+dy*length*t
            z=crown[2]+rise*t-1.25*t*t; half=(math.sin(math.pi*t)**0.7)*(0.34*(1-t)+0.035)
            vv.extend([(px-dy*half,py+dx*half,z),(px+dy*half,py-dx*half,z)])
        for s in range(steps):
            ff.append((2*s,2*s+1,2*s+3,2*s+2))
        mesh_obj("Palm_Frond",vv,ff,leaf if li%2 else leaf2)

for i,x in enumerate(range(-90,91,18)): palm(x,-61.0,8.4+(i%3)*0.45,(i%2)*0.35-0.1)
# benches, lights and planters distributed outside circulation line
for x in range(-84,85,28):
    box("Bench_Seat",(x,-55.0,0.74),(2.4,0.55,0.14),trunk,0.07)
    box("Bench_Back",(x,-55.30,1.25),(2.4,0.12,0.95),trunk,0.06)
    for dx in (-0.85,0.85): cyl("Bench_Leg",(x+dx,-55.0,0.35),0.07,0.68,metal,8)
for x in range(-90,91,30):
    cyl("Promenade_Lamp_Pole",(x,-57.7,3.2),0.065,6.0,metal,10)
    box("Lamp_Lantern",(x,-57.7,6.25),(0.65,0.65,0.32),roadline,0.08)
# curb ramps and zebra crossings at three points
for x in (-60,0,60):
    for j in range(8):
        box("Zebra_Crossing",(x-3.0+j*0.85,-14,0.13),(0.46,10.4,0.025),roadline,0.03)
# elevated coastal promenade entry/street connections
for x in (-60,0,60):
    box("Crosswalk_Forecourt",(x,-52.4,0.28),(4.6,9.1,0.10),pave,0.04)
    box("Tactile_Guidance",(x,-61.0,0.30),(0.42,7.1,0.08),roadline)
# second boulevard median palms
for x in range(-90,91,22):
    palm(x,37,7.0,0.0)
# Square manholes and linear drainage along building/service interfaces
for x in range(-90,91,20):
    box("Drain_Grate",(x,-20.8,0.28),(1.2,0.75,0.04),metal,0.03)
    for k in range(7): box("Drain_Slot",(x-0.48+k*0.16,-20.8,0.31),(0.04,0.62,0.018),dark)

# Low tropical planting beds fit in the gaps between buildings and keep the accessible path clear.
for px in (-65.5,-32.5,0.5,33.5,66.5):
    box("Tropical_Planter",(px,-53.4,0.42),(2.7,1.05,0.50),concrete,0.14)
    for j in range(9):
        sx=px+random.uniform(-1.0,1.0); sy=-53.4+random.uniform(-0.28,0.28)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1.0,location=(sx,sy,0.90+random.uniform(-0.08,0.12)))
        sh=link(bpy.context.object); sh.name="GEO-Tropical_Foliage_Cluster"
        sh.scale=(random.uniform(0.25,0.40),random.uniform(0.20,0.32),random.uniform(0.30,0.48))
        sh.data.materials.append(leaf if j%2 else plant)
        for poly in sh.data.polygons: poly.use_smooth=True
flush_batch()

# Lighting / two real cameras for overview and pedestrian inspection
sun_data=bpy.data.lights.new("LGT-CoastalSun","SUN"); sun_data.energy=1.15; sun_data.angle=math.radians(9)
sun=bpy.data.objects.new("LGT-CoastalSun",sun_data); col.objects.link(sun); sun.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-32))
fill_data=bpy.data.lights.new("LGT-SkyFill","AREA"); fill_data.energy=1100; fill_data.shape="DISK"; fill_data.size=100
fill=bpy.data.objects.new("LGT-SkyFill",fill_data); col.objects.link(fill); fill.location=(0,-15,125)
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def camera(n,loc,target,lens):
    d=bpy.data.cameras.new(n); o=bpy.data.objects.new(n,d); col.objects.link(o); o.location=loc; aim(o,target); d.lens=lens; return o
cam=camera("CAM-Overview",(140,-220,190),(0,-4,2),32); scene.camera=cam
cam_walk=camera("CAM-Promenade",(-45,-56,1.72),(-24,-48,4.2),30)
scene.render.image_settings.color_mode="RGBA"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"Resort_Test_200x200_v11.blend"))
bpy.ops.render.render(write_still=True)
scene.render.filepath=os.path.join(ROOT,"resort_200x200_v11_walk.png"); scene.camera=cam_walk
bpy.ops.render.render(write_still=True); scene.camera=cam
# Portable Unity-oriented interchange: GLB retains Principled materials; FBX supports scene geometry.
export_objects=[o for o in col.objects if o.type in {"MESH"}]
bpy.ops.object.select_all(action="DESELECT")
for o in export_objects:o.select_set(True)
bpy.context.view_layer.objects.active=export_objects[0] if export_objects else None
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,"Resort_Test_200x200_v11.glb"),export_format="GLB",use_selection=True,export_apply=True,export_materials="EXPORT",export_yup=True,export_lights=False,export_cameras=False)
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,"Resort_Test_200x200_v11.fbx"),use_selection=True,apply_unit_scale=True,apply_scale_options="FBX_SCALE_ALL",bake_space_transform=True,object_types={"MESH"},use_mesh_modifiers=True,mesh_smooth_type="FACE",path_mode="COPY",axis_forward="-Z",axis_up="Y",embed_textures=True)
# Machine-readable scene dimensions and artifact summary.
mesh_count=len(export_objects); face_count=sum(len(o.data.polygons) for o in export_objects)
with open(os.path.join(ROOT,"build_report.txt"),"w",encoding="utf-8") as f:
    f.write("scene=RESORT_Test_200x200m\nsite_dimensions_m=200x200\n")
    f.write(f"export_mesh_objects={mesh_count}\nexport_mesh_faces={face_count}\n")
    f.write("promenade_width_m=8\nbuilding_forecourt_width_m=9\n")
    f.write("source_scene=Resort_Test_200x200_v11.blend\nexport_formats=GLB,FBX\n")
print("RESORT_200X200_BUILD_DONE",mesh_count,face_count)
