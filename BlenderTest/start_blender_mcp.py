import bpy, traceback
log_path = r'D:\ProjectResort_300m_CompactPass\BlenderTest\blender_mcp_start.log'
try:
    bpy.ops.preferences.addon_enable(module='blender_mcp')
    bpy.context.scene.blendermcp_port = 9876
    bpy.context.scene.blendermcp_auto_start_server = False
    bpy.ops.wm.save_userpref()
    result = bpy.ops.blendermcp.start_server()
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('result=' + repr(result) + '\\n')
        f.write('running=' + repr(bpy.context.scene.blendermcp_server_running) + '\\n')
except Exception:
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
