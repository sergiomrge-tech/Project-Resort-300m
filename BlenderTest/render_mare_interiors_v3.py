import bpy,json
OUT='D:/ProjectResort_300m_CompactPass/BlenderTest/'
gpu=False
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='OPTIX'
    gpu=any(d.use for d in prefs.devices)
    print('RENDER_DEVICES '+str([(d.name,d.type,d.use) for d in prefs.devices]))
except Exception as error:print('GPU unavailable, using CPU: '+str(error))
jobs=[
 ('lobby','INTERIOR_CAMERA_LOBBY',['UNIDA_06_HOTEL_SIMPLES','INTERIOR_06_LOBBY','INTERIOR_06_PUBLIC_WASHROOMS','INTERIOR_06_ADMINISTRATION']),
 ('quarto','INTERIOR_CAMERA_ROOM',['UNIDA_06_HOTEL_SIMPLES','INTERIOR_06_QUARTOS_HOTEL']),
 ('restaurante','INTERIOR_CAMERA_RESTAURANT',['UNIDA_06_RESTAURANTE_NOS_FUNDOS','INTERIOR_06_REAR_RESTAURANT_INTERIOR','UNIDA_RESTAURANT_REAR_ROOF']),
 ('cozinha','INTERIOR_CAMERA_KITCHEN',['UNIDA_06_RESTAURANTE_NOS_FUNDOS','INTERIOR_06_REAR_RESTAURANT_INTERIOR','UNIDA_RESTAURANT_REAR_ROOF']),
 ('spa','INTERIOR_CAMERA_SPA',['UNIDA_14_SPA_ANEXADO','INTERIOR_14_SPA_INTERIOR']),
 ('lavanderia','INTERIOR_CAMERA_LAUNDRY',['UNIDA_18_LAVANDERIA_E_RECURSOS','INTERIOR_18_SERVICE_INTERIOR'])]
metrics=[]
for name,camera,collections in jobs:
    s=bpy.data.scenes.new('INSPECAO_INTERIOR_'+name.upper());s.world=bpy.data.worlds['MARE_World_01']
    s.collection.children.link(bpy.data.collections['UNIDA_ORLA_CONTINUA'])
    for col in collections:s.collection.children.link(bpy.data.collections[col])
    bpy.context.window.scene=s;s.camera=bpy.data.objects[camera];s.render.engine='CYCLES';s.cycles.device='GPU' if gpu else 'CPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.max_bounces=8;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=6;s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False
    s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=OUT+'interior_v3_'+name+'.png'
    bpy.ops.render.render(write_still=True);metrics.append({'sector':name,'camera':camera,'included_collections':collections,'image':s.render.filepath,'resolution':[1600,900],'engine':'Cycles','device':s.cycles.device,'scope':'isolated sector inspection of real saved assets, not a Unity gameplay capture'})
from pathlib import Path
(Path(OUT)/'mare_interiors_render_evidence_v3.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print('SIX_REAL_INTERIOR_RENDERS_COMPLETE')
