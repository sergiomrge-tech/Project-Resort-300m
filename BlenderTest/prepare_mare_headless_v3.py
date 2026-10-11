import bpy
c=bpy.data.collections['INTERIOR_06_REAR_RESTAURANT_INTERIOR']
for o in list(c.objects):
    if any(t in o.name for t in ['Dining_','Plate','Water_Glass','Napkin','Knife','Table_Vase']) and 1.7<abs(o.location.x)<4.0:bpy.data.objects.remove(o,do_unlink=True)
for cname in ['UNIDA_04_RESTAURANTE_TRANSFORMADO','UNIDA_06_RESTAURANTE_NOS_FUNDOS']:
    for o in bpy.data.collections[cname].objects:
        if '_Floor' in o.name and o.type=='MESH':o.data.materials[0]=bpy.data.materials['INTERIOR_Travertine_Honed']
print('HEADLESS_REPAIR_PREPARED')
