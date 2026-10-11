import bpy,math
from mathutils import Vector
s=bpy.context.scene
if s.get('sidewalk_curve_alignment_v1'):raise RuntimeError('Curve alignment already applied.')
stone=bpy.data.materials['IP_Limestone']; asphalt=bpy.data.materials['asphalt_03']
stats={'sector_variants':0,'rounded_sidewalk_corners_per_variant':4,'curb_paths':0}
def mesh(c,name,v,f,m,uvscale=.25):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.materials.append(m);me.update()
    uv=me.uv_layers.new(name='WorldMeters')
    for p in me.polygons:
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x*uvscale,co.y*uvscale)
    ob=bpy.data.objects.new(name,me);c.objects.link(ob);return ob
def solid(c,name,poly,z0,z1,m):
    n=len(poly);v=[(x,y,z) for z in (z0,z1) for x,y in poly]
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(c,name,v,f,m)
def curved_front(x0,x1,r0,r1):
    # Same 5m radius and centres as the street corner fillets.
    path=[]
    for cx,cy,r,a0 in [(x0+r0,-36+r0,r0,180),(x1-r1,-36+r1,r1,270)]:
        for i in range(25):
            a=math.radians(a0+i*90/24);path.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return path
def curb(c,path,label):
    # One continuous volumetric strip: arc, tangents and straight section share vertices.
    inner=[]
    for i,p in enumerate(path):
        prev=Vector(path[max(0,i-1)]);nxt=Vector(path[min(len(path)-1,i+1)])
        t=(nxt-prev).normalized();normal=Vector((-t.y,t.x))
        inner.append((p[0]+normal.x*.23,p[1]+normal.y*.23))
    v=[]
    for a,b in zip(path,inner):v.extend([(a[0],a[1],.226),(b[0],b[1],.226),(a[0],a[1],.49),(b[0],b[1],.49)])
    f=[]
    for i in range(len(path)-1):
        k=i*4;f.extend([(k,k+4,k+6,k+2),(k+1,k+3,k+7,k+5),(k+2,k+6,k+7,k+3),(k,k+1,k+5,k+4)])
    f.extend([(0,2,3,1),(len(v)-4,len(v)-3,len(v)-1,len(v)-2)])
    mesh(c,label,v,f,stone);stats['curb_paths']+=1
for c in list(bpy.data.collections):
    if not c.name.endswith('CONNECTED_ROADS_GROUNDED'):continue
    old=next(o for o in c.objects if o.name.startswith('CLEAR_ROAD_Urban_Sidewalk__'))
    mat=old.data.materials[0];c.objects.unlink(old)
    for side,x0,x1,r0,r1 in [('WEST',-94,20,5,3),('EAST',30,94,3,5)]:
        path=curved_front(x0,x1,r0,r1)
        polygon=path+[(x1,-28),(x0,-28)]
        solid(c,'ALIGNED_Urban_Sidewalk_'+side,polygon,.01,.47,mat)
        # Continue the curb up the outside and lateral street until the adjoining sidewalk.
        curb(c,[(x0,-28)]+path+[(x1,-28)],'ALIGNED_Continuous_Curb_'+side)
        # Fill the road-facing corner cuts with asphalt instead of exposing the low base slab.
        for xx,r,left in [(x0,r0,True),(x1,r1,False)]:
            cx=xx+r if left else xx-r;cy=-36+r;start=180 if left else 270
            arc=[]
            for i in range(25):
                a=math.radians(start+i*90/24);arc.append((cx+r*math.cos(a),cy+r*math.sin(a)))
            corner=(xx,-36)
            poly=[corner]+arc if left else [corner]+list(reversed(arc))
            # Correct winding; these patches are completely outside the paved walking contour.
            area=sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
            if area<0:poly.reverse()
            solid(c,'ALIGNED_Street_Corner_'+side+str(xx),poly,.005,.225,asphalt)
    # Remove the obsolete straight north curb; retain the boulevard's south curb.
    for oldcurb in list(c.objects):
        if not oldcurb.name.startswith('CLEAR_ROAD_Curb__'):continue
        v=[tuple(v.co) for v in oldcurb.data.vertices[:8]]
        faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        c.objects.unlink(oldcurb);mesh(c,'ALIGNED_South_Boulevard_Curb',v,faces,stone)
    stats['sector_variants']+=1
# Remove the old inclined ribbon only at the coastal junctions replaced above.
for o in list(s.objects):
    if o.type!='MESH' or not o.name.startswith('STREET_Rounded_Curbs__'):continue
    me=o.data.copy();old=o.data;v=[tuple(p.co) for p in old.vertices];f=[]
    for p in old.polygons:
        cy=sum(old.vertices[i].co.y for i in p.vertices)/len(p.vertices)
        if -326.01<=cy<=-320.7:continue
        f.append(tuple(p.vertices))
    me.clear_geometry();me.from_pydata(v,[],f);me.update();o.data=me
s['sidewalk_curve_alignment_v1']=str(stats)
s.camera=bpy.data.objects['STREET_COAST_JUNCTION'];s.cycles.samples=24
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Calcadas_Alinhadas.blend')
print(stats)
s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/resort_2x1_sidewalk_curves.png'
bpy.ops.render.render(write_still=True)
print('SIDEWALK_RENDER_DONE')
