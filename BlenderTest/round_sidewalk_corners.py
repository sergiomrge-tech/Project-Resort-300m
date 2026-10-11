import bpy, math
s=bpy.context.scene
cols={o.instance_collection.name:o.instance_collection for o in s.objects if o.instance_type=='COLLECTION'}
changed=0
for col in cols.values():
    for ob in col.objects:
        if not ob.name.startswith('CLEAR_ROAD_') or ob.type!='MESH': continue
        me=ob.data
        if len(me.vertices)%8: continue
        vv=[]; ff=[]; any_round=False
        for start in range(0,len(me.vertices),8):
            p=[v.co for v in me.vertices[start:start+8]]
            x0=min(v.x for v in p); x1=max(v.x for v in p); y0=min(v.y for v in p); y1=max(v.y for v in p); z0=min(v.z for v in p); z1=max(v.z for v in p)
            urban='Urban_Sidewalk' in ob.name
            bottom=abs(y0+94)<.02 or (urban and abs(y0+36)<.02)
            top=abs(y1-94)<.02
            flags=[abs(x0+94)<.02 and bottom,abs(x1-94)<.02 and bottom,abs(x1-94)<.02 and top,abs(x0+94)<.02 and top]
            polygon=[]
            corners=[(x0,y0,180),(x1,y0,270),(x1,y1,0),(x0,y1,90)]
            for j,(x,y,a) in enumerate(corners):
                if not flags[j]: polygon.append((x,y)); continue
                any_round=True
                r=min(5,(x1-x0)*.45,(y1-y0)*(.45 if flags[0] and flags[3] else .95))
                cx=x+r if j in (0,3) else x-r; cy=y+r if j in (0,1) else y-r
                for k in range(17):
                    angle=math.radians(a+k*90/16); polygon.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
            n=len(polygon); off=len(vv)
            vv.extend((x,y,z0) for x,y in polygon); vv.extend((x,y,z1) for x,y in polygon)
            ff.append(tuple(off+i for i in reversed(range(n)))); ff.append(tuple(off+n+i for i in range(n)))
            ff.extend((off+i,off+(i+1)%n,off+(i+1)%n+n,off+i+n) for i in range(n))
        if any_round:
            mats=list(me.materials); new=bpy.data.meshes.new(ob.name+'_ROUNDED'); new.from_pydata(vv,[],ff)
            for m in mats: new.materials.append(m)
            new.update(); uv=new.uv_layers.new(name='WorldMeters')
            for poly in new.polygons:
                for li in poly.loop_indices:
                    co=new.vertices[new.loops[li].vertex_index].co; uv.data[li].uv=(co.x*.25,co.y*.25)
            ob.data=new; changed+=1
s['rounded_pavement_assets']=changed
s.camera=bpy.data.objects['STREET_COAST_JUNCTION']
bpy.ops.wm.save_as_mainfile(filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/Resort_Ipanema_2x1km_Comercio_Ruas.blend')
s.cycles.samples=20
s.render.filepath='D:/ProjectResort_300m_CompactPass/BlenderTest/resort_2x1_street_coast.png'
bpy.ops.render.render(write_still=True)
print('ROUNDED_PAVEMENTS',changed)
