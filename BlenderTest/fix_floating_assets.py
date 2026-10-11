"""Run once on the saved connected-road scene using Blender MCP.
Private mesh copies preserve the previous scene's assets. All foliage follows its root.
"""
import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

s=bpy.context.scene
if s.get('grounding_pass_v1'):
    raise RuntimeError('Grounding pass already applied; reopen the uncorrected file before regenerating.')
report={}
wood=bpy.data.materials['IP_Teak']; metal=bpy.data.materials['IP_Bronze']; stone=bpy.data.materials['IP_Limestone']

def parts(o,step):
    return [list(range(i,min(i+step,len(o.data.vertices)))) for i in range(0,len(o.data.vertices),step)]

def bounds(o,ids):
    p=[o.matrix_world@o.data.vertices[i].co for i in ids]
    return [min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]

def components(o):
    parent=list(range(len(o.data.vertices)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for e in o.data.edges:
        a,b=e.vertices; parent[find(a)]=find(b)
    groups={}
    for i in range(len(parent)): groups.setdefault(find(i),[]).append(i)
    return list(groups.values())

def root_list(o,step,base_count):
    out=[]
    for ids in parts(o,step):
        p=[o.matrix_world@o.data.vertices[i].co for i in ids[:base_count]]
        out.append((sum(v.x for v in p)/len(p),sum(v.y for v in p)/len(p),min(v.z for v in p)))
    return out

def nearest(x,y,roots):
    return min(( (x-r[0])**2+(y-r[1])**2,i) for i,r in enumerate(roots))[1]

def geometry_box(batch,name,p,d,m):
    vv,ff,mm=batch.setdefault((name,m.name),([],[],m)); off=len(vv)
    x,y,z=p; a,b,c=[v/2 for v in d]
    vv.extend([(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)])
    ff.extend(tuple(off+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

def flush(batch,c):
    for (name,mname),(v,f,m) in batch.items():
        me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.materials.append(m); me.update()
        o=bpy.data.objects.new('FIX_'+name+'__'+mname,me); c.objects.link(o)

sources=[c for c in bpy.data.collections if c.name.endswith('CONNECTED_ROADS')]
for src in sources:
    coast='COAST' in src.name
    c=bpy.data.collections.new(src.name+'_GROUNDED'); c['grounding_version']=1
    lookup={}; originals={}; clones={}; batch={}; log={'vegetation':[],'support_legs':0,'pergola_beams':0,'patios':0}
    for o in src.objects:
        c.objects.link(o); lookup[o.name]=o; originals[o.name]=o
    for child in src.children: c.children.link(child)
    def private(name):
        if name not in clones:
            old=lookup[name]; new=old.copy(); new.data=old.data.copy(); new.name='GROUNDED_'+old.name
            c.objects.unlink(old); c.objects.link(new); clones[name]=new; lookup[name]=new
        return clones[name]
    ground=[]; footprints=[]
    for o in src.all_objects:
        if o.type!='MESH': continue
        lo,hi=bounds(o,range(len(o.data.vertices)))
        if 'Shell__' in o.name or 'UPPER_STRUCTURE' in o.name: footprints.append((lo[0],hi[0],lo[1],hi[1]))
        isground=any(t in o.name for t in ['Site_','Beach__','Promenade__','Cycleway__','CLEAR_ROAD_','Courtyard_Deck','GardenBeds','Resort_Garden','Garden_Walkway','Garden_Crosswalk','Restaurant_Terrace','Forecourt','InteriorFloor'])
        if isground and hi[2]<1.5:
            vs=[o.matrix_world@v.co for v in o.data.vertices]
            ground.append(BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons]))
    patios=[]
    if not coast:
        for x in (42,67,87,-5):
            geometry_box(batch,'Cafe_Patio',(x,-27,.225),(4,4,.45),stone); patios.append((x-2,x+2,-29,-25,.45)); log['patios']+=1
    def height(x,y):
        h=0.0
        for tree in ground:
            p,n,idx,dist=tree.ray_cast(Vector((x,y,2)),Vector((0,0,-1)),3)
            if p is not None: h=max(h,p.z)
        for a,b,d,e,z in patios:
            if a<=x<=b and d<=y<=e: h=max(h,z)
        return h
    def road(x,y,r):
        if -52-r<y<-36+r: return True
        if y>-44-r and (abs(x)>94-r or y>94-r): return True
        if not coast and (abs(x)>94-r or abs(y)>94-r): return True
        if y>-44-r and 20-r<x<30+r: return True
        if x>30-r and 27-r<y<37+r: return True
        if abs(x)>89-r and abs(y)>89-r and y>0:
            dx=max(0,abs(x)-89); dy=max(0,abs(y)-89)
            if dx*dx+dy*dy>(5-r)**2: return True
        return False
    occupied=[]
    def valid(x,y,r):
        if road(x,y,r) or abs(x)>98-r or abs(y)>98-r: return False
        for a,b,d,e in footprints:
            if a-r<x<b+r and d-r<y<e+r: return False
        for a,b,rr in occupied:
            if (x-a)**2+(y-b)**2<(r+rr+.2)**2: return False
        return True
    def place(root,r):
        x,y,z=root
        options=[]
        for dx in range(-36,37):
            for dy in range(-36,37): options.append((dx*dx+dy*dy,dx,dy))
        options.sort()
        for score,dx,dy in options:
            if valid(x+dx,y+dy,r):
                occupied.append((x+dx,y+dy,r))
                return (x+dx,y+dy,height(x+dx,y+dy)-.015)
        raise RuntimeError('No safe vegetation position '+str(root))
    families=[('Palms_Trunks',320,16,('Palms_',),4.5),('Trees_Trunks',32,16,('Trees_',),3.25),('GardenTrees',212,16,('GardenTrees','GardenLeaves'),2.6),('Park_Trunks',8,4,('Park_Trunks','Park_Foliage'),2.9),('Planter_Edges',8,4,('Planter_','Shrubs__'),2.4)]
    for trunk_prefix,step,nbase,prefixes,radius in families:
        trunks=[o for name,o in originals.items() if name.startswith(trunk_prefix)]
        if not trunks: continue
        roots=root_list(trunks[0],step,nbase)
        dest=[place(r,radius) for r in roots]
        for old,new in zip(roots,dest): log['vegetation'].append({'family':trunk_prefix,'from':old,'to':new,'road_clearance_m':radius})
        for name,old in originals.items():
            if not name.startswith(prefixes): continue
            groups=components(old); obj=private(name)
            for ids in groups:
                lo,hi=bounds(old,ids); x=(lo[0]+hi[0])/2; y=(lo[1]+hi[1])/2; k=nearest(x,y,roots)
                delta=Vector(dest[k])-Vector(roots[k])
                localdelta=obj.matrix_world.inverted().to_3x3()@delta
                for i in ids: obj.data.vertices[i].co+=localdelta
            obj.data.update()
    # Roof slats were missing their two load-bearing longitudinal beams.
    for name,o in originals.items():
        if '_Pergola__' not in name: continue
        for ids in parts(o,136):
            post_ids=ids[:64]; lo,hi=bounds(o,post_ids)
            for y in (lo[1]+.06,hi[1]-.06):
                geometry_box(batch,'Pergola_Beams',((lo[0]+hi[0])/2,y,hi[2]-.06),(hi[0]-lo[0]+.12,.18,.20),wood); log['pergola_beams']+=1
    # Feet connect elevated seat frames to their actual paving/sand/grass surface.
    for name,o in originals.items():
        if not any(t in name for t in ['Loungers_Frame__','Pool_Loungers__IP_Teak','Park_Benches__IP_Teak','Restaurant_Seats__','Cafe_Seats__']): continue
        for ids in parts(o,8):
            lo,hi=bounds(o,ids)
            if hi[2]-lo[2]>.25: continue
            for x in (lo[0]+.09,hi[0]-.09):
                for y in (lo[1]+.09,hi[1]-.09):
                    z=height(x,y)-.01; top=lo[2]+.025
                    if top>z:
                        geometry_box(batch,'Furniture_Feet',(x,y,(z+top)/2),(.075,.075,top-z),metal); log['support_legs']+=1
    # Weighted umbrella bases meet the deck or sand.
    for name,o in originals.items():
        if not name.startswith('Parasols_Pole'): continue
        for ids in components(o):
            lo,hi=bounds(o,ids); x=(lo[0]+hi[0])/2; y=(lo[1]+hi[1])/2; z=height(x,y)
            top=max(z+.09,lo[2]+.03)
            geometry_box(batch,'Umbrella_Weighted_Base',(x,y,(z+top)/2),(.44,.44,top-z),stone)
    flush(batch,c)
    for ob in s.objects:
        if ob.instance_collection==src: ob.instance_collection=c
    report[src.name]=log
    print(src.name,'vegetation',len(log['vegetation']),'feet',log['support_legs'],'beams',log['pergola_beams'])

# Map-wide park benches are not part of a sector prototype.
root=bpy.data.collections['MAP_2000x1000_COMERCIO']; extra=bpy.data.collections.new('GROUNDED_WORLD_SUPPORTS'); root.children.link(extra); batch={}
for o in list(s.objects):
    if 'North_Park_Benches__' in o.name and o.type=='MESH':
        for ids in parts(o,8):
            lo,hi=bounds(o,ids)
            for x in (lo[0]+.12,hi[0]-.12):
                for y in (lo[1]+.1,hi[1]-.1): geometry_box(batch,'North_Park_Bench_Feet',(x,y,(.425+lo[2]+.02)/2),(.09,.09,lo[2]+.02-.425),metal)
flush(batch,extra)
s['grounding_pass_v1']=True
s['grounding_audit_json']=json.dumps(report)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Comercio_Ruas_Corrigido.blend')
print('SAVED corrected 2000x1000 scene; previous .blend preserved')
