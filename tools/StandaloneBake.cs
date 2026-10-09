using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Rendering.Universal;

public static class StandaloneBake {
 const string Source="Assets/Scenes/R15_Copacabana_300x300_Cloudy.unity";
 const string Dest="Assets/Scenes/ProjectResort_300m.unity";
 static string Root=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 static Dictionary<UnityEngine.Object,UnityEngine.Object> copies=new Dictionary<UnityEngine.Object,UnityEngine.Object>();
 static List<string> provenance=new List<string>();
 static int serial;
 static void Need(bool ok,string message){if(!ok)throw new Exception(message);}
 static void Folder(string path){if(AssetDatabase.IsValidFolder(path))return;Directory.CreateDirectory(path);AssetDatabase.Refresh();}
 static string Clean(string s)=>Regex.Replace(Regex.Replace(s,@"(?i)R\d+[_ ]?",""),@"[^A-Za-z0-9_]","_");
 static UnityEngine.Object Local(UnityEngine.Object obj){
  if(obj==null)return null;
  if(copies.TryGetValue(obj,out var cached))return cached;
  string src=AssetDatabase.GetAssetPath(obj);
  if(!src.StartsWith("Assets/"))return obj;
  string category=obj is Material?"Materials":obj is Texture?"Textures":obj is Shader?"Shaders":"Rendering";
  string ext=Path.GetExtension(src);if(obj is Material)ext=".mat";if(obj is ScriptableObject)ext=".asset";
  string dst="Assets/R15/"+category+"/R15_"+(serial++).ToString("D4")+"_"+Clean(obj.name)+ext;
  Folder(Path.GetDirectoryName(dst));
  UnityEngine.Object clone;
  if(obj is Material || obj is ScriptableObject){clone=UnityEngine.Object.Instantiate(obj);clone.name="R15_"+Clean(obj.name);var prior=AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(dst);if(prior!=null){EditorUtility.CopySerialized(clone,prior);UnityEngine.Object.DestroyImmediate(clone);clone=prior;}else AssetDatabase.CreateAsset(clone,dst);}
  else {if(File.Exists(dst))File.Copy(src,dst,true);else Need(AssetDatabase.CopyAsset(src,dst),"Cannot copy "+src);if(obj is Shader)File.WriteAllText(dst,Regex.Replace(File.ReadAllText(dst),@"R(?:[1-9]|1[0-4])[_/]","R15_"));AssetDatabase.ImportAsset(dst);clone=AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(dst);}
  copies[obj]=clone;
  provenance.Add(src+"\t"+dst+"\t"+AssetDatabase.AssetPathToGUID(src)+"\t"+AssetDatabase.AssetPathToGUID(dst));
  if(clone is Material mat){
   mat.shader=(Shader)Local(mat.shader);
   var so=new SerializedObject(mat);var slots=so.FindProperty("m_SavedProperties.m_TexEnvs");var valid=mat.GetTexturePropertyNames();
   for(int i=slots.arraySize-1;i>=0;i--)if(!valid.Contains(slots.GetArrayElementAtIndex(i).FindPropertyRelative("first").stringValue))slots.DeleteArrayElementAtIndex(i);
   so.ApplyModifiedPropertiesWithoutUndo();
   foreach(var prop in valid)mat.SetTexture(prop,(Texture)Local(mat.GetTexture(prop)));
  } else if(clone is ScriptableObject){
   var so=new SerializedObject(clone);var it=so.GetIterator();
   while(it.Next(true))if(it.propertyType==SerializedPropertyType.ObjectReference&&it.name!="m_Script")it.objectReferenceValue=Local(it.objectReferenceValue);
   so.ApplyModifiedPropertiesWithoutUndo();
  }
  EditorUtility.SetDirty(clone);return clone;
 }
 static Vector3 W(float x,float y,float h)=>new Vector3(.69465837f*x-.71933980f*y,h,-.71933980f*x-.69465837f*y);
 public static void Audit(){
  var source=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
  var all=source.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshRenderer>(true)).Where(r=>r.GetComponent<MeshFilter>()?.sharedMesh!=null).ToArray();
  var lines=new List<string>{"destination\tsource_asset\tsource_guid\tsource_local_file_id\tsource_object\tactive"};
  int idx=0;foreach(var r in all){var mesh=r.GetComponent<MeshFilter>().sharedMesh;AssetDatabase.TryGetGUIDAndLocalFileIdentifier(mesh,out string guid,out long id);lines.Add("Assets/R15/Meshes/R15_Mesh_"+(idx++).ToString("D4")+".asset\t"+AssetDatabase.GetAssetPath(mesh)+"\t"+guid+"\t"+id+"\t"+r.name+"\t"+(r.enabled&&r.gameObject.activeInHierarchy));}
  File.WriteAllLines(Root+"/evidence/mesh_provenance.tsv",lines);
  File.WriteAllText(Root+"/evidence/source_scene_sha256.txt",BitConverter.ToString(System.Security.Cryptography.SHA256.Create().ComputeHash(File.ReadAllBytes(Source))).Replace("-","").ToLowerInvariant());
  Debug.Log("STANDALONE_SOURCE_AUDIT_PASS meshes="+all.Length);
 }
 public static void Run(){
  Directory.CreateDirectory(Root+"/docs");Directory.CreateDirectory(Root+"/evidence");
  var before=AssetDatabase.GetDependencies(Source,true).OrderBy(x=>x).ToArray();
  string rows=string.Join("\n",before.Select(p=>"| `"+p+"` | "+AssetDatabase.AssetPathToGUID(p)+" | "+AssetDatabase.GetMainAssetTypeAtPath(p)?.Name+" |"));
  File.WriteAllText(Root+"/docs/DEPENDENCIES_BEFORE.md","# Dependências antes do bake\n\nUnity "+Application.unityVersion+"; AssetDatabase.GetDependencies(scene, true), na cópia temporária, sem alterar fontes.\n\nTotal: "+before.Length+". Caminhos R7–R14: "+before.Count(p=>Regex.IsMatch(p,@"R(?:[7-9]|1[0-4])(?:[_/\.])"))+". FBX: "+before.Count(p=>p.EndsWith(".fbx",StringComparison.OrdinalIgnoreCase))+". Materiais: "+before.Count(p=>p.EndsWith(".mat"))+".\n\n| Caminho | GUID | Tipo |\n|---|---|---|\n"+rows+"\n");
  var old=EditorSceneManager.OpenScene(Source,OpenSceneMode.Single);
  var selected=old.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshRenderer>(true)).Where(r=>r.GetComponent<MeshFilter>()?.sharedMesh!=null).ToArray();
  Need(selected.Length==380,"Expected 380 visible renderers; got "+selected.Length);
  var sky=(Material)Local(RenderSettings.skybox);
  var pipe=(RenderPipelineAsset)Local(GraphicsSettings.defaultRenderPipeline);
  var global=(RenderPipelineGlobalSettings)Local(AssetDatabase.LoadAssetAtPath<RenderPipelineGlobalSettings>("Assets/UniversalRenderPipelineGlobalSettings.asset"));
  var lightData=old.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Light>(true)).Where(l=>l.enabled&&l.gameObject.activeInHierarchy).Select(l=>new {l.type,l.color,l.intensity,l.shadows,position=l.transform.position,rotation=l.transform.rotation}).ToArray();
  var volumeData=old.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Volume>(true)).Where(v=>v.enabled&&v.gameObject.activeInHierarchy).Select(v=>new {v.isGlobal,v.priority,v.weight,profile=(VolumeProfile)Local(v.sharedProfile)}).ToArray();
  var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
  UnityEngine.SceneManagement.SceneManager.SetActiveScene(scene);
  RenderSettings.skybox=sky;RenderSettings.ambientMode=AmbientMode.Skybox;RenderSettings.ambientIntensity=1;
  int idx=0;long tris=0;
  foreach(var r in selected){
   var sourceMesh=r.GetComponent<MeshFilter>().sharedMesh;var mesh=UnityEngine.Object.Instantiate(sourceMesh);mesh.name="R15_Mesh_"+idx.ToString("D4");
   var vv=mesh.vertices;var nn=mesh.normals;var tt=mesh.tangents;
   for(int i=0;i<vv.Length;i++){
    vv[i]=r.transform.TransformPoint(vv[i]);
    float x=vv[i].x*.69465837f-vv[i].z*.71933980f,y=-vv[i].x*.71933980f-vv[i].z*.69465837f;
    Need(x>=-510.02f&&x<=-209.98f&&y>=-40.02f&&y<=260.02f,"Vertex outside crop: "+r.name);
    if(nn.Length==vv.Length)nn[i]=r.transform.localToWorldMatrix.inverse.transpose.MultiplyVector(nn[i]).normalized;
    if(tt.Length==vv.Length){var t=r.transform.TransformDirection(new Vector3(tt[i].x,tt[i].y,tt[i].z));tt[i]=new Vector4(t.x,t.y,t.z,tt[i].w);}
   }
   mesh.vertices=vv;mesh.normals=nn;mesh.tangents=tt;mesh.RecalculateBounds();
   Folder("Assets/R15/Meshes");string path="Assets/R15/Meshes/R15_Mesh_"+idx.ToString("D4")+".asset";var priorMesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(priorMesh!=null){EditorUtility.CopySerialized(mesh,priorMesh);UnityEngine.Object.DestroyImmediate(mesh);mesh=priorMesh;}else AssetDatabase.CreateAsset(mesh,path);
   var go=new GameObject("R15_"+idx.ToString("D4")+"_"+Clean(r.name));go.AddComponent<MeshFilter>().sharedMesh=mesh;
   var renderer=go.AddComponent<MeshRenderer>();renderer.enabled=r.enabled&&r.gameObject.activeInHierarchy;renderer.sharedMaterials=r.sharedMaterials.Select(m=>(Material)Local(m)).ToArray();renderer.receiveShadows=r.receiveShadows;renderer.shadowCastingMode=r.shadowCastingMode;
   // New colliders use only clipped local meshes. Water and foliage are not walkable solids.
   if(renderer.enabled&&!Regex.IsMatch(r.name,@"OCEAN|WATER|TREE|PALM|LEAF|FOLIAGE|GRASS",RegexOptions.IgnoreCase))go.AddComponent<MeshCollider>().sharedMesh=mesh;
   for(int sm=0;sm<mesh.subMeshCount;sm++)tris+=mesh.GetIndexCount(sm)/3;
   idx++;
  }
  foreach(var d in lightData){var g=new GameObject("R15_Light");g.transform.SetPositionAndRotation(d.position,d.rotation);var l=g.AddComponent<Light>();l.type=d.type;l.color=d.color;l.intensity=d.intensity;l.shadows=d.shadows;}
  foreach(var d in volumeData){var g=new GameObject("R15_Volume");var v=g.AddComponent<Volume>();v.isGlobal=d.isGlobal;v.priority=d.priority;v.weight=d.weight;v.sharedProfile=d.profile;}
  for(int axis=0;axis<2;axis++)for(int side=0;side<2;side++){
   var g=new GameObject("R15_Boundary_"+axis+"_"+side);g.transform.position=W(axis==0?(side==0?-510:-210):-360,axis==1?(side==0?-40:260):110,8);g.transform.rotation=Quaternion.Euler(0,46,0);
   var b=g.AddComponent<BoxCollider>();b.size=axis==0?new Vector3(1,18,300):new Vector3(300,18,1);
  }
  var cg=new GameObject("R15_MainCamera");cg.tag="MainCamera";var cam=cg.AddComponent<Camera>();cam.clearFlags=CameraClearFlags.Skybox;cam.fieldOfView=57;cam.nearClipPlane=.15f;cam.farClipPlane=420;cg.transform.position=W(-412.3f,72.44f,1.65f);cg.transform.LookAt(W(-411,142.43f,3.8f));cg.AddComponent<UniversalAdditionalCameraData>();
  GraphicsSettings.defaultRenderPipeline=pipe;QualitySettings.renderPipeline=pipe;
  if(global!=null)GraphicsSettings.RegisterRenderPipelineSettings<UniversalRenderPipeline>(global);
  Folder("Assets/Scenes");Need(EditorSceneManager.SaveScene(scene,Dest),"Save failed");AssetDatabase.SaveAssets();
  EditorSceneManager.CloseScene(old,true);
  EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Dest,true)};
  var deps=AssetDatabase.GetDependencies(new[]{Dest,AssetDatabase.GetAssetPath(pipe),AssetDatabase.GetAssetPath(global)},true).Distinct().OrderBy(x=>x).ToArray();
  Need(deps.All(p=>!p.StartsWith("Assets/")||p.StartsWith("Assets/R15/")||p==Dest),"External dependency: "+string.Join(",",deps.Where(p=>p.StartsWith("Assets/")&&!p.StartsWith("Assets/R15/")&&p!=Dest)));
  File.WriteAllLines(Root+"/evidence/export_paths.txt",deps.Where(p=>p.StartsWith("Assets/")));
  File.WriteAllLines(Root+"/evidence/provenance.tsv",new[]{"source\tdestination\tsource_guid\tdestination_guid"}.Concat(provenance));
  File.WriteAllText(Root+"/evidence/bake.json","{\"renderers\":"+idx+",\"triangles\":"+tris+",\"width_m\":300,\"depth_m\":300,\"scale\":1,\"source_dependencies\":"+before.Length+",\"local_dependencies\":"+deps.Count(p=>p.StartsWith("Assets/"))+"}");
  Debug.Log("STANDALONE_BAKE_PASS renderers="+idx+" tris="+tris);
 }
}
