# Project Resort v7 - selective Blender -> Unity export. Keeps the original 2x1 km meshes untouched.
import bpy, json, struct, numpy as np
from pathlib import Path
from mathutils import Matrix
ROOT = Path('D:/ProjectResort_300m_CompactPass/BlenderTest/CityHousesUnityV7')
ROOT.mkdir(parents=True, exist_ok=True)
C = Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
city = bpy.data.collections['MAIN_CITY_WITH_MARE_LOT']
dg = bpy.context.evaluated_depsgraph_get()
names = []
lookup = {}
def matid(mat):
    name = mat.name if mat else 'IP_Limestone'
    if name not in lookup:
        lookup[name] = len(names)
        names.append({'name': name, 'color': list(mat.diffuse_color) if mat else [0.8,0.8,0.8,1]})
    return lookup[name]
def convert_collection(coll, output, only_v7=False):
    verts, submeshes, tri_count = [], {}, 0
    objects = sorted(coll.objects, key=lambda o:o.name)
    for ob in objects:
        if ob.type not in ('MESH','CURVE','FONT') or ob.hide_render: continue
        if only_v7 and (not ob.name.startswith('V7_') or ob.name.startswith('V7_PRESERVED_')): continue
        ev = ob.evaluated_get(dg)
        mesh = ev.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
        if mesh is None:continue
        try:
            if len(mesh.polygons)==0: continue
            mesh.calc_loop_triangles()
            count=len(mesh.loops)
            if count==0:continue
            xyz=np.empty(len(mesh.vertices)*3,np.float32)
            mesh.vertices.foreach_get('co',xyz)
            xyz=xyz.reshape(-1,3)
            matrix=np.array(ob.matrix_local,dtype=np.float64)
            xyz=(xyz@matrix[:3,:3].T+matrix[:3,3]).astype(np.float32)
            coords=np.empty(count,np.int32);mesh.loops.foreach_get('vertex_index',coords)
            pos=xyz[coords][:,[0,2,1]]
            norm=np.empty((count,3),np.float32)
            mesh.corner_normals.foreach_get('vector',norm.ravel())
            normalmat=np.linalg.inv(matrix[:3,:3]).T
            norm=norm@normalmat.T
            norm=norm/(np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-6))
            norm=norm[:,[0,2,1]].astype(np.float32)
            uv=np.zeros((count,2),np.float32)
            layer=mesh.uv_layers.active or (mesh.uv_layers[0] if mesh.uv_layers else None)
            if layer:layer.data.foreach_get('uv',uv.ravel())
            mat=ob.material_slots[0].material if ob.material_slots else None
            if mat is not None:uv/=max(0.1,float(mat.get('tile_width_m',1.0)))
            data=np.concatenate([pos,norm,uv],axis=1).astype('<f4')
            offset=sum(len(block) for block in verts)
            verts.append(data)
            for tri in mesh.loop_triangles:
                index=tri.material_index
                m=mesh.materials[index] if index<len(mesh.materials) else mat
                key=matid(m)
                submeshes.setdefault(key,[]).extend((offset+tri.loops[0],offset+tri.loops[2],offset+tri.loops[1]))
                tri_count+=1
        finally:
            ev.to_mesh_clear()
    if not verts:
        raise RuntimeError('Empty mesh for '+coll.name)
    array=np.concatenate(verts)
    if len(array)>2000000:raise RuntimeError('Too many loop vertices '+coll.name+' '+str(len(array)))
    with (ROOT/output).open('wb') as f:
        f.write(struct.pack('<III',0x3452534d,len(array),len(submeshes)))
        f.write(array.tobytes())
        for index,inds in sorted(submeshes.items()):
            f.write(struct.pack('<II',index,len(inds)))
            f.write(np.asarray(inds,dtype='<i4').tobytes())
    return {'name':coll.name, 'file':output,'vertices':int(len(array)),'triangles':tri_count,'materials':len(submeshes)}
templates=[]
for c in sorted((c for c in bpy.data.collections if c.name.startswith('V7_HOME_')),key=lambda c:c.name):
    templates.append(convert_collection(c,'template_%02d.meshbin'%len(templates)))
districts=[]
for c in sorted((c for c in bpy.data.collections if c.name.startswith(('V7_HOUSES_DISTRICT_','V7_COAST_BUILDINGS_HOUSES_'))),key=lambda c:c.name):
    districts.append(convert_collection(c,'district_%02d.meshbin'%len(districts),only_v7=True))
sector_data=[]
for ob in city.objects:
    if not ob.name.startswith('V7_') or ob.instance_type!='COLLECTION' or not ob.instance_collection:
        continue
    coll=ob.instance_collection
    if not coll.name.startswith(('V7_HOUSES_DISTRICT_','V7_COAST_BUILDINGS_HOUSES_')):continue
    sector_data.append({'old_name':ob.name[3:],'district':coll.name,
                        'x':float(ob.location.x),'z':float(ob.location.y),
                        'rotation_y':float(-ob.rotation_euler.z)})
lots={}
for d in districts:
    c=bpy.data.collections[d['name']]
    lots[c.name]=[]
    for ob in c.objects:
        if ob.instance_type=='COLLECTION' and ob.instance_collection and ob.instance_collection.name.startswith('V7_HOME_'):
            lots[c.name].append({'template':ob.instance_collection.name,'x':float(ob.location.x),
                                 'z':float(ob.location.y),'rotation_y':float(-ob.rotation_euler.z)})
    assert len(lots[c.name])>=10, (c.name,len(lots[c.name]))
out={'version':7,'map_width':2000,'map_depth':1000,
     'materials':names,'templates':templates,'districts':districts,'sectors':sector_data,'lots_by_district':lots,
     'source_blend':'Resort_Main_Map_Mare_Houses_v7.blend',
     'city_pool_removal':True, 'original_coastline_buildings_preserved':True}
print("V7_PRECHECK",len(templates),len(districts),len(sector_data),[(s["old_name"],s["district"]) for s in sector_data[:3]],flush=True)
assert len(templates)>=15 and len(districts)==4 and len(sector_data)==40,(len(templates),len(districts),len(sector_data))
assert sum(len(lots[s['district']]) for s in sector_data)==1132
(ROOT/'city_houses_export.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('CITY_V7_EXPORT_PASS',json.dumps({'templates':len(templates),'district_meshes':len(districts),
 'sector_instances':len(sector_data),'houses':1132,'materials':len(names),
 'bytes':sum(p.stat().st_size for p in ROOT.glob('*.meshbin'))}),flush=True)
