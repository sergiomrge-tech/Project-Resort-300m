using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using TMPro;

[InitializeOnLoad]
public static class BuildMareWindows
{
    const string Main="Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity";
    const string Preview="Assets/Scenes/ProjectResort_Mare_StandalonePreview.unity";
    const string Output=@"D:\ProjectResort_300m_CompactPass\Builds\Mare_Windows_v6";
    [Serializable] class Manifest { public Assembly[] assemblies; }
    [Serializable] class Assembly { public string name; public int[] stages; }
    static double nextTick;
    static BuildMareWindows() { if(SessionState.GetBool("MareBuildPending",false)) { nextTick=EditorApplication.timeSinceStartup+8; EditorApplication.update+=ContinueBuild; } }
    public static void Bootstrap()
    {
        SessionState.SetBool("MareBuildPending",true);
        var package=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(TMP_Text).Assembly);
        if(!AssetDatabase.LoadAssetAtPath<TMP_FontAsset>("Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset"))
            AssetDatabase.ImportPackage(Path.Combine(package.resolvedPath,"Package Resources/TMP Essential Resources.unitypackage"),false);
        nextTick=EditorApplication.timeSinceStartup+8; EditorApplication.update-=ContinueBuild; EditorApplication.update+=ContinueBuild;
    }
    static void ContinueBuild()
    {
        if(EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.timeSinceStartup<nextTick) return;
        EditorApplication.update-=ContinueBuild; SessionState.SetBool("MareBuildPending",false);
        try { Debug.Log(Prepare()); Debug.Log(Build()); if(Application.isBatchMode) EditorApplication.Exit(0); }
        catch(Exception error) { Debug.LogException(error); Directory.CreateDirectory(Output); File.WriteAllText(Path.Combine(Output,"build_failure.txt"),error.ToString()); if(Application.isBatchMode) EditorApplication.Exit(1); }
    }
    public static string Prepare()
    {
        AssetDatabase.Refresh();
        if(EditorApplication.isCompiling) throw new Exception("Compilation still in progress");
        if(!AssetDatabase.LoadAssetAtPath<SceneAsset>(Preview) && !AssetDatabase.CopyAsset(Main,Preview)) throw new Exception("Cannot copy main scene");
        var scene=EditorSceneManager.OpenScene(Preview,OpenSceneMode.Single);
        var camera=Camera.main; if(!camera) throw new Exception("Missing main camera");
        var viewer=camera.GetComponent<MareStandaloneViewer>(); if(!viewer) viewer=camera.gameObject.AddComponent<MareStandaloneViewer>();
        viewer.font=AssetDatabase.LoadAssetAtPath<TMP_FontAsset>("Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset");
        if(!viewer.font) throw new Exception("TMP Essential Resources not imported");
        var root=scene.GetRootGameObjects().First(g=>g.name.StartsWith("MARE_RESORT_EVOLUTION_STAGE_"));
        var manifest=Newtonsoft.Json.JsonConvert.DeserializeObject<Manifest>(File.ReadAllText("Assets/R15/BlenderIntegrated/main_map_export.json"));
        viewer.modules=manifest.assemblies.Select(a=>new MareStandaloneViewer.Module{root=root.transform.Find(a.name)?.gameObject,stages=a.stages}).ToArray();
        if(viewer.modules.Any(m=>!m.root)) throw new Exception("Missing evolution module");
        viewer.stage=20;
        foreach(var module in viewer.modules) module.root.SetActive(module.stages.Contains(20));
        root.name="MARE_RESORT_EVOLUTION_STAGE_20";
        camera.allowMSAA=true; var data=camera.GetComponent<UniversalAdditionalCameraData>(); data.antialiasing=AntialiasingMode.SubpixelMorphologicalAntiAliasing; data.antialiasingQuality=AntialiasingQuality.High;
        EditorUtility.SetDirty(viewer); EditorSceneManager.MarkSceneDirty(scene); EditorSceneManager.SaveScene(scene);
        PlayerSettings.productName="Project Resort Mare";
        PlayerSettings.companyName="Project Resort";
        PlayerSettings.bundleVersion="0.6.0";
        PlayerSettings.defaultScreenWidth=1600; PlayerSettings.defaultScreenHeight=900;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
        PlayerSettings.resizableWindow=true;
        PlayerSettings.runInBackground=true;
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.StandaloneWindows64,false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.StandaloneWindows64,new[]{GraphicsDeviceType.Direct3D11});
        PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
        AssetDatabase.SaveAssets();
        Directory.CreateDirectory(Output);
        return "Standalone scene prepared: "+viewer.modules.Length+" modules; Windows64 Mono Direct3D11; original main scene preserved";
    }
    public static string Build()
    {
        if(!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Standalone,BuildTarget.StandaloneWindows64)) throw new Exception("Windows build support missing");
        try {
            var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Preview},locationPathName=Path.Combine(Output,"ProjectResort_Mare.exe"),target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
            var messages=report.steps.SelectMany(s=>s.messages).Where(m=>m.type==LogType.Warning||m.type==LogType.Error||m.type==LogType.Exception).Select(m=>new{type=m.type.ToString(),message=m.content}).ToArray();
            string json=Newtonsoft.Json.JsonConvert.SerializeObject(new{result=report.summary.result.ToString(),errors=report.summary.totalErrors,warnings=report.summary.totalWarnings,bytes=report.summary.totalSize,duration_seconds=report.summary.totalTime.TotalSeconds,scene=Preview,unity=Application.unityVersion,build_time=DateTime.UtcNow,messages},Newtonsoft.Json.Formatting.Indented);
            File.WriteAllText(Path.Combine(Output,"build_report.json"),json);
            if(report.summary.result!=BuildResult.Succeeded) throw new Exception(json);
            return json;
        } finally { EditorSceneManager.OpenScene(Main,OpenSceneMode.Single); }
    }
}
