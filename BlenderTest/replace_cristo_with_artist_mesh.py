"""Import the locally preserved, attributed CC BY 4.0 mesh into the landscape scene."""
import bpy
from mathutils import Vector
s=bpy.context.scene
if bpy.data.objects.get('CRISTO_REDENTOR_38m_Detailed_Artist_Mesh'):raise RuntimeError('Artist mesh already installed.')
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/AssetsExternal/christ_the_redeemer_parlin_sitorus.glb')
new=[o for o in bpy.data.objects if o not in before];src=next(o for o in new if o.type=='MESH')
points=[src.matrix_world@v.co for v in src.data.vertices]
lo=Vector(tuple(min(v[k] for v in points) for k in range(3)));hi=Vector(tuple(max(v[k] for v in points) for k in range(3)));factor=38/(hi.z-lo.z);centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
me=src.data.copy()
for v,p in zip(me.vertices,points):v.co=(p-centre)*factor
me.materials.clear();me.materials.append(bpy.data.materials['CRISTO_Soapstone_Mosaic']);me.update()
c=bpy.data.collections.new('CRISTO_REDEEMER_PARLIN_SITORUS_CC_BY');bpy.data.collections['MAP_2000x1000_COMERCIO'].children.link(c)
o=bpy.data.objects.new('CRISTO_REDENTOR_38m_Detailed_Artist_Mesh',me);c.objects.link(o);o.location=(-350,1650,704)
o['author']='Parlin Sitorus';o['source']='https://sketchfab.com/3d-models/christ-the-redeemer-cristo-redentor-157dbdb9d8654651a5e5c9af7b412398';o['license']='Creative Commons Attribution 4.0 — verified Sketchfab model API';o['changes']='scaled to 38m total height, soapstone material and adapted Corcovado placement'
for p in me.polygons:p.use_smooth=True
for old in bpy.data.collections['CRISTO_REDENTOR_DETAILED'].objects:
    if not old.name.startswith('Mirante_'):old.hide_render=True;old.hide_set(True)
for imported in new:imported.hide_render=True;imported.hide_set(True)
bpy.context.view_layer.update()
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Rio_Cristo_Montanhas_Vegetacao_v2.blend')
