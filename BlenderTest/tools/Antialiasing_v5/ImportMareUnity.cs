using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class ImportMareUnity {
 const string Src = @"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityExport_v4";
 const string Root = "Assets/R15/BlenderIntegrated";
 const string ScenePath = "Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity";
 [Serializable] public class Data { public int map_width,map_depth,city_collection,final_room_count; public string sky; public Mat[] materials; public Geo[] meshes; public Col[] collections; public Assembly[] assemblies; public float[] resort_matrix; }
 [Serializable] public class Mat { public int id; public string name,base_map,normal_map,metallic_map; public float[] color,emission; public float metallic,smoothness,alpha,emission_strength; public bool transparent; }
 [Serializable] public class Geo { public int id,vertices,triangles; public string name,file; public int[] materials; }
 [Serializable] public class Col { public int id; public string name; public Node[] nodes; }
 [Serializable] public class Node { public string name,kind,interaction,room_id; public int collection,mesh; public float[] matrix,light_color; public bool collider; public float light_energy,light_range; }
 [Serializable] public class Assembly { public string name; public int collection; public int[] stages; }
 static Data d; static Mesh[] meshes; static Material[] mats; static GameObject[] prefabs;
 static string P(string path) { return Root+"/"+path.Replace('\\','/'); }
 static Color ColorOf(float[] a) { return a==null||a.Length<3?Color.white:new Color(a[0],a[1],a[2],a.Length>3?a[3]:1); }
 static void TransformFrom(Transform t,float[] a) {
   if(a==null||a.Length!=16)return;
   var m=new Matrix4x4(); for(int r=0;r<4;r++)for(int c=0;c<4;c++)m[r,c]=a[r*4+c];
   Vector3 x=m.GetColumn(0), y=m.GetColumn(1), z=m.GetColumn(2); var s=new Vector3(x.magnitude,y.magnitude,z.magnitude);
   if(Vector3.Dot(Vector3.Cross(x,y),z)<0)s.x=-s.x;
   t.localPosition=m.GetColumn(3); t.localScale=s;
   t.localRotation=(s.z>0.00001f&&s.y>0.00001f)?Quaternion.LookRotation(z/s.z,y/s.y):Quaternion.identity;
 }
 static Texture TextureOf(string f) { return string.IsNullOrEmpty(f)?null:AssetDatabase.LoadAssetAtPath<Texture>(P(f)); }
 static void SaveAsset(UnityEngine.Object o,string path) {
   var old=AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path);
   if(old!=null) {EditorUtility.CopySerialized(o,old); UnityEngine.Object.DestroyImmediate(o);} else AssetDatabase.CreateAsset(o,path);
 }
 public static string Main() {
  d=Newtonsoft.Json.JsonConvert.DeserializeObject<Data>(File.ReadAllText(Path.Combine(Src,"main_map_export.json")));
  foreach(var folder in new[]{"Textures","Meshes","Materials","Prefabs","Evidence"})Directory.CreateDirectory(P(folder));
  foreach(var f in Directory.GetFiles(Path.Combine(Src,"Textures")))File.Copy(f,P("Textures/"+Path.GetFileName(f)),true);
  File.Copy(Path.Combine(Src,"main_map_export.json"),P("main_map_export.json"),true);
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  foreach(var f in Directory.GetFiles(P("Textures"))) {
   if(f.EndsWith(".meta"))continue; var ti=AssetImporter.GetAtPath(f.Replace('\\','/')) as TextureImporter;if(ti==null)continue;
   ti.maxTextureSize=2048; ti.wrapMode=TextureWrapMode.Repeat; ti.anisoLevel=4;
   if(f.Contains("normal")){ti.textureType=TextureImporterType.NormalMap;ti.sRGBTexture=false;}
   if(f.Contains("metallic")){ti.sRGBTexture=false;ti.alphaSource=TextureImporterAlphaSource.FromInput;}
   if(f.Contains("panorama"))ti.wrapMode=TextureWrapMode.Clamp;
   ti.SaveAndReimport();
  }
  mats=new Material[d.materials.Length]; meshes=new Mesh[d.meshes.Length]; prefabs=new GameObject[d.collections.Length];
  try {
   AssetDatabase.StartAssetEditing();
   foreach(var a in d.materials) {
    string path=P("Materials/material_"+a.id.ToString("D3")+".mat"); var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.name=a.name;m.enableInstancing=true;
    var color=ColorOf(a.color); if(a.transparent)color.a=a.alpha;
    m.SetColor("_BaseColor",color); m.SetFloat("_Metallic",a.metallic);m.SetFloat("_Smoothness",a.smoothness);
    if(!string.IsNullOrEmpty(a.base_map))m.SetTexture("_BaseMap",TextureOf(a.base_map));
    if(!string.IsNullOrEmpty(a.normal_map)){m.SetTexture("_BumpMap",TextureOf(a.normal_map));m.SetFloat("_BumpScale",0.65f);m.EnableKeyword("_NORMALMAP");}
    if(!string.IsNullOrEmpty(a.metallic_map)){m.SetTexture("_MetallicGlossMap",TextureOf(a.metallic_map));m.SetFloat("_Smoothness",1);m.EnableKeyword("_METALLICSPECGLOSSMAP");}
    if(a.emission_strength>0){m.EnableKeyword("_EMISSION");m.SetColor("_EmissionColor",ColorOf(a.emission)*Mathf.Min(a.emission_strength,2));}
    m.SetFloat("_Cull",0);
    if(a.transparent){m.SetFloat("_Surface",1);m.SetFloat("_SrcBlend",5);m.SetFloat("_DstBlend",10);m.SetFloat("_ZWrite",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.SetOverrideTag("RenderType","Transparent");m.renderQueue=3000;}
    SaveAsset(m,path); mats[a.id]=AssetDatabase.LoadAssetAtPath<Material>(path);
   }
   foreach(var g in d.meshes) {
    string path=P("Meshes/mesh_"+g.id.ToString("D5")+".asset");
    var existing=AssetDatabase.LoadAssetAtPath<Mesh>(path); if(existing!=null){meshes[g.id]=existing;continue;}
    using(var br=new BinaryReader(File.OpenRead(Path.Combine(Src,g.file)))) {
     if(br.ReadUInt32()!=0x3452534d)throw new Exception("Invalid mesh "+g.file);
     int count=(int)br.ReadUInt32(), sub=(int)br.ReadUInt32();var vs=new Vector3[count];var ns=new Vector3[count];var uv=new Vector2[count];
     for(int i=0;i<count;i++){vs[i]=new Vector3(br.ReadSingle(),br.ReadSingle(),br.ReadSingle());ns[i]=new Vector3(br.ReadSingle(),br.ReadSingle(),br.ReadSingle());uv[i]=new Vector2(br.ReadSingle(),br.ReadSingle());}
     var mesh=new Mesh {name=g.name,indexFormat=count>65535?IndexFormat.UInt32:IndexFormat.UInt16};mesh.vertices=vs;mesh.normals=ns;mesh.uv=uv;mesh.subMeshCount=sub;
     for(int j=0;j<sub;j++){br.ReadUInt32();int n=(int)br.ReadUInt32();var ix=new int[n];for(int k=0;k<n;k++)ix[k]=br.ReadInt32();mesh.SetIndices(ix,MeshTopology.Triangles,j,false);}
     mesh.RecalculateBounds();mesh.RecalculateTangents();AssetDatabase.CreateAsset(mesh,path);meshes[g.id]=mesh;
    }
    if(g.id%500==0)Debug.Log("MARE_IMPORT_MESH "+g.id);
   }
  } finally {AssetDatabase.StopAssetEditing();}
  AssetDatabase.SaveAssets();
  foreach(var a in d.materials)mats[a.id]=AssetDatabase.LoadAssetAtPath<Material>(P("Materials/material_"+a.id.ToString("D3")+".mat"));
  for(int i=0;i<d.collections.Length;i++)BuildCollection(i);
  EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
  PrefabUtility.InstantiatePrefab(prefabs[d.city_collection]);
  var resort=new GameObject("MARE_RESORT_EVOLUTION_STAGE_20");TransformFrom(resort.transform,d.resort_matrix);
  foreach(var a in d.assemblies){var go=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[a.collection]);go.transform.SetParent(resort.transform,false);go.name=a.name;go.SetActive(a.stages.Contains(20));}
  var sky=new Material(Shader.Find("Skybox/Panoramic"));sky.name="Mare_MainMap_Sky";sky.SetTexture("_MainTex",TextureOf(d.sky));sky.SetFloat("_Exposure",1);SaveAsset(sky,P("Materials/Sky.mat"));RenderSettings.skybox=AssetDatabase.LoadAssetAtPath<Material>(P("Materials/Sky.mat"));
  RenderSettings.ambientMode=AmbientMode.Skybox;RenderSettings.ambientIntensity=1;RenderSettings.reflectionIntensity=0.65f;
  if(UnityEngine.Object.FindObjectsByType<Light>().All(l=>l.type!=LightType.Directional)){var sun=new GameObject("Mare_Sun").AddComponent<Light>();sun.type=LightType.Directional;sun.intensity=1.7f;sun.transform.rotation=Quaternion.Euler(48,-35,0);sun.shadows=LightShadows.Soft;RenderSettings.sun=sun;}
  var camera=MakeCamera("Mare_Main_Camera",new Vector3(-343,1.8f,-357),new Vector3(-340,5,-311));camera.tag="MainCamera";camera.gameObject.AddComponent<AudioListener>();
  QualitySettings.shadowDistance=200;
  DynamicGI.UpdateEnvironment();
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),ScenePath);
  AssetDatabase.SaveAssets();
  if(SceneView.lastActiveSceneView!=null)SceneView.lastActiveSceneView.LookAt(new Vector3(-340,5,-295),Quaternion.Euler(25,0,0),100);
  return "Imported "+d.meshes.Length+" shared meshes, "+d.materials.Length+" materials, "+d.collections.Length+" prefabs into "+ScenePath;
 }
 static GameObject BuildCollection(int id) {
  if(prefabs[id]!=null)return prefabs[id];
  var col=d.collections[id];var root=new GameObject(col.name);
  foreach(var n in col.nodes) {
   GameObject go;
   if(n.collection>=0)go=(GameObject)PrefabUtility.InstantiatePrefab(BuildCollection(n.collection));else go=new GameObject(n.name);
   go.name=n.name;go.transform.SetParent(root.transform,false);TransformFrom(go.transform,n.matrix);
   if(n.mesh>=0){go.AddComponent<MeshFilter>().sharedMesh=meshes[n.mesh];var mr=go.AddComponent<MeshRenderer>();mr.sharedMaterials=d.meshes[n.mesh].materials.Select(i=>mats[i]).ToArray();if(n.collider)go.AddComponent<MeshCollider>().sharedMesh=meshes[n.mesh];}
   if(n.kind=="SUN"||n.kind=="POINT"||n.kind=="AREA"){var light=go.AddComponent<Light>();light.type=n.kind=="SUN"?LightType.Directional:LightType.Point;light.color=ColorOf(n.light_color);light.intensity=n.kind=="SUN"?1.7f:Mathf.Clamp(n.light_energy/150f,0.2f,2);light.range=Mathf.Clamp(n.light_range,3,12);light.shadows=n.kind=="SUN"?LightShadows.Soft:LightShadows.None;if(n.kind=="SUN")go.transform.rotation=Quaternion.Euler(48,-35,0);}
  }
  string path=P("Prefabs/collection_"+id.ToString("D3")+".prefab");prefabs[id]=PrefabUtility.SaveAsPrefabAsset(root,path);UnityEngine.Object.DestroyImmediate(root);Debug.Log("MARE_PREFAB "+id+" "+col.name);return prefabs[id];
 }
 public static string RepairMaterials() {
  d=Newtonsoft.Json.JsonConvert.DeserializeObject<Data>(File.ReadAllText(Path.Combine(Src,"main_map_export.json")));
  mats=d.materials.Select(a=>AssetDatabase.LoadAssetAtPath<Material>(P("Materials/material_"+a.id.ToString("D3")+".mat"))).ToArray();
  int fixedCount=0;
  foreach(var col in d.collections){string path=P("Prefabs/collection_"+col.id.ToString("D3")+".prefab");var root=PrefabUtility.LoadPrefabContents(path);
   foreach(var r in root.GetComponentsInChildren<MeshRenderer>(true)){var mesh=r.GetComponent<MeshFilter>().sharedMesh;var file=Path.GetFileNameWithoutExtension(AssetDatabase.GetAssetPath(mesh));int id=int.Parse(file.Substring(5));r.sharedMaterials=d.meshes[id].materials.Select(i=>mats[i]).ToArray();fixedCount++;}
   PrefabUtility.SaveAsPrefabAsset(root,path);PrefabUtility.UnloadPrefabContents(root);
  }
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());return "Rebound renderer materials: "+fixedCount;
 }
 static Camera MakeCamera(string name,Vector3 pos,Vector3 target) {
  var cam=new GameObject(name).AddComponent<Camera>();cam.transform.position=pos;cam.transform.LookAt(target);cam.nearClipPlane=.08f;cam.farClipPlane=10000;cam.fieldOfView=60;cam.clearFlags=CameraClearFlags.Skybox;cam.allowHDR=true;var extra=cam.gameObject.AddComponent<UniversalAdditionalCameraData>();extra.renderPostProcessing=true;extra.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;extra.antialiasingQuality=AntialiasingQuality.High;return cam;
 }
 public static string Capture() {
  if(UnityEngine.SceneManagement.SceneManager.GetActiveScene().path!=ScenePath)EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
  var camera=UnityEngine.Object.FindObjectsByType<Camera>().First(c=>c.name=="Mare_Main_Camera");
  var cameraData=camera.GetComponent<UniversalAdditionalCameraData>();cameraData.renderPostProcessing=true;
  if(cameraData.volumeStack==null||cameraData.volumeStack.GetComponent<ColorAdjustments>()==null)cameraData.volumeStack=VolumeManager.instance.CreateStack();
  VolumeManager.instance.Update(cameraData.volumeStack,camera.transform,cameraData.volumeLayerMask);
  string outDir=@"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityCaptures_v4";Directory.CreateDirectory(outDir);
  var shots=new[]{new {n="unity_walk",p=new Vector3(-343,1.8f,-357),t=new Vector3(-340,5,-311)},new {n="unity_map_overview",p=new Vector3(0,1250,-1900),t=new Vector3(0,40,-80)},new {n="unity_aerial",p=new Vector3(-560,340,-650),t=new Vector3(-330,5,-275)},new {n="unity_lobby",p=new Vector3(-337.8f,2.05f,-314),t=new Vector3(-345,1.65f,-308.5f)},new {n="unity_room",p=new Vector3(-344.35f,5.2f,-307.85f),t=new Vector3(-343.35f,4.65f,-312.1f)},new {n="unity_restaurant",p=new Vector3(-348.6f,2.1f,-287),t=new Vector3(-338.5f,1.5f,-278.5f)}};
  foreach(var shot in shots){camera.transform.position=shot.p;camera.transform.LookAt(shot.t);var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);rt.antiAliasing=UniversalRenderPipeline.asset.msaaSampleCount;rt.Create();camera.targetTexture=rt;var req=new UniversalRenderPipeline.SingleCameraRequest {destination=rt};for(int i=0;i<4;i++)RenderPipeline.SubmitRenderRequest(camera,req);var prev=RenderTexture.active;RenderTexture.active=rt;var tex=new Texture2D(1600,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,900),0,0);tex.Apply();File.WriteAllBytes(Path.Combine(outDir,shot.n+".png"),tex.EncodeToPNG());RenderTexture.active=prev;UnityEngine.Object.DestroyImmediate(tex);camera.targetTexture=null;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
  camera.transform.position=shots[0].p;camera.transform.LookAt(shots[0].t);EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
  var renderers=UnityEngine.Object.FindObjectsByType<MeshRenderer>();var cols=UnityEngine.Object.FindObjectsByType<MeshCollider>();Physics.SyncTransforms();
  var report=new {scene=ScenePath,device=SystemInfo.graphicsDeviceType.ToString(),unity=Application.unityVersion,active_renderers=renderers.Length,mesh_colliders=cols.Length,missing_meshes=renderers.Count(r=>r.GetComponent<MeshFilter>()==null||r.GetComponent<MeshFilter>().sharedMesh==null),missing_materials=renderers.Sum(r=>r.sharedMaterials.Count(m=>m==null||m.shader==null||m.shader.name=="Hidden/InternalErrorShader")),triangles=renderers.Sum(r=> (long)r.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3),map_width=2000,map_depth=1000,runtime_gameplay=false};
  File.WriteAllText(Path.Combine(outDir,"validation.json"),Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));return Newtonsoft.Json.JsonConvert.SerializeObject(report);
 }
 public static string GeometryReport() {
  var pts=new[]{new {name="promenade",p=new Vector3(-340,3,-352)},new {name="avenue",p=new Vector3(-340,3,-334)},new {name="sidewalk",p=new Vector3(-340,3,-321)},new {name="lobby",p=new Vector3(-342,3,-309)},new {name="restaurant",p=new Vector3(-340,3,-279)},new {name="room_upper",p=new Vector3(-343,6,-312)},new {name="beach",p=new Vector3(-340,3,-374)}};
  Physics.SyncTransforms();var rays=pts.Select(point=> {RaycastHit hit;bool ok=Physics.Raycast(point.p,Vector3.down,out hit,20);return new {point.name,hit=ok,object_name=ok?hit.collider.name:"",height=ok?hit.point.y:float.NaN};}).ToArray();
  var all=UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
  var deps=AssetDatabase.GetDependencies(ScenePath,true);
  var report=new {ground_samples=rays,object_count=all.Length,all_mesh_colliders=all.Count(t=>t.GetComponent<MeshCollider>()!=null),nonlocal_dependencies=deps.Where(p=>!p.StartsWith("Assets/")&&!p.StartsWith("Packages/")).ToArray(),local_dependency_count=deps.Length,scene=ScenePath,source_units="meters",building_rescale=false};
  var text=Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(@"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityCaptures_v4\geometry_validation.json",text);return text;
 }
 public static string FinishLighting() {
  d=Newtonsoft.Json.JsonConvert.DeserializeObject<Data>(File.ReadAllText(Path.Combine(Src,"main_map_export.json")));
  var fixtureEnergy=d.collections.SelectMany(c=>c.nodes).Where(n=>n.kind=="POINT"||n.kind=="AREA").GroupBy(n=>n.name).ToDictionary(g=>g.Key,g=>g.First().light_energy);
  var camera=UnityEngine.Object.FindObjectsByType<Camera>().First(c=>c.name=="Mare_Main_Camera");
  var volumeObject=GameObject.Find("Mare_Global_Art_Volume");if(volumeObject==null)volumeObject=new GameObject("Mare_Global_Art_Volume");
  var volume=volumeObject.GetComponent<Volume>();if(volume==null)volume=volumeObject.AddComponent<Volume>();volume.isGlobal=true;volume.priority=20;
  var profile=AssetDatabase.LoadAssetAtPath<VolumeProfile>(P("Materials/Mare_Volume.asset"));if(profile==null){profile=ScriptableObject.CreateInstance<VolumeProfile>();AssetDatabase.CreateAsset(profile,P("Materials/Mare_Volume.asset"));}
  ColorAdjustments ca;if(!profile.TryGet<ColorAdjustments>(out ca)){ca=profile.Add<ColorAdjustments>(true);AssetDatabase.AddObjectToAsset(ca,profile);}ca.postExposure.Override(0.35f);ca.saturation.Override(-5);ca.contrast.Override(4);
  Tonemapping tm;if(!profile.TryGet<Tonemapping>(out tm)){tm=profile.Add<Tonemapping>(true);AssetDatabase.AddObjectToAsset(tm,profile);}tm.mode.Override(TonemappingMode.ACES);
  Bloom bloom;if(!profile.TryGet<Bloom>(out bloom)){bloom=profile.Add<Bloom>(true);AssetDatabase.AddObjectToAsset(bloom,profile);}bloom.intensity.Override(.08f);bloom.threshold.Override(1.2f);
  volume.sharedProfile=profile;EditorUtility.SetDirty(profile);AssetDatabase.SaveAssets();
  var data=camera.GetComponent<UniversalAdditionalCameraData>();data.renderPostProcessing=true;data.volumeLayerMask=1;data.volumeStack=VolumeManager.instance.CreateStack();VolumeManager.instance.Update(data.volumeStack,camera.transform,1);
  foreach(var light in UnityEngine.Object.FindObjectsByType<Light>())if(light.type==LightType.Directional){light.intensity=2.0f;light.shadowBias=.05f;light.shadowNormalBias=.25f;}
  RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.48f,.58f,.7f);RenderSettings.ambientEquatorColor=new Color(.38f,.4f,.42f);RenderSettings.ambientGroundColor=new Color(.24f,.22f,.19f);RenderSettings.ambientIntensity=1;foreach(var light in UnityEngine.Object.FindObjectsByType<Light>())if(light.type==LightType.Point){float energy;light.intensity=fixtureEnergy.TryGetValue(light.name,out energy)?Mathf.Clamp(energy/150f,.2f,2)*2.5f:1;light.range=Mathf.Max(light.range,6);}RenderSettings.skybox.SetFloat("_Exposure",.8f);EditorUtility.SetDirty(RenderSettings.skybox);AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());return "ACES volume created with +0.35 exposure and restrained bloom";
 }
}
