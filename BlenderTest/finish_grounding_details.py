import bpy
from mathutils import Vector
s=bpy.context.scene
if s.get('grounding_details_counts'):
    raise RuntimeError('Detail supports already applied; reopen the output of fix_floating_assets.py before regenerating.')
wood=bpy.data.materials['IP_Teak']; metal=bpy.data.materials['IP_Bronze']; stone=bpy.data.materials['IP_Limestone']
def box(c,name,p,d,m):
    x,y,z=p; a,b,h=[v/2 for v in d]
    v=[(x-a,y-b,z-h),(x+a,y-b,z-h),(x+a,y+b,z-h),(x-a,y+b,z-h),(x-a,y-b,z+h),(x+a,y-b,z+h),(x+a,y+b,z+h),(x-a,y+b,z+h)]
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(m);me.update()
    o=bpy.data.objects.new('FIX_'+name,me);c.objects.link(o)
def bounds(o,ids):
    p=[o.matrix_world@o.data.vertices[i].co for i in ids]
    return [min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]
count={'menu_feet':0,'surf_racks':0,'plant_stems':0,'fashion_stands':0,'sealed_paving_strips':0,'cabana_beams':0}
for c in list(bpy.data.collections):
    if not c.name.endswith('CONNECTED_ROADS_GROUNDED'): continue
    # Solid infill seals the gaps between promenade, cycle path, and boulevard curb.
    if 'COAST' in c.name:
        for y,w,z in [(-56.75,.5,.34),(-52.75,1.5,.27)]:
            box(c,'Paving_Transition_Solid',(0,y,z/2),(200,w,z),stone);count['sealed_paving_strips']+=1
        for xx in (-62,-42):
            for yy in (2,43):
                for y in (yy-1.2,yy+1.2):
                    box(c,'Cabana_Beam',(xx,y,3.22),(4.5,.16,.18),wood);count['cabana_beams']+=1
        retail=bpy.data.collections.new('RETAIL_GROUND_SUPPORTS'); c.children.link(retail)
        for o in list(c.all_objects):
            if o.type!='MESH': continue
            if o.name.startswith('RETAIL_Menu_Boards'):
                for i in range(0,len(o.data.vertices),8):
                    lo,hi=bounds(o,range(i,i+8));x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2
                    for dx in (-.16,.16):
                        box(retail,'Menu_Board_Feet',(x+dx,y,(.465+lo[2]+.07)/2),(.045,.32,lo[2]+.07-.465),wood);count['menu_feet']+=1
            if o.name.startswith('RETAIL_Surfboards'):
                for i in range(0,len(o.data.vertices),64):
                    lo,hi=bounds(o,range(i,i+64));x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2
                    box(retail,'Surfboard_Rack_Base',(x,y,.555),(.48,.28,.12),wood)
                    box(retail,'Surfboard_Rack_Back',(x,y+.09,1.10),(.07,.08,1.17),wood);count['surf_racks']+=1
            if o.name.startswith('RETAIL_Shop_Pots'):
                # Cylinder mesh components are 48 vertices (24 per ring).
                for i in range(0,len(o.data.vertices),48):
                    lo,hi=bounds(o,range(i,min(i+48,len(o.data.vertices))));x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2
                    box(retail,'Plant_Stem',(x,y,.944),(.025,.025,.12),wood)
                    box(retail,'Pot_Foot',(x,y,.483),(.24,.24,.04),wood);count['plant_stems']+=1
            if o.name.startswith('RETAIL_Fashion_Display'):
                for i in range(0,len(o.data.vertices),8):
                    lo,hi=bounds(o,range(i,i+8))
                    if hi[2]-lo[2]<.5:continue
                    x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2
                    box(retail,'Fashion_Stand',(x,y+.08,1.515),(.025,.025,.75),metal)
                    box(retail,'Fashion_Hanger',(x,y,1.87),(.30,.20,.035),metal);count['fashion_stands']+=1
s['grounding_details_counts']=str(count)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Comercio_Ruas_Corrigido.blend')
print(count)
