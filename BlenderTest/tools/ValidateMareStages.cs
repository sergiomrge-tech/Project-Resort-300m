using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
public static class ValidateMareStages {
 public static string Main() {
  string manifest="Assets/R15/BlenderIntegrated/main_map_export.json";
  var d=Newtonsoft.Json.Linq.JObject.Parse(File.ReadAllText(manifest));
  var roomNames=new HashSet<string>(d["collections"].SelectMany(c=>c["nodes"]).Where(n=>!string.IsNullOrEmpty((string)n["room_id"])).Select(n=>(string)n["name"]));
  var reports=new List<object>();
  for(int stage=1;stage<=20;stage++) {
   MareEvolutionPreview.Apply(stage);
   var renderers=UnityEngine.Object.FindObjectsByType<MeshRenderer>();
   int rooms=UnityEngine.Object.FindObjectsByType<Transform>().Count(t=>roomNames.Contains(t.name));
   reports.Add(new {stage,rooms,renderers=renderers.Length,missing_meshes=renderers.Count(r=>r.GetComponent<MeshFilter>().sharedMesh==null),missing_materials=renderers.Sum(r=>r.sharedMaterials.Count(m=>m==null||m.shader==null||!m.shader.isSupported))});
  }
  MareEvolutionPreview.Apply(20);EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
  var output=Newtonsoft.Json.JsonConvert.SerializeObject(reports,Newtonsoft.Json.Formatting.Indented);File.WriteAllText(@"D:\ProjectResort_300m_CompactPass\BlenderTest\UnityCaptures_v4\stages_validation.json",output);return output;
 }
}
