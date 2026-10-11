using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ResortCompactLayoutAudit {
 [Serializable] class Item {
  public string name,mesh,materials;public int vertices,triangles;
  public bool active;public float cross_min,cross_max,along_min,along_max,world_y_min,world_y_max;
 }
 [Serializable] class Report{
  public string status,unity_version,source_scene;
  public int mesh_renderers,active_renderers;public Item[] items;
 }
 static float Cross(Vector3 p)=>p.x*.69465837f-p.z*.71933980f;
 static float Along(Vector3 p)=>-p.x*.71933980f-p.z*.69465837f;
 public static void Run(){
  var s=EditorSceneManager.OpenScene("Assets/Scenes/ProjectResort_300m.unity",OpenSceneMode.Single);
  var renderers=s.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  var list=new List<Item>();
  foreach(var r in renderers){
   var f=r.GetComponent<MeshFilter>();if(f==null||f.sharedMesh==null)continue;
   var v=f.sharedMesh.vertices;if(v.Length==0)continue;
   float c0=float.MaxValue,c1=float.MinValue,a0=float.MaxValue,a1=float.MinValue,y0=float.MaxValue,y1=float.MinValue;
   foreach(var p in v){
    var q=r.transform.TransformPoint(p);float c=Cross(q),a=Along(q);
    c0=Mathf.Min(c0,c);c1=Mathf.Max(c1,c);
    a0=Mathf.Min(a0,a);a1=Mathf.Max(a1,a);
    y0=Mathf.Min(y0,q.y);y1=Mathf.Max(y1,q.y);
   }
   int tris=0;for(int sm=0;sm<f.sharedMesh.subMeshCount;sm++)tris+=(int)f.sharedMesh.GetIndexCount(sm)/3;
   list.Add(new Item{name=r.name,mesh=f.sharedMesh.name,
    materials=string.Join("|",r.sharedMaterials.Select(m=>m!=null?m.name:"MISSING")),
    vertices=v.Length,triangles=tris,active=r.enabled&&r.gameObject.activeInHierarchy,
    cross_min=c0,cross_max=c1,along_min=a0,along_max=a1,world_y_min=y0,world_y_max=y1});
  }
  var report=new Report{status="LAYOUT_AUDIT_DATA_NOT_GAMEPLAY",unity_version=Application.unityVersion,
    source_scene="Assets/Scenes/ProjectResort_300m.unity",mesh_renderers=list.Count,
    active_renderers=list.Count(x=>x.active),items=list.ToArray()};
  string outpath=Path.GetFullPath(Path.Combine(Application.dataPath,"../../evidence/layout_before.json"));
  Directory.CreateDirectory(Path.GetDirectoryName(outpath));
  File.WriteAllText(outpath,JsonUtility.ToJson(report,true));
  Debug.Log("RESORT_300M_LAYOUT_NATIVE_AUDIT_PASS active="+report.active_renderers+" total="+report.mesh_renderers+" file="+outpath);
 }
}
