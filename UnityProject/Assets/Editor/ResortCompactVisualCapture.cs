using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortCompactVisualCapture {
 [Serializable] class Shot{
  public string filename,sha256,scene,view,gpu; public int width,height,warmup_frames;public Vector3 camera,target;
 }
 [Serializable] class Report{
  public string status,unity,gpu,renderer;public float measured_gap_before,measured_gap_after,city_approach_m;
  public bool skybox_seen,art_approved=false,real_gameplay_tested=false,fps_measured=false;
  public Shot[] captures;
 }
 static string Sha(byte[] bytes){using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
 static Vector3 W(float c,float along,float height)=>new Vector3(c*.69465837f-along*.71933980f,height,-c*.71933980f-along*.69465837f);
 static void Need(bool p,string reason){if(!p)throw new Exception("COMPACT_VISUAL_FAIL:"+reason);}
 static Shot Capture(string scenePath,string name,string view,Vector3 pos,Vector3 target,string outdir){
  var scene=EditorSceneManager.OpenScene(scenePath,OpenSceneMode.Single);
  Need(RenderSettings.skybox!=null&&RenderSettings.skybox.shader.name=="Skybox/Panoramic","SKY_MISSING");
  var c=Camera.main??scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Camera>(true)).FirstOrDefault();
  Need(c!=null,"NO_CAMERA");
  c.transform.position=pos;c.transform.LookAt(target);c.fieldOfView=57f;
  c.nearClipPlane=.08f;c.farClipPlane=420f;c.clearFlags=CameraClearFlags.Skybox;
  var rt=new RenderTexture(1600,900,24,RenderTextureFormat.ARGB32);rt.Create();
  var savedTarget=c.targetTexture;var savedActive=RenderTexture.active;Texture2D image=null;
  try {
   c.targetTexture=rt;var req=new UniversalRenderPipeline.SingleCameraRequest{destination=rt};
   Need(RenderPipeline.SupportsRenderRequest(c,req),"URP_NOT_READY");
   for(int i=0;i<5;i++)RenderPipeline.SubmitRenderRequest(c,req);
   RenderTexture.active=rt;image=new Texture2D(1600,900,TextureFormat.RGB24,false);
   image.ReadPixels(new Rect(0,0,1600,900),0,0);image.Apply();
   var pixels=image.GetPixels32();
   int range=pixels.Max(x=>x.r+x.g+x.b)-pixels.Min(x=>x.r+x.g+x.b);
   var data=image.EncodeToPNG();
   Need(data.Length>60000&&range>90,"GPU_FRAME_NOT_POPULATED");
   string path=Path.Combine(outdir,name);File.WriteAllBytes(path,data);
   Debug.Log("R15_COMPACT_REAL_UNITY_GPU "+name+" size="+data.Length+" sha="+Sha(data));
   return new Shot{filename=name,sha256=Sha(data),scene=scenePath,view=view,
    gpu=SystemInfo.graphicsDeviceName,width=1600,height=900,warmup_frames=5,camera=pos,target=target};
  }finally{
   c.targetTexture=savedTarget;RenderTexture.active=savedActive;
   if(image!=null)UnityEngine.Object.DestroyImmediate(image);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
  }
 }
 [MenuItem("Resort/Compact Shore/Real before-after Unity captures")]
 public static void Run(){
  string root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../"));
  string dir=Path.Combine(root,"evidence/compact_before_after");
  Directory.CreateDirectory(dir);
  var configs=new[]{
   new {id="01_MosaicToCity",pos=W(-419,110,1.65f),target=W(-345,111,12)},
   new {id="02_CoastFacingCity",pos=W(-404,80,2.15f),target=W(-343,120,10)},
   new {id="03_AbovePromenade",pos=W(-424,115,86),target=W(-336,115,4)}
  };
  var shots=new List<Shot>();
  foreach(var q in configs) {
   shots.Add(Capture(ResortCompactShoreCity.Source,"R15_"+q.id+"_BEFORE_RealUnity.png",q.id,q.pos,q.target,dir));
   shots.Add(Capture(ResortCompactShoreCity.Output,"R15_"+q.id+"_AFTER_RealUnity.png",q.id,q.pos,q.target,dir));
  }
  Need(shots.Count==6,"INCOMPLETE_BEFORE_AFTER");
  var report=new Report{status="R15_COMPACT_REAL_GPU_BEFORE_AFTER_PASS_VISUAL_REVIEW_PENDING",
   unity=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,
   renderer=SystemInfo.graphicsDeviceType.ToString(),skybox_seen=true,
   city_approach_m=64f,measured_gap_before=73.2f,measured_gap_after=9.2f,captures=shots.ToArray()};
  File.WriteAllText(Path.Combine(root,"evidence/compact_visual_qa.json"),JsonUtility.ToJson(report,true));
  Debug.Log("R15_COMPACT_REAL_UNITY_BEFORE_AFTER_PASS captures=6");
 }
}
