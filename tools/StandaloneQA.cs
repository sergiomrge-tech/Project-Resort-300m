using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class StandaloneQA {
 const string Scene="Assets/Scenes/ProjectResort_300m.unity";
 static string Output { get {
  var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-qaOutput");
  return i>=0?Path.GetFullPath(args[i+1]):Path.GetFullPath(Path.Combine(Application.dataPath,"../../evidence"));
 }}
 [Serializable] public class Shot {public string filename,sha256;public Vector3 position,target;public int width=1600,height=900;public float fov=57;public int pixel_span;public int magenta_pixels;}
 [Serializable] public class Report {
  public string status,unity_version,gpu,renderer,scene_sha256,utc;
  public string[] dependencies,package_dependencies;
  public int objects,renderers,active_renderers,meshes,materials,textures,mesh_colliders,box_colliders,triangles,active_triangles,missing_scripts;
  public float width_m=300,depth_m=300,units_per_meter=1,min_crop_x=-510,max_crop_x=-210,min_crop_y=-40,max_crop_y=260;
  public float min_observed_x,max_observed_x,min_observed_y,max_observed_y;
  public bool skybox_assigned,player_tested=false,playmode_tested=false,npc_tested=false,saves_tested=false,fps_measured=false,art_approved=false;
  public int ground_rays,ground_hits;
  public Shot[] captures;
 }
 static void Need(bool good,string why){if(!good)throw new Exception("STANDALONE_QA_FAILED: "+why);}
 static Vector3 W(float x,float y,float h)=>new Vector3(.69465837f*x-.71933980f*y,h,-.71933980f*x-.69465837f*y);
 static string Sha(string p){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(p))).Replace("-","").ToLowerInvariant();}
 static Shot Render(Camera c,Vector3 pos,Vector3 target,string file){
  c.transform.position=pos;c.transform.LookAt(target);c.fieldOfView=57;c.clearFlags=CameraClearFlags.Skybox;
  var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);rt.Create();var saved=c.targetTexture;var active=RenderTexture.active;c.targetTexture=rt;
  var request=new UniversalRenderPipeline.SingleCameraRequest{destination=rt};Need(RenderPipeline.SupportsRenderRequest(c,request),"URP render request unsupported");
  for(int i=0;i<5;i++)RenderPipeline.SubmitRenderRequest(c,request);
  RenderTexture.active=rt;var image=new Texture2D(1600,900,TextureFormat.RGB24,false);image.ReadPixels(new Rect(0,0,1600,900),0,0);image.Apply();
  var pixels=image.GetPixels32();int span=pixels.Max(p=>p.r+p.g+p.b)-pixels.Min(p=>p.r+p.g+p.b);int magenta=pixels.Count(p=>p.r>220&&p.b>220&&p.g<50);
  string path=Path.Combine(Output,file);File.WriteAllBytes(path,image.EncodeToPNG());Need(span>75&&new FileInfo(path).Length>50000,"Empty capture");Need(magenta<1440,"Pink shader fallback");
  c.targetTexture=saved;RenderTexture.active=active;rt.Release();UnityEngine.Object.DestroyImmediate(rt);UnityEngine.Object.DestroyImmediate(image);
  Debug.Log("STANDALONE_REAL_GPU_FRAME "+file+" SHA256="+Sha(path));
  return new Shot{filename=file,sha256=Sha(path),position=pos,target=target,pixel_span=span,magenta_pixels=magenta};
 }
 public static void Run(){
  Directory.CreateDirectory(Output);
  // Rename historical lowercase texture labels, preserving their .meta GUIDs.
  foreach(var p in AssetDatabase.GetAllAssetPaths().Where(p=>p.StartsWith("Assets/R15/")&&!AssetDatabase.IsValidFolder(p)).ToArray()){
   string name=Path.GetFileNameWithoutExtension(p),clean=Regex.Replace(name,@"(?i)r(?:[1-9]|1[0-4])_","");
   if(clean!=name)Need(string.IsNullOrEmpty(AssetDatabase.RenameAsset(p,clean)),"Asset rename failed "+p);
  }
  AssetDatabase.SaveAssets();
  var scene=EditorSceneManager.OpenScene(Scene,OpenSceneMode.Single);
  var objects=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Select(t=>t.gameObject).ToArray();
  var rs=objects.SelectMany(g=>g.GetComponents<MeshRenderer>()).ToArray();Need(rs.Length==380,"Renderer count "+rs.Length);
  var materials=rs.SelectMany(r=>r.sharedMaterials).Concat(new[]{RenderSettings.skybox}).Distinct().ToArray();
  foreach(var m in materials){Need(m!=null,"Missing material");Need(m.shader!=null&&m.shader.isSupported&&!ShaderUtil.ShaderHasError(m.shader),"Bad shader "+m.name);Need(AssetDatabase.GetAssetPath(m).StartsWith("Assets/R15/"),"Nonlocal material");}
  var meshes=rs.Select(r=>r.GetComponent<MeshFilter>().sharedMesh).Distinct().ToArray();Need(meshes.All(m=>m!=null&&AssetDatabase.GetAssetPath(m).StartsWith("Assets/R15/")),"Nonlocal mesh");
  var q=new Report{status="STANDALONE_IMPORT_AND_REAL_GPU_PASS_ART_PENDING",utc=DateTime.UtcNow.ToString("o"),unity_version=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,renderer=SystemInfo.graphicsDeviceType.ToString(),scene_sha256=Sha(Scene),objects=objects.Length,renderers=rs.Length,meshes=meshes.Length,materials=materials.Length,mesh_colliders=objects.Sum(g=>g.GetComponents<MeshCollider>().Length),box_colliders=objects.Sum(g=>g.GetComponents<BoxCollider>().Length),missing_scripts=objects.Sum(g=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(g)),skybox_assigned=RenderSettings.skybox!=null};
  Need(q.missing_scripts==0&&q.skybox_assigned,"Missing component or sky");
  q.active_renderers=rs.Count(r=>r.enabled&&r.gameObject.activeInHierarchy);
  Need(q.renderer=="Direct3D11"&&q.unity_version=="6000.6.2f1","Wrong Unity or graphics API");
  var paths=AssetDatabase.GetDependencies(new[]{Scene,AssetDatabase.GetAssetPath(GraphicsSettings.defaultRenderPipeline)},true).Distinct().OrderBy(p=>p).ToArray();
  q.dependencies=paths.Where(p=>p.StartsWith("Assets/")).ToArray();q.package_dependencies=paths.Where(p=>!p.StartsWith("Assets/")).ToArray();
  Need(q.dependencies.All(p=>p==Scene||p.StartsWith("Assets/R15/")),"Legacy dependency");
  var guidRows=new List<string>{"guid\tpath"};
  foreach(var file in Directory.GetFiles("Assets","*",SearchOption.AllDirectories).Concat(Directory.GetFiles("ProjectSettings","*",SearchOption.AllDirectories))){
   if(file.EndsWith(".meta"))continue;string text=File.ReadAllText(file);
   foreach(Match match in Regex.Matches(text,@"guid: ([a-f0-9]{32})")){
    string guid=match.Groups[1].Value;if(guid.StartsWith("0000000000000000"))continue;
    string resolved=AssetDatabase.GUIDToAssetPath(guid);Need(!string.IsNullOrEmpty(resolved),"Unresolved GUID "+guid+" in "+file);
    Need(resolved.StartsWith("Packages/")||resolved.StartsWith("Assets/R15/")||resolved==Scene,"Legacy GUID "+resolved+" in "+file);
    guidRows.Add(guid+"\t"+resolved);
   }
  }
  File.WriteAllLines(Path.Combine(Output,"guid_resolution.tsv"),guidRows.Distinct().OrderBy(x=>x));
  q.textures=materials.SelectMany(m=>m.GetTexturePropertyNames().Select(p=>m.GetTexture(p))).Where(t=>t!=null).Distinct().Count();
  q.min_observed_x=q.min_observed_y=float.MaxValue;q.max_observed_x=q.max_observed_y=float.MinValue;
  foreach(var r in rs){Need(r.transform.localScale==Vector3.one,"Scaled geometry");var mesh=r.GetComponent<MeshFilter>().sharedMesh;
   foreach(var v in mesh.vertices){var p=r.transform.TransformPoint(v);float x=p.x*.69465837f-p.z*.71933980f,y=-p.x*.71933980f-p.z*.69465837f;q.min_observed_x=Mathf.Min(q.min_observed_x,x);q.max_observed_x=Mathf.Max(q.max_observed_x,x);q.min_observed_y=Mathf.Min(q.min_observed_y,y);q.max_observed_y=Mathf.Max(q.max_observed_y,y);Need(x>=-510.02f&&x<=-209.98f&&y>=-40.02f&&y<=260.02f,"Outside crop");}
   for(int sm=0;sm<mesh.subMeshCount;sm++){int count=(int)mesh.GetIndexCount(sm)/3;q.triangles+=count;if(r.enabled&&r.gameObject.activeInHierarchy)q.active_triangles+=count;}
  }
  Physics.SyncTransforms();foreach(float y in new[]{30f,70f,110f,150f,190f,230f})foreach(float x in new[]{-412f,-400f,-390f}){q.ground_rays++;if(Physics.Raycast(W(x,y,100),Vector3.down,out var hit,150)&&hit.collider is MeshCollider)q.ground_hits++;}
  Need(q.ground_hits>0,"No solid clipped ground");
  var c=Camera.main;Need(c!=null,"No camera");var shots=new List<Shot>();
  shots.Add(Render(c,W(-412.3f,72.44f,1.65f),W(-411,142.43f,3.8f),"R15_01_CoastWalk_CloudyDay_RealUnity.png"));
  shots.Add(Render(c,W(-412,128,2.4f),W(-510,155,14),"R15_02_Clouds_Over_Beach_RealUnity.png"));
  shots.Add(Render(c,W(-390,113,1.65f),W(-350,114,4.5f),"R15_03_CompactCity_Clouds_RealUnity.png"));
  shots.Add(Render(c,W(-360,110,230),W(-360,110,0),"R15_04_300m_Cropped_Aerial_RealUnity.png"));
  q.captures=shots.ToArray();File.WriteAllText(Path.Combine(Output,"standalone_qa.json"),JsonUtility.ToJson(q,true));
  Debug.Log("STANDALONE_IMPORT_GPU_PASS renderers="+q.renderers+" triangles="+q.triangles+" dependencies="+q.dependencies.Length+" ground="+q.ground_hits+"/"+q.ground_rays);
 }
}
