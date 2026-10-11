using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class FixMareAntialiasing {
 const string Scene="Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity";
 const string Asset="Assets/R15/BlenderIntegrated/Rendering/Mare_URP_Antialiasing.asset";
 const string Output=@"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityCaptures_AA_v5";
 public static string Apply() {
  if(UnityEngine.SceneManagement.SceneManager.GetActiveScene().path!=Scene)EditorSceneManager.OpenScene(Scene,OpenSceneMode.Single);
  var current=GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
  if(current==null)throw new Exception("URP is required");
  Directory.CreateDirectory(Path.GetDirectoryName(Asset));AssetDatabase.Refresh();
  var pipeline=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Asset);
  if(pipeline==null){pipeline=UnityEngine.Object.Instantiate(current);pipeline.name="Mare_URP_Antialiasing";AssetDatabase.CreateAsset(pipeline,Asset);}
  pipeline.msaaSampleCount=4;pipeline.renderScale=1;
  GraphicsSettings.defaultRenderPipeline=pipeline;QualitySettings.renderPipeline=pipeline;EditorUtility.SetDirty(pipeline);
  foreach(var cam in UnityEngine.Object.FindObjectsByType<Camera>()) {
   cam.allowMSAA=true;var data=cam.GetComponent<UniversalAdditionalCameraData>();if(data==null)continue;
   data.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing;data.antialiasingQuality=AntialiasingQuality.High;data.renderPostProcessing=true;data.volumeStack=null;
   EditorUtility.SetDirty(cam);EditorUtility.SetDirty(data);
  }
  AssetDatabase.SaveAssets();EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
  return "MSAA4 + SMAA High configured on Mare camera and dedicated URP asset";
 }
 public static string Capture() {
  if(UnityEngine.SceneManagement.SceneManager.GetActiveScene().path!=Scene)throw new Exception("Unexpected scene");
  Directory.CreateDirectory(Output);
  var camera=UnityEngine.Camera.main;var data=camera.GetComponent<UniversalAdditionalCameraData>();
  if(data.volumeStack==null||data.volumeStack.GetComponent<ColorAdjustments>()==null)data.volumeStack=VolumeManager.instance.CreateStack();
  VolumeManager.instance.Update(data.volumeStack,camera.transform,data.volumeLayerMask);
  var savedPos=camera.transform.position;var savedRot=camera.transform.rotation;
  var shots=new[]{new {n="walk",p=new Vector3(-343,1.8f,-357),t=new Vector3(-340,5,-311)},new {n="room",p=new Vector3(-344.35f,5.2f,-307.85f),t=new Vector3(-343.35f,4.65f,-312.1f)},new {n="restaurant",p=new Vector3(-348.6f,2.1f,-287),t=new Vector3(-338.5f,1.5f,-278.5f)},new {n="aerial",p=new Vector3(-560,340,-650),t=new Vector3(-330,5,-275)}};
  var records=new System.Collections.Generic.List<object>();
  foreach(var shot in shots) {
   var old=@"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityCaptures_v4\unity_"+shot.n+".png";
   File.Copy(old,Path.Combine(Output,"before_"+shot.n+".png"),true);
   camera.transform.position=shot.p;camera.transform.LookAt(shot.t);
   var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32){antiAliasing=4};rt.Create();camera.targetTexture=rt;
   var request=new UniversalRenderPipeline.SingleCameraRequest{destination=rt};
   if(!RenderPipeline.SupportsRenderRequest(camera,request))throw new Exception("Unsupported render request");
   for(int i=0;i<5;i++)RenderPipeline.SubmitRenderRequest(camera,request);
   var prior=RenderTexture.active;RenderTexture.active=rt;
   var tex=new Texture2D(1600,900,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,900),0,0);tex.Apply();
   var pixels=tex.GetPixels32();var spread=pixels.Max(p=>(int)p.r+p.g+p.b)-pixels.Min(p=>(int)p.r+p.g+p.b);
   byte[] png=tex.EncodeToPNG();if(png.Length<60000||spread<90)throw new Exception("Empty capture "+shot.n);
   string path=Path.Combine(Output,"after_"+shot.n+".png");File.WriteAllBytes(path,png);
   records.Add(new {view=shot.n,width=1600,height=900,msaa_requested=4,msaa_texture=rt.antiAliasing,antialiasing=data.antialiasing.ToString(),quality=data.antialiasingQuality.ToString(),path,bytes=png.Length});
   RenderTexture.active=prior;camera.targetTexture=null;UnityEngine.Object.DestroyImmediate(tex);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
  }
  camera.transform.position=savedPos;camera.transform.rotation=savedRot;
  var pipeline=GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
  var report=new {scene=Scene,pipeline=Asset,device=SystemInfo.graphicsDeviceType.ToString(),gpu=SystemInfo.graphicsDeviceName,msaa=pipeline.msaaSampleCount,render_scale=pipeline.renderScale,post_processing=data.renderPostProcessing,render_request=true,fps_measured=false,captures=records};
  string json=Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(Path.Combine(Output,"antialiasing_validation.json"),json);EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());return json;
 }
}
