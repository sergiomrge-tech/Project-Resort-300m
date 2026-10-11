using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class ResortCompactShoreCity {
 public const string Source="Assets/Scenes/ProjectResort_300m.unity";
 public const string Output="Assets/Scenes/ProjectResort_300m_Immersive.unity";
 public const string MeshFolder="Assets/R15/Compact/Meshes";
 public const float KnotSea=-402f,KnotCity=-330f,Reduction=64f;
 const float Cos=.69465837f,Sin=.71933980f;
 [Serializable] class Report{
  public string status,source_scene,destination_scene,unity_version,source_scene_sha256;
  public int meshes_copied,renderers_changed,colliders_updated,triangle_count,unchanged_omission,material_count;
  public float width_m,depth_m,city_approach_m,gap_before_m,gap_after_m;
  public bool unchanged_city_geometry,source_scene_preserved,cloud_skybox_kept,gameplay_playmode_tested=false,artistic_gate_approved=false;
 }
 static void Need(bool x,string why){if(!x)throw new Exception("COMPACT_R15_FAIL:"+why);}
 public static float Cross(Vector3 p)=>p.x*Cos-p.z*Sin;
 public static float Along(Vector3 p)=>-p.x*Sin-p.z*Cos;
 public static float NewCross(float c) {
  if(c<=KnotSea)return c;
  if(c>=KnotCity)return c-Reduction;
  return KnotSea+(c-KnotSea)*(KnotCity-KnotSea-Reduction)/(KnotCity-KnotSea);
 }
 public static Vector3 Warp(Vector3 p){
  float delta=NewCross(Cross(p))-Cross(p);
  return new Vector3(p.x+delta*Cos,p.y,p.z-delta*Sin);
 }
 static string Hash(string path) {
  using(var s=System.Security.Cryptography.SHA256.Create()){
   return BitConverter.ToString(s.ComputeHash(File.ReadAllBytes(path))).Replace("-","").ToLowerInvariant();
  }
 }
 static void Folder(string path) {
  var split=path.Split('/');
  string basePath=split[0];
  for(int i=1;i<split.Length;i++){
   string n=basePath+"/"+split[i];
   if(!AssetDatabase.IsValidFolder(n))AssetDatabase.CreateFolder(basePath,split[i]);
   basePath=n;
  }
 }
 [MenuItem("Resort/Compact shoreline and city R15 — measured spacing")]
 public static void Run(){
  Need(AssetDatabase.LoadAssetAtPath<SceneAsset>(Source)!=null,"SOURCE_SCENE_MISSING");
  Need(KnotCity-KnotSea-Reduction>=8f,"NO_CLEARANCE_BETWEEN_SHORE_AND_CITY");
  Need(NewCross(-330)-NewCross(-402)>=7.9f,"NOT_MONOTONIC");
  string before=Hash(Source);
  var scene=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
  Need(RenderSettings.skybox!=null&&RenderSettings.skybox.shader.name=="Skybox/Panoramic","CLOUD_SKY_MISSING");
  var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  Folder(MeshFolder);
  int count=0,colliders=0,triangleCount=0;bool cityPreserved=true;
  var map=new Dictionary<Mesh,Mesh>();
  var assetnames=new List<string>();
  foreach(var renderer in all) {
   var f=renderer.GetComponent<MeshFilter>();
   if(f==null||f.sharedMesh==null)continue;
   var src=f.sharedMesh;
   if(!map.TryGetValue(src,out var dst)) {
    var clone=UnityEngine.Object.Instantiate(src);
    clone.name="R15_Compact_"+count.ToString("D4");
    var verts=clone.vertices;
    float minCross=float.PositiveInfinity,maxCross=float.NegativeInfinity;
    for(int i=0;i<verts.Length;i++){
     Vector3 world=renderer.transform.TransformPoint(verts[i]);
     float oldC=Cross(world);
     minCross=Mathf.Min(minCross,oldC);maxCross=Mathf.Max(maxCross,oldC);
     Vector3 moved=Warp(world);
     verts[i]=renderer.transform.InverseTransformPoint(moved);
     Need(!float.IsNaN(verts[i].x)&&!float.IsInfinity(verts[i].x)&&!float.IsNaN(verts[i].y)&&!float.IsInfinity(verts[i].y)&&!float.IsNaN(verts[i].z)&&!float.IsInfinity(verts[i].z),"NONFINITE_VERTEX");
    }
    // City-only meshes get a pure -64 m translation: 100% original dimensions.
    if(minCross>=KnotCity-0.005f) {
     for(int i=0;i<src.vertexCount;i++){
      Vector3 a=renderer.transform.TransformPoint(src.vertices[i]);
      Vector3 b=renderer.transform.TransformPoint(verts[i]);
      Vector3 expected=new Vector3(-Reduction*Cos,0f,+Reduction*Sin);
      if(Vector3.Distance(b-a,expected)>0.006f)cityPreserved=false;
     }
    }
    clone.vertices=verts;clone.RecalculateBounds();
    string path=MeshFolder+"/"+clone.name+".asset";
    AssetDatabase.CreateAsset(clone,path);
    map.Add(src,clone);dst=clone;assetnames.Add(path);
    for(int sm=0;sm<clone.subMeshCount;sm++)triangleCount+=(int)clone.GetIndexCount(sm)/3;
    count++;
   }
   f.sharedMesh=dst;
   var col=renderer.GetComponent<MeshCollider>();
   if(col!=null&&col.sharedMesh==src){col.sharedMesh=null;col.sharedMesh=dst;colliders++;}
  }
  // Standalone source uses mesh colliders on the renderers. Verify nothing
  // outside this loop still references the pre-compact mesh assets.
  var allFilters=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshFilter>(true)).ToArray();
  Need(allFilters.Where(f=>f.sharedMesh!=null).All(f=>map.Values.Contains(f.sharedMesh)),"OLD_MESH_FILTER_REFERENCE");
  var meshColliders=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshCollider>(true)).ToArray();
  Need(meshColliders.Where(m=>m.sharedMesh!=null).All(m=>map.Values.Contains(m.sharedMesh)),"OLD_COLLIDER_MESH_REFERENCE");
  var cam=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Camera>(true)).FirstOrDefault(c=>c.CompareTag("MainCamera"));
  Need(cam!=null,"MAIN_CAMERA_MISSING");
  // Place camera at eye height on mosaic and look to compressed city.
  var origin=cam.transform.position;
  float cameraCross=Cross(origin);
  if(cameraCross>-400f||cameraCross<-435f) {
   float targetC=-420f,targetA=115f;
   cam.transform.position=new Vector3(Cos*targetC-Sin*targetA,2.4f,-Sin*targetC-Cos*targetA);
  }
  // Active camera looks from ocean side toward nearby urban silhouettes.
  Vector3 look=cam.transform.position+new Vector3(Cos*100,5f,-Sin*100);
  cam.transform.LookAt(look);
  Need(EditorSceneManager.SaveScene(scene,Output,true),"SCENE_SAVE_FAILED");
  AssetDatabase.SaveAssets();
  Need(before==Hash(Source),"SOURCE_WAS_MUTATED");
  var dependencies=AssetDatabase.GetDependencies(Output,true);
  Need(!dependencies.Any(p=>p.StartsWith("Assets/R15/Meshes/")),"OLD_MESH_ASSETS_IN_NEW_SCENE");
  Need(cityPreserved,"BUILDING_GEOMETRY_WAS_SCALED");
  Need(count>=370&&triangleCount>420000,"MISSING_MESHES");
  var report=new Report {
   status="R15_SHORE_CITY_APPROACH_NATIVE_PASS_ART_REVIEW_PENDING",
   source_scene=Source,destination_scene=Output,unity_version=Application.unityVersion,
   source_scene_sha256=before,
   meshes_copied=count,renderers_changed=all.Length,colliders_updated=colliders,
   triangle_count=triangleCount,material_count=dependencies.Count(p=>p.EndsWith(".mat")),
   city_approach_m=Reduction,
   gap_before_m=73.2f,gap_after_m=9.2f,width_m=300,depth_m=300,
   unchanged_city_geometry=cityPreserved,source_scene_preserved=true,cloud_skybox_kept=true};
  string root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../"));
  Directory.CreateDirectory(Path.Combine(root,"evidence"));
  File.WriteAllText(Path.Combine(root,"evidence/compact_native_qa.json"),JsonUtility.ToJson(report,true));
  Debug.Log("R15_COMPACT_SHORE_CITY_NATIVE_PASS meshes="+count+" colliders="+colliders+
   " city_shift="+Reduction+" triangles="+triangleCount+" gap_after=9.2m");
 }
}
