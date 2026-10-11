import bpy,json
from pathlib import Path
s=bpy.context.scene;o=bpy.data.objects['CRISTO_REDENTOR_38m_Detailed_Artist_Mesh']
sectors=[x for x in s.objects if x.instance_collection and x.instance_collection.name.endswith('CONNECTED_ROADS_GROUNDED')]
images=[i for i in bpy.data.images if i.source=='FILE']
land=bpy.data.collections['RIO_MOUNTAINS_AND_FOREST'];forest=sum(1 for x in land.objects if x.instance_collection and x.instance_collection.name=='RIO_FOREST_TREE_SOURCE')
r={'file':bpy.data.filepath,'engine':s.render.engine,'city_dimensions_m':list(bpy.data.objects['SITE_2000x1000_METERS'].dimensions),'city_sector_count':len(sectors),'city_scales':sorted(set(tuple(x.scale) for x in sectors)),'cristo_dimensions_m':list(o.dimensions),'cristo_vertices':len(o.data.vertices),'cristo_triangles':len(o.data.polygons),'cristo_author':o.get('author'),'cristo_license':o.get('license'),'cristo_source':o.get('source'),'forest_instances':forest,'mountains':[x.name for x in land.objects if x.type=='MESH' and x.name.endswith('_TERRAIN')],'packed_images':sum(bool(i.packed_file) for i in images),'file_images':len(images),'sidewalk_alignment':s.get('sidewalk_curve_alignment_v1'),'limitations':['Geography and mountain surfaces are artistic approximations, not surveyed GIS terrain.','No Unity integration, physics, LOD budget or FPS validation in this Blender pass.']}
Path('D:/ProjectResort_300m_CompactPass/BlenderTest/rio_delivery_validation.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print('RIO_VALIDATION',json.dumps(r))
