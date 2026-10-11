using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public static class ResortVisualFinishCapture
{
    const string ScenePath = "Assets/Scenes/ProjectResort_300m_Immersive_v2.unity";

    [Serializable]
    sealed class CaptureRecord
    {
        public string file, sha256, view, scene, gpu, renderer;
        public int width, height, warmup_frames;
        public Vector3 camera, target;
    }

    [Serializable]
    sealed class CaptureReport
    {
        public string status, unity, gpu, renderer;
        public bool genuine_unity_render, fps_measured, art_approved;
        public CaptureRecord[] captures;
    }

    static Vector3 W(float cross, float along, float height)
    {
        return new Vector3(cross * .69465837f - along * .71933980f,
            height, -cross * .71933980f - along * .69465837f);
    }

    static void Need(bool condition, string reason)
    {
        if (!condition) throw new Exception("VISUAL_FINISH_CAPTURE_FAIL:" + reason);
    }

    static string Sha(byte[] bytes)
    {
        using (var sha = SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
    }

    static CaptureRecord RenderOne(string root, string id, string view, Vector3 position, Vector3 target)
    {
        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        Need(RenderSettings.skybox != null &&
             RenderSettings.skybox.shader.name == "Skybox/Panoramic", "PANORAMIC_SKY_MISSING");
        var camera = Camera.main ?? scene.GetRootGameObjects()
            .SelectMany(x => x.GetComponentsInChildren<Camera>(true)).FirstOrDefault();
        Need(camera != null, "CAMERA_MISSING");

        camera.transform.SetParent(null, true);
        camera.transform.position = position;
        if (id.StartsWith("04_", StringComparison.Ordinal))
        {
            Bounds bounds = new Bounds();
            bool hasBounds = false;
            foreach (var renderer in scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<Renderer>(true)))
            {
                if (!renderer.enabled) continue;
                if (!hasBounds) { bounds = renderer.bounds; hasBounds = true; }
                else bounds.Encapsulate(renderer.bounds);
            }
            Need(hasBounds, "AERIAL_BOUNDS_MISSING");
            target = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
            float requiredVerticalSpan = Mathf.Max(bounds.size.z, bounds.size.x / (16f / 9f));
            float aerialHeight = requiredVerticalSpan / (2f * Mathf.Tan(57f * Mathf.Deg2Rad * .5f)) * 1.12f;
            position = new Vector3(bounds.center.x, bounds.max.y + aerialHeight, bounds.center.z);
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(Vector3.down, new Vector3(-.7193398f, 0f, -.69465837f));
        }
        else camera.transform.LookAt(target);
        camera.fieldOfView = 57f;
        camera.nearClipPlane = .15f;
        camera.farClipPlane = 1000f;
        camera.clearFlags = CameraClearFlags.Skybox;

        const int width = 1600, height = 900;
        var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
        rt.Create();
        var priorTarget = camera.targetTexture;
        var priorActive = RenderTexture.active;
        Texture2D image = null;
        try
        {
            camera.targetTexture = rt;
            var request = new UniversalRenderPipeline.SingleCameraRequest { destination = rt };
            Need(RenderPipeline.SupportsRenderRequest(camera, request), "URP_RENDER_REQUEST_UNSUPPORTED");
            for (int i = 0; i < 5; i++) RenderPipeline.SubmitRenderRequest(camera, request);

            RenderTexture.active = rt;
            image = new Texture2D(width, height, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            image.Apply();
            var pixels = image.GetPixels32();
            int spread = pixels.Max(p => (int)p.r + p.g + p.b) -
                         pixels.Min(p => (int)p.r + p.g + p.b);
            byte[] png = image.EncodeToPNG();
            Need(png.Length > 60000 && spread > 90, "FRAME_EMPTY_OR_UNIFORM");
            string filename = "ProjectResort_v2_" + id + "_UnityGPU.png";
            File.WriteAllBytes(Path.Combine(root, filename), png);
            Debug.Log("VISUAL_FINISH_REAL_UNITY_GPU " + filename +
                      " bytes=" + png.Length + " sha256=" + Sha(png));
            return new CaptureRecord {
                file = filename, sha256 = Sha(png), view = view, scene = ScenePath,
                gpu = SystemInfo.graphicsDeviceName, renderer = SystemInfo.graphicsDeviceType.ToString(),
                width = width, height = height, warmup_frames = 5,
                camera = position, target = target
            };
        }
        finally
        {
            camera.targetTexture = priorTarget;
            RenderTexture.active = priorActive;
            if (image != null) UnityEngine.Object.DestroyImmediate(image);
            rt.Release();
            UnityEngine.Object.DestroyImmediate(rt);
        }
    }

    [MenuItem("Resort/Visual Finish/Capture five native Unity views")]
    public static void Run()
    {
        string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "../../"));
        string output = Path.Combine(repo, "evidence/visual_finish");
        Directory.CreateDirectory(output);

        var views = new[] {
            new { id = "01_PromenadeToBuildings", label = "Calçadão olhando para os prédios",
                pos = W(-427, 110, 1.65f), target = W(-397, 112, 9.5f) },
            new { id = "02_AvenueAndFacades", label = "Avenida e fachadas",
                pos = W(-412, 80, 2f), target = W(-394, 105, 7.8f) },
            new { id = "03_BeachSkyClouds", label = "Praia, céu e nuvens",
                pos = W(-430, 130, 2f), target = W(-408, 168, 15f) },
            new { id = "04_Aerial300m", label = "Vista aérea do mapa compacto",
                pos = W(-300, 150, 360f), target = W(-300, 150, 0f) },
            new { id = "05_CloseFacade", label = "Detalhe próximo das fachadas",
                pos = W(-401, 105, 2.4f), target = W(-391, 111, 6.5f) }
        };

        var captures = new List<CaptureRecord>();
        foreach (var view in views)
            captures.Add(RenderOne(output, view.id, view.label, view.pos, view.target));
        Need(captures.Count == 5, "FIVE_VIEWS_REQUIRED");

        var report = new CaptureReport {
            status = "FIVE_NATIVE_UNITY_GPU_CAPTURES_PASS_VISUAL_REVIEW_PENDING",
            unity = Application.unityVersion, gpu = SystemInfo.graphicsDeviceName,
            renderer = SystemInfo.graphicsDeviceType.ToString(),
            genuine_unity_render = true, fps_measured = false, art_approved = false,
            captures = captures.ToArray()
        };
        File.WriteAllText(Path.Combine(output, "visual_finish_qa.json"),
            JsonUtility.ToJson(report, true));

        // Leave the Editor on the saved v2 scene without persisting capture camera transforms.
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        Debug.Log("VISUAL_FINISH_FIVE_NATIVE_CAPTURES_PASS gpu=" +
                  SystemInfo.graphicsDeviceName + " size=1600x900");
    }
}
