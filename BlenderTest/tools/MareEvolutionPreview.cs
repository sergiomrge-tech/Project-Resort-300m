using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public class MareEvolutionPreview : EditorWindow {
 [Serializable] class Manifest {public Assembly[] assemblies;}
 [Serializable] class Assembly {public string name;public int[] stages;}
 int stage=20;
 [MenuItem("Resort/Blender Mare/Visualizar evolução 1 a 20")]
 public static void Open(){GetWindow<MareEvolutionPreview>("Evolução Maré");}
 void OnGUI(){
  EditorGUILayout.LabelField("Prévia dos módulos do resort",EditorStyles.boldLabel);
  stage=EditorGUILayout.IntSlider("Etapa",stage,1,20);
  EditorGUILayout.HelpBox("Ativa a composição arquitetônica da etapa escolhida. Compras, economia e interações ainda precisam de implementação no jogo.",MessageType.Info);
  if(GUILayout.Button("Aplicar etapa na cena"))Apply(stage);
 }
 public static void Apply(int stage){
  var resort=UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects().FirstOrDefault(g=>g.name.StartsWith("MARE_RESORT_EVOLUTION_STAGE_"));
  if(resort==null){Debug.LogError("Abra ProjectResort_Main_2x1km_Mare antes de escolher a etapa.");return;}
  var manifest=Newtonsoft.Json.JsonConvert.DeserializeObject<Manifest>(File.ReadAllText("Assets/R15/BlenderIntegrated/main_map_export.json"));
  foreach(var a in manifest.assemblies){var child=resort.transform.Find(a.name);if(child!=null){Undo.RecordObject(child.gameObject,"Etapa do resort");child.gameObject.SetActive(a.stages.Contains(stage));}}
  Undo.RecordObject(resort,"Etapa do resort");resort.name="MARE_RESORT_EVOLUTION_STAGE_"+stage.ToString("D2");EditorSceneManager.MarkSceneDirty(resort.scene);SceneView.RepaintAll();
 }
}
