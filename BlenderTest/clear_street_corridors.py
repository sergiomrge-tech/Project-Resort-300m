import bpy
s=bpy.context.scene
collections={o.instance_collection.name:o.instance_collection for o in s.objects if o.instance_type=='COLLECTION'}
surface_names=('Urban_Sidewalk__','Street_Sidewalk__','Curb__','Inland_Garden__','Park_Path__','Park_CrossPath__','Praca_Garden__','Praca_CrossPath__','Praca_PerimeterPath__','Promenade__','Promenade_Joints__','Promenade_Mosaic__','Cycleway__')
updated=0
for name,col in collections.items():
    coastal='COAST' in name
    for ob in list(col.objects):
        if ob.type!='MESH' or not ob.name.startswith(surface_names): continue
        if coastal and ob.name.startswith(('Promenade','Cycleway')): continue
        me=ob.data
        if len(me.vertices)%8: continue
        verts=[]; faces=[]
        for start in range(0,len(me.vertices),8):
            points=[v.co for v in me.vertices[start:start+8]]
            x0=min(v.x for v in points); x1=max(v.x for v in points); y0=min(v.y for v in points); y1=max(v.y for v in points); z0=min(v.z for v in points); z1=max(v.z for v in points)
            # Inland edge roads occupy +/-94 to +/-100; coast streets begin at y=-44.
            if not coastal or y1>-44: x0=max(x0,-94); x1=min(x1,94)
            if not coastal: y0=max(y0,-94)
            y1=min(y1,94)
            xranges=[(x0,x1)]
            if ob.name.startswith(('Urban_Sidewalk__','Curb__')) and y1>-40 and y0<-24: xranges=[(x0,min(x1,20)),(max(x0,30),x1)]
            for lo,hi in xranges:
                if hi-lo<.005 or y1-y0<.005: continue
                off=len(verts)
                verts.extend([(lo,y0,z0),(hi,y0,z0),(hi,y1,z0),(lo,y1,z0),(lo,y0,z1),(hi,y0,z1),(hi,y1,z1),(lo,y1,z1)])
                faces.extend(tuple(i+off for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        cp=ob.copy(); cp.data=bpy.data.meshes.new(ob.name+'_ROAD_CUT'); cp.data.from_pydata(verts,[],faces)
        for m in ob.data.materials: cp.data.materials.append(m)
        cp.data.update(); uv=cp.data.uv_layers.new(name='WorldMeters')
        for p in cp.data.polygons:
            for li in p.loop_indices:
                co=cp.data.vertices[cp.data.loops[li].vertex_index].co; uv.data[li].uv=(co.x*.25,co.y*.25)
        cp.name='CLEAR_ROAD_'+ob.name; col.objects.unlink(ob); col.objects.link(cp); updated+=1

m=bpy.data.materials['ROAD_Signal_Green']; bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Emission Strength'].default_value=0
# Junction metadata remains an art inventory; signal states are static.
s['cleared_surface_assets']=updated
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Comercio_Ruas.blend')
print('CLEARED_ROAD_CORRIDORS',updated)
s.camera=bpy.data.objects['STREET_COAST_JUNCTION']; s.cycles.samples=24
s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/resort_2x1_street_coast.png'
bpy.ops.render.render(write_still=True)
print('COAST_JUNCTION_RENDERED')
