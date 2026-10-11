import sys,time,json,pathlib
sys.path.insert(0,'D:/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution
remote=remote_execution.RemoteExecution()
remote.start()
try:
    deadline=time.time()+15
    nodes=[]
    while time.time()<deadline:
        nodes=[n for n in remote.remote_nodes if n.get('project_name')=='ProjectResortUE']
        if nodes: break
        time.sleep(0.3)
    if not nodes: raise RuntimeError('ProjectResortUE not discovered; available nodes: '+str(remote.remote_nodes))
    remote.open_command_connection(nodes[0]['node_id'])
    command=sys.argv[1] if len(sys.argv)>1 else "import unreal;print(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name())"
    result=remote.run_command(command,unattended=True,exec_mode=remote_execution.MODE_EXEC_FILE)
    print(json.dumps(result,ensure_ascii=False))
finally:
    remote.stop()
