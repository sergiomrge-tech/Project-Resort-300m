using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

// Operates only on the newly baked local scene and R15 assets.
public static class StandaloneFinish {
 public static void Run(){
  const string path="Assets/Scenes/ProjectResort_300m.unity";
  var scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Single);
  int removed=0,tuned=0;
  var rs=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<MeshRenderer>(true)).ToArray();
  foreach(var r in rs){
   var mesh=r.GetComponent<MeshFilter>().sharedMesh;var mats=r.sharedMaterials;
   var groups=new List<int[]>();var used=new List<Material>();
   for(int i=0;i<mesh.subMeshCount;i++){
    var indices=mesh.GetTriangles(i);if(indices.Length==0){removed++;continue;}
    if(i>=mats.Length||mats[i]==null)throw new Exception("Missing used material "+r.name+" slot="+i);
    groups.Add(indices);used.Add(mats[i]);
   }
   mesh.subMeshCount=groups.Count;for(int i=0;i<groups.Count;i++)mesh.SetTriangles(groups[i],i,false);mesh.RecalculateBounds();r.sharedMaterials=used.ToArray();
   var collider=r.GetComponent<MeshCollider>();if(collider!=null){collider.sharedMesh=null;collider.sharedMesh=mesh;}
   EditorUtility.SetDirty(mesh);
  }
  foreach(var mat in rs.SelectMany(r=>r.sharedMaterials).Distinct()){
   string name=mat.name.ToLowerInvariant();
   // Remove obsolete texture slots left by earlier shader changes.
   var so=new SerializedObject(mat);var slots=so.FindProperty("m_SavedProperties.m_TexEnvs");var valid=mat.GetTexturePropertyNames();
   for(int i=slots.arraySize-1;i>=0;i--)if(!valid.Contains(slots.GetArrayElementAtIndex(i).FindPropertyRelative("first").stringValue))slots.DeleteArrayElementAtIndex(i);
   so.ApplyModifiedPropertiesWithoutUndo();
   if(name.Contains("mosaic")&&mat.HasProperty("_BaseColor")){mat.SetColor("_BaseColor",new Color(.84f,.83f,.80f,1));tuned++;}
   if((name.Contains("asphalt")||name.Contains("sidewalk")||name.Contains("gutter")||name.Contains("curb"))&&mat.HasProperty("_BumpScale")){mat.SetFloat("_BumpScale",.65f);tuned++;}
   mat.enableInstancing=true;EditorUtility.SetDirty(mat);
  }
  var pipe=GraphicsSettings.defaultRenderPipeline;
  int quality=QualitySettings.GetQualityLevel();for(int i=0;i<QualitySettings.names.Length;i++){QualitySettings.SetQualityLevel(i,false);QualitySettings.renderPipeline=pipe;}QualitySettings.SetQualityLevel(quality,false);
  PlayerSettings.productName="Project Resort 300m";PlayerSettings.companyName="Project Resort";
  EditorSceneManager.SaveScene(scene,path);AssetDatabase.SaveAssets();
  var roots=new[]{path}.Concat(AssetDatabase.FindAssets("",new[]{"Assets/R15/Rendering"}).Select(AssetDatabase.GUIDToAssetPath).Where(p=>!AssetDatabase.IsValidFolder(p))).ToArray();
  var deps=AssetDatabase.GetDependencies(roots,true).Distinct().OrderBy(p=>p).ToArray();
  if(deps.Any(p=>p.StartsWith("Assets/")&&!p.StartsWith("Assets/R15/")&&p!=path))throw new Exception("Non-local asset after finish");
  string output=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
  File.WriteAllLines(output+"/evidence/export_paths.txt",deps.Where(p=>p.StartsWith("Assets/")));
  File.WriteAllText(output+"/evidence/material_finish.json","{\"empty_material_slots_removed\":"+removed+",\"materials_tuned\":"+tuned+",\"art_approved\":false}");
  Debug.Log("STANDALONE_FINISH_PASS removedSlots="+removed+" tuned="+tuned+" dependencies="+deps.Length);
 }
}
