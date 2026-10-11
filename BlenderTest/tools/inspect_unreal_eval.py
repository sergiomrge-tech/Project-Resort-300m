import bpy, json, os, time
from mathutils import Vector
scene=bpy.data.scenes.get('RESORT_MAIN_MARE_20') or bpy.context.scene
bpy.context.window.scene=scene if bpy.context.window else None
dg=bpy.context.evaluated_depsgraph_get()
items=[]; types={}; mats=set(); bounds=[1e30]*3+[-1e30]*3
for inst in dg.object_instances:
    ob=inst.object
    if ob.type!='MESH' or ob.hide_render: continue
    mesh=ob.evaluated_get(dg).to_mesh()
    if not mesh or not mesh.polygons:
        ob.evaluated_get(dg).to_mesh_clear(); continue
    types[ob.name]=types.get(ob.name,0)+1
    for m in mesh.materials:
        if m:mats.add(m.name)
    if len(items)<100: items.append({'name':ob.name,'inst':inst.is_instance,'verts':len(mesh.vertices),'faces':len(mesh.polygons),'loc':list(inst.matrix_world.translation)})
    co=mesh.vertices
    if len(co):
        mat=inst.matrix_world
        for vi in range(0,len(co),max(1,len(co)//1000)):
            v=co[vi]
            p=mat @ v.co
            for k in range(3): bounds[k]=min(bounds[k],p[k]);bounds[k+3]=max(bounds[k+3],p[k])
    ob.evaluated_get(dg).to_mesh_clear()
rep={'scene':scene.name,'instances_count':len(dg.object_instances),'mesh_type_counts':len(types),'sample':items,'material_count':len(mats),'materials':sorted(mats),'sampled_bounds':bounds}
out=r'D:/ProjectResort_300m_CompactPass/BlenderTest/unreal_export_eval.json'
open(out,'w',encoding='utf8').write(json.dumps(rep,ensure_ascii=False,indent=2))
print(json.dumps({k:rep[k] for k in ['scene','instances_count','mesh_type_counts','material_count','sampled_bounds']},ensure_ascii=False))
