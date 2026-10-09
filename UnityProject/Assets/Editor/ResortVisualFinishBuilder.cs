using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

public static class ResortVisualFinishBuilder
{
    const string SourceScene = "Assets/Scenes/ProjectResort_300m_Immersive.unity";
    const string OutputScene = "Assets/Scenes/ProjectResort_300m_Immersive_v2.unity";
    const string RootName = "RPF_VisualFinish";
    const string AssetRoot = "Assets/R15/VisualFinish";
    const string MeshRoot = AssetRoot + "/Meshes";
    const string MaterialRoot = AssetRoot + "/Materials";
    const float Cos = .69465837f;
    const float Sin = .71933980f;
    const float Yaw = 136f;
    static Mesh cube;
    static Mesh sphere;
    static Mesh palmTrunk;
    static Mesh palmLeaves;
    static readonly Dictionary<string, Material> Mats = new Dictionary<string, Material>();

    sealed class Building
    {
        public string key;
        public float c0 = float.PositiveInfinity, c1 = float.NegativeInfinity;
        public float a0 = float.PositiveInfinity, a1 = float.NegativeInfinity;
        public float y0 = float.PositiveInfinity, y1 = float.NegativeInfinity;
    }

    [Serializable]
    sealed class Report
    {
        public string status, source_scene, destination_scene, unity, renderer, gpu, source_sha256;
        public int base_renderers, final_renderers, building_families, awnings, palms, planters, benches, lights;
        public float width_m, depth_m;
        public bool source_unchanged, skybox_preserved, original_scenes_preserved;
        public bool fps_measured, art_approved;
        public string[] views;
    }

    static void Need(bool condition, string code)
    {
        if (!condition) throw new Exception("VISUAL_FINISH_FAIL:" + code);
    }

    static string Hash(string file)
    {
        using (var sha = System.Security.Cryptography.SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(file))).Replace("-", "").ToLowerInvariant();
    }

    static Vector3 P(float cross, float along, float y)
    {
        return new Vector3(cross * Cos - along * Sin, y, -cross * Sin - along * Cos);
    }

    static int StableHash(string value)
    {
        unchecked
        {
            int h = 23;
            foreach (char c in value) h = h * 31 + c;
            return h & 0x7fffffff;
        }
    }

    static void EnsureFolder(string path)
    {
        string[] parts = path.Split('/');
        string parent = parts[0];
        for (int i = 1; i < parts.Length; i++)
        {
            string next = parent + "/" + parts[i];
            if (!AssetDatabase.IsValidFolder(next)) AssetDatabase.CreateFolder(parent, parts[i]);
            parent = next;
        }
    }

    static Material Mat(string name, Color color, float smoothness, float metallic = 0f)
    {
        string path = MaterialRoot + "/" + name + ".mat";
        Material m = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (m == null)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) shader = Shader.Find("Standard");
            Need(shader != null, "LIT_SHADER_MISSING");
            m = new Material(shader);
            m.name = name;
            AssetDatabase.CreateAsset(m, path);
        }
        if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", color);
        if (m.HasProperty("_Color")) m.SetColor("_Color", color);
        if (m.HasProperty("_Smoothness")) m.SetFloat("_Smoothness", smoothness);
        if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", metallic);
        m.enableInstancing = true;
        Mats[name] = m;
        return m;
    }

    static Mesh SaveMesh(string name, Mesh mesh)
    {
        string path = MeshRoot + "/" + name + ".asset";
        Mesh existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if (existing != null)
        {
            UnityEngine.Object.DestroyImmediate(mesh);
            return existing;
        }
        mesh.name = name;
        AssetDatabase.CreateAsset(mesh, path);
        return mesh;
    }

    static Mesh MakeCube()
    {
        Mesh m = new Mesh();
        m.vertices = new[] {
            new Vector3(-.5f,-.5f,-.5f),new Vector3(.5f,-.5f,-.5f),new Vector3(.5f,.5f,-.5f),new Vector3(-.5f,.5f,-.5f),
            new Vector3(-.5f,-.5f,.5f),new Vector3(.5f,-.5f,.5f),new Vector3(.5f,.5f,.5f),new Vector3(-.5f,.5f,.5f),
            new Vector3(-.5f,-.5f,-.5f),new Vector3(-.5f,.5f,-.5f),new Vector3(-.5f,.5f,.5f),new Vector3(-.5f,-.5f,.5f),
            new Vector3(.5f,-.5f,-.5f),new Vector3(.5f,.5f,-.5f),new Vector3(.5f,.5f,.5f),new Vector3(.5f,-.5f,.5f),
            new Vector3(-.5f,-.5f,-.5f),new Vector3(-.5f,-.5f,.5f),new Vector3(.5f,-.5f,.5f),new Vector3(.5f,-.5f,-.5f),
            new Vector3(-.5f,.5f,-.5f),new Vector3(-.5f,.5f,.5f),new Vector3(.5f,.5f,.5f),new Vector3(.5f,.5f,-.5f)
        };
        var tris = new List<int>();
        for (int f = 0; f < 6; f++)
        {
            int i = f * 4;
            tris.AddRange(new[] { i, i + 1, i + 2, i, i + 2, i + 3 });
        }
        m.triangles = tris.ToArray();
        m.RecalculateNormals();
        m.RecalculateBounds();
        return SaveMesh("RPF_Box", m);
    }

    static Mesh MakeSphere()
    {
        const int rings = 8, sides = 12;
        var v = new List<Vector3>();
        var uv = new List<Vector2>();
        var t = new List<int>();
        for (int r = 0; r <= rings; r++)
        {
            float phi = Mathf.PI * r / rings;
            for (int s = 0; s <= sides; s++)
            {
                float theta = Mathf.PI * 2f * s / sides;
                v.Add(new Vector3(Mathf.Sin(phi) * Mathf.Cos(theta), Mathf.Cos(phi), Mathf.Sin(phi) * Mathf.Sin(theta)) * .5f);
                uv.Add(new Vector2((float)s / sides, (float)r / rings));
                if (r < rings && s < sides)
                {
                    int a = r * (sides + 1) + s, b = a + sides + 1;
                    t.AddRange(new[] { a, b, a + 1, a + 1, b, b + 1 });
                }
            }
        }
        Mesh m = new Mesh { vertices = v.ToArray(), uv = uv.ToArray(), triangles = t.ToArray() };
        m.RecalculateNormals(); m.RecalculateBounds();
        return SaveMesh("RPF_SoftSphere", m);
    }

    static Mesh MakeTrunk()
    {
        const int rings = 8, sides = 12;
        var v = new List<Vector3>(); var t = new List<int>();
        for (int r = 0; r <= rings; r++)
        {
            float q = (float)r / rings;
            float radius = Mathf.Lerp(.22f, .105f, q);
            float bend = .12f * q * q;
            for (int s = 0; s < sides; s++)
            {
                float a = Mathf.PI * 2f * s / sides;
                v.Add(new Vector3(Mathf.Cos(a) * radius + bend, q * 4.7f, Mathf.Sin(a) * radius));
                if (r < rings)
                {
                    int n = r * sides + s, next = r * sides + (s + 1) % sides;
                    int upper = n + sides, upperNext = next + sides;
                    t.AddRange(new[] { n, upper, next, next, upper, upperNext });
                }
            }
        }
        Mesh m = new Mesh { vertices = v.ToArray(), triangles = t.ToArray() };
        m.RecalculateNormals(); m.RecalculateBounds();
        return SaveMesh("RPF_PalmTrunk", m);
    }

    static Mesh MakeFronds()
    {
        var v = new List<Vector3>(); var uv = new List<Vector2>(); var t = new List<int>();
        const int fronds = 9, segments = 10;
        for (int f = 0; f < fronds; f++)
        {
            float angle = Mathf.PI * 2f * f / fronds;
            Vector3 radial = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle));
            Vector3 side = new Vector3(-radial.z, 0f, radial.x);
            int start = v.Count;
            for (int s = 0; s <= segments; s++)
            {
                float q = (float)s / segments;
                float radius = Mathf.Lerp(.18f, 2.8f, q);
                float height = .35f - q * q * 1.35f;
                float width = Mathf.Lerp(.05f, .28f, Mathf.Sin(Mathf.PI * q));
                Vector3 center = radial * radius + Vector3.up * height;
                v.Add(center - side * width);
                v.Add(center + side * width);
                uv.Add(new Vector2(0f, q)); uv.Add(new Vector2(1f, q));
                if (s < segments)
                {
                    int a = start + s * 2, b = a + 2;
                    t.AddRange(new[] { a, b, a + 1, a + 1, b, b + 1 });
                    t.AddRange(new[] { a + 1, b, a, b + 1, b, a + 1 });
                }
            }
        }
        Mesh m = new Mesh { vertices = v.ToArray(), uv = uv.ToArray(), triangles = t.ToArray() };
        m.RecalculateNormals(); m.RecalculateBounds();
        return SaveMesh("RPF_PalmFronds", m);
    }

    static MeshFilter AddMesh(string name, Mesh mesh, Material material, Transform parent)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent, false);
        var filter = go.AddComponent<MeshFilter>();
        filter.sharedMesh = mesh;
        var renderer = go.AddComponent<MeshRenderer>();
        renderer.sharedMaterial = material;
        renderer.shadowCastingMode = ShadowCastingMode.On;
        renderer.receiveShadows = true;
        go.isStatic = true;
        return filter;
    }

    static void Box(string name, Vector3 center, Vector3 size, Material material, Transform parent, bool rotate = true)
    {
        var f = AddMesh(name, cube, material, parent);
        f.transform.SetPositionAndRotation(center, rotate ? Quaternion.Euler(0f, Yaw, 0f) : Quaternion.identity);
        f.transform.localScale = size;
    }

    static void AddQuad(List<Vector3> v, List<int> t, float c0, float c1, float a0, float a1, float y)
    {
        int n = v.Count;
        v.Add(P(c0, a0, y)); v.Add(P(c1, a0, y)); v.Add(P(c1, a1, y)); v.Add(P(c0, a1, y));
        t.AddRange(new[] { n, n + 1, n + 2, n, n + 2, n + 3 });
    }

    static void CreatePaverStrip(Transform root, Material[] palette)
    {
        var verts = new List<Vector3>(); var uv = new List<Vector2>();
        var sub = new[] { new List<int>(), new List<int>(), new List<int>() };
        const float startC = -401.45f, depth = 2.55f, startA = -39.25f, endA = 259.25f;
        const float tileA = .88f, gapA = .055f, tileC = .57f, gapC = .055f;
        int cols = Mathf.FloorToInt((endA - startA) / (tileA + gapA));
        int rows = Mathf.FloorToInt(depth / (tileC + gapC));
        for (int row = 0; row < rows; row++)
        for (int col = 0; col < cols; col++)
        {
            float a0 = startA + col * (tileA + gapA), a1 = a0 + tileA;
            float c0 = startC + row * (tileC + gapC), c1 = Mathf.Min(startC + depth, c0 + tileC);
            int paletteIndex = ((col + row * 3) % 13 < 8) ? 0 : ((col + row) % 2 == 0 ? 1 : 2);
            int first = verts.Count;
            AddQuad(verts, sub[paletteIndex], c0, c1, a0, a1, .105f);
            uv.AddRange(new[] { Vector2.zero, Vector2.right, Vector2.one, Vector2.up });
        }
        var mesh = new Mesh { name = "RPF_CoastalWalkwayTiles", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
        mesh.SetVertices(verts); mesh.SetUVs(0, uv);
        mesh.subMeshCount = 3;
        for (int i = 0; i < 3; i++) mesh.SetTriangles(sub[i], i);
        mesh.RecalculateNormals(); mesh.RecalculateBounds();
        mesh = SaveMesh("RPF_CoastalWalkwayTiles", mesh);
        var filter = AddMesh("RPF_CoastalWalkway", mesh, palette[0], root);
        filter.GetComponent<MeshRenderer>().sharedMaterials = palette;
    }

    static Dictionary<string, Building> ScanBuildings(Scene scene)
    {
        var result = new Dictionary<string, Building>();
        foreach (var root in scene.GetRootGameObjects())
        foreach (var r in root.GetComponentsInChildren<MeshRenderer>(true))
        {
            string marker = "_Clipped_";
            int begin = r.name.IndexOf(marker, StringComparison.Ordinal);
            int split = r.name.IndexOf("__", begin < 0 ? 0 : begin, StringComparison.Ordinal);
            if (begin < 0 || split < 0) continue;
            string key = r.name.Substring(begin + marker.Length, split - begin - marker.Length);
            if (!(key.StartsWith("cop_", StringComparison.Ordinal) || key.StartsWith("cop", StringComparison.Ordinal))) continue;
            if (!result.TryGetValue(key, out var b)) result[key] = b = new Building { key = key };
            Bounds bounds = r.bounds;
            for (int mask = 0; mask < 8; mask++)
            {
                Vector3 p = new Vector3((mask & 1) == 0 ? bounds.min.x : bounds.max.x,
                                        (mask & 2) == 0 ? bounds.min.y : bounds.max.y,
                                        (mask & 4) == 0 ? bounds.min.z : bounds.max.z);
                float c = p.x * Cos - p.z * Sin;
                float a = -p.x * Sin - p.z * Cos;
                b.c0 = Mathf.Min(b.c0, c); b.c1 = Mathf.Max(b.c1, c);
                b.a0 = Mathf.Min(b.a0, a); b.a1 = Mathf.Max(b.a1, a);
                b.y0 = Mathf.Min(b.y0, p.y); b.y1 = Mathf.Max(b.y1, p.y);
            }
        }
        return result;
    }

    static Material WallFor(Building b)
    {
        int h = StableHash(b.key);
        if (b.key.Contains("hotel") || b.key.Contains("art_deco")) return Mats[(h % 2 == 0) ? "Facade_Cream" : "Facade_Seafoam"];
        if (b.key.Contains("historico")) return Mats[(h % 2 == 0) ? "Facade_CoralWash" : "Facade_Cream"];
        if (b.key.Contains("misto_loja")) return Mats[(h % 2 == 0) ? "Facade_Peach" : "Facade_Seafoam"];
        return Mats[(h % 3 == 0) ? "Facade_Cream" : ((h % 3 == 1) ? "Facade_Peach" : "Facade_Seafoam")];
    }

    static void StyleBuildings(Scene scene)
    {
        foreach (var root in scene.GetRootGameObjects())
        foreach (var r in root.GetComponentsInChildren<MeshRenderer>(true))
        {
            string marker = "_Clipped_";
            int begin = r.name.IndexOf(marker, StringComparison.Ordinal);
            int split = r.name.IndexOf("__", begin < 0 ? 0 : begin, StringComparison.Ordinal);
            if (begin < 0 || split < 0) continue;
            string key = r.name.Substring(begin + marker.Length, split - begin - marker.Length);
            if (!(key.StartsWith("cop_", StringComparison.Ordinal) || key.StartsWith("cop", StringComparison.Ordinal))) continue;
            string part = r.name.Substring(split + 2);
            Material target = null;
            if (part.StartsWith("wall", StringComparison.Ordinal))
                target = WallFor(new Building { key = key });
            else if (part.StartsWith("glass", StringComparison.Ordinal))
                target = Mats["Glass_Turquoise"];
            else if (part.StartsWith("stone", StringComparison.Ordinal) || part.StartsWith("roof", StringComparison.Ordinal))
                target = part.StartsWith("roof", StringComparison.Ordinal) ? Mats["Roof_Terracotta"] : Mats["Stone_Warm"];
            else if (part.StartsWith("trim", StringComparison.Ordinal) || part.StartsWith("cornices", StringComparison.Ordinal) || part.StartsWith("balcony", StringComparison.Ordinal))
                target = Mats[key.Contains("hotel") || key.Contains("art_deco") ? "Trim_SeaTeal" : "Trim_Cream"];
            else if (part.StartsWith("metal", StringComparison.Ordinal))
                target = Mats["Metal_Bronze"];
            if (target == null) continue;
            // Tint the existing authored materials through a property block so their
            // albedo and normal maps stay connected for a more convincing PBR finish.
            Color tint = target.HasProperty("_BaseColor") ? target.GetColor("_BaseColor") :
                         (target.HasProperty("_Color") ? target.GetColor("_Color") : Color.white);
            var block = new MaterialPropertyBlock();
            r.GetPropertyBlock(block);
            block.SetColor("_BaseColor", tint);
            block.SetColor("_Color", tint);
            r.SetPropertyBlock(block);
        }
    }

    static void AddFacadeDetails(Dictionary<string, Building> buildings, Transform root, ref int awnings)
    {
        int index = 0;
        foreach (var b in buildings.Values.OrderBy(x => x.key, StringComparer.Ordinal))
        {
            float span = b.a1 - b.a0, height = b.y1 - b.y0;
            if (span < 5f || height < 5f || !Finite(b.c0) || b.c0 < -400f || b.c0 > -370f) continue;
            float front = b.c0 - .11f;
            Material trim = b.key.Contains("hotel") || b.key.Contains("art_deco") ? Mats["Trim_SeaTeal"] : Mats["Trim_Cream"];
            float edge = Mathf.Min(span * .22f, 3.2f);
            Box("RPF_Facade_Pilaster_L_" + index, P(front, b.a0 + edge, (b.y0 + b.y1) * .5f), new Vector3(.20f, height * .88f, .13f), trim, root);
            Box("RPF_Facade_Pilaster_R_" + index, P(front, b.a1 - edge, (b.y0 + b.y1) * .5f), new Vector3(.20f, height * .88f, .13f), trim, root);
            if (span < 65f)
                Box("RPF_Facade_Cornice_" + index, P(front, (b.a0 + b.a1) * .5f, b.y1 - .25f), new Vector3(Mathf.Max(3f, span - .4f), .18f, .14f), trim, root);
            if (b.key.Contains("misto_loja"))
            {
                int count = Mathf.Clamp(Mathf.FloorToInt(span / 11f), 1, 4);
                for (int n = 0; n < count; n++)
                {
                    float a = Mathf.Lerp(b.a0 + 2f, b.a1 - 2f, (n + .5f) / count);
                    float w = Mathf.Min(5.2f, (span - 2f) / count);
                    float c = front - .48f;
                    for (int stripe = 0; stripe < 8; stripe++)
                    {
                        float sa = a - w * .5f + w * (stripe + .5f) / 8f;
                        Material cloth = stripe % 2 == 0 ? Mats["Awning_Coral"] : Mats["Awning_Cream"];
                        Box("RPF_AwningStripe_" + index + "_" + n + "_" + stripe, P(c, sa, b.y0 + 3.1f), new Vector3(w / 8f + .015f, .14f, 1.25f), cloth, root);
                    }
                    Box("RPF_AwningValance_" + index + "_" + n, P(c - .62f, a, b.y0 + 2.73f), new Vector3(w, .42f, .12f), Mats["Awning_Coral"], root);
                    Box("RPF_AwningSign_" + index + "_" + n, P(front - .18f, a, b.y0 + 3.62f), new Vector3(w * .62f, .38f, .09f), Mats["Sign_SeaTeal"], root);
                    awnings++;
                }
            }
            index++;
        }
    }

    static bool Finite(float x) { return !float.IsNaN(x) && !float.IsInfinity(x); }

    static void AddPalm(float c, float a, int index, Transform root)
    {
        var go = new GameObject("RPF_Palm_" + index);
        go.transform.SetParent(root, false);
        go.transform.position = P(c, a, .12f);
        Box("RPF_PalmPlanter_" + index, P(c, a, .24f), new Vector3(1.7f, .42f, 1.55f), Mats["Planter_Seafoam"], root);
        var trunk = AddMesh("RPF_PalmTrunk_" + index, palmTrunk, Mats["Palm_Trunk"], go.transform);
        trunk.transform.localPosition = Vector3.zero;
        var leaves = AddMesh("RPF_PalmFronds_" + index, palmLeaves, Mats["Palm_Leaf"], go.transform);
        leaves.transform.localPosition = new Vector3(.12f, 4.45f, 0f);
        for (int n = 0; n < 4; n++)
        {
            float angle = n * Mathf.PI * .5f;
            var shrub = AddMesh("RPF_PlanterLeaf_" + index + "_" + n, sphere, Mats[n % 2 == 0 ? "Palm_Leaf" : "Palm_Leaf_Light"], go.transform);
            shrub.transform.localPosition = new Vector3(Mathf.Cos(angle) * .48f, .42f, Mathf.Sin(angle) * .42f);
            shrub.transform.localScale = new Vector3(.7f, .34f, .7f);
        }
    }

    static void AddBench(float c, float a, int i, Transform root)
    {
        Quaternion q = Quaternion.Euler(0f, Yaw, 0f);
        Box("RPF_BenchSeat_" + i, P(c, a, .48f), new Vector3(1.9f, .12f, .52f), Mats["Wood_Honey"], root);
        Box("RPF_BenchBack_" + i, P(c + .18f, a, .92f), new Vector3(1.9f, .72f, .12f), Mats["Wood_Honey"], root);
        Box("RPF_BenchLegA_" + i, P(c, a - .72f, .25f), new Vector3(.12f, .5f, .12f), Mats["Metal_Bronze"], root);
        Box("RPF_BenchLegB_" + i, P(c, a + .72f, .25f), new Vector3(.12f, .5f, .12f), Mats["Metal_Bronze"], root);
    }

    static void AddStreetLight(float c, float a, int i, Transform root)
    {
        Box("RPF_LightPost_" + i, P(c, a, 2.0f), new Vector3(.12f, 4f, .12f), Mats["Metal_Bronze"], root);
        Box("RPF_LightArm_" + i, P(c - .34f, a, 3.85f), new Vector3(.7f, .08f, .09f), Mats["Metal_Bronze"], root);
        Box("RPF_LightLantern_" + i, P(c - .67f, a, 3.72f), new Vector3(.32f, .18f, .32f), Mats["Light_Warm"], root);
    }

    static void AddKiosk(float c, float a, Transform root)
    {
        Box("RPF_KioskBase", P(c, a, 1.12f), new Vector3(2.8f, 2.12f, 2.25f), Mats["Kiosk_Seafoam"], root);
        Box("RPF_KioskCounter", P(c - .94f, a, 1.04f), new Vector3(2.85f, .18f, .38f), Mats["Stone_Warm"], root);
        for (int i = 0; i < 7; i++)
        {
            Material stripe = i % 2 == 0 ? Mats["Awning_Coral"] : Mats["Awning_Cream"];
            Box("RPF_KioskCanopyStripe_" + i, P(c, a - 1.55f + i * .46f, 2.34f), new Vector3(.48f, .20f, 3.6f), stripe, root);
        }
        Box("RPF_KioskSign", P(c - .03f, a, 2.62f), new Vector3(2.6f, .35f, .12f), Mats["Sign_SeaTeal"], root);
        Box("RPF_KioskShelf", P(c - 1.38f, a, 1.55f), new Vector3(.16f, .8f, 2.4f), Mats["Wood_Honey"], root);
    }

    static void TuneLighting()
    {
        if (RenderSettings.skybox != null)
        {
            Material sky = AssetDatabase.LoadAssetAtPath<Material>(MaterialRoot + "/Sky_PremiumPanoramic.mat");
            if (sky == null)
            {
                sky = new Material(RenderSettings.skybox);
                sky.name = "Sky_PremiumPanoramic";
                AssetDatabase.CreateAsset(sky, MaterialRoot + "/Sky_PremiumPanoramic.mat");
            }
            if (sky.HasProperty("_Exposure")) sky.SetFloat("_Exposure", .46f);
            if (sky.HasProperty("_Tint")) sky.SetColor("_Tint", new Color(.68f, .82f, .96f, 1f));
            RenderSettings.skybox = sky;
            RenderSettings.ambientIntensity = .78f;
        }
        Light sun = RenderSettings.sun;
        if (sun == null)
            sun = UnityEngine.Object.FindObjectsOfType<Light>(true).FirstOrDefault(x => x.type == LightType.Directional);
        if (sun != null)
        {
            sun.color = new Color(1f, .91f, .78f);
            sun.intensity = 1.05f;
            sun.shadows = LightShadows.Soft;
        }
    }

    static void CreateMaterials()
    {
        Mat("Facade_Cream", new Color(.91f, .78f, .59f), .68f);
        Mat("Facade_Peach", new Color(.88f, .57f, .43f), .66f);
        Mat("Facade_Seafoam", new Color(.43f, .73f, .64f), .66f);
        Mat("Facade_CoralWash", new Color(.81f, .48f, .39f), .66f);
        Mat("Glass_Turquoise", new Color(.19f, .53f, .55f), .62f, .12f);
        Mat("Trim_SeaTeal", new Color(.05f, .31f, .31f), .48f, .18f);
        Mat("Trim_Cream", new Color(.96f, .83f, .63f), .52f);
        Mat("Stone_Warm", new Color(.78f, .67f, .51f), .82f);
        Mat("Metal_Bronze", new Color(.13f, .22f, .20f), .58f, .32f);
        Mat("Roof_Terracotta", new Color(.63f, .23f, .16f), .6f);
        Mat("Awning_Coral", new Color(.91f, .29f, .20f), .45f);
        Mat("Awning_Cream", new Color(.98f, .82f, .58f), .45f);
        Mat("Sign_SeaTeal", new Color(.025f, .24f, .25f), .5f);
        Mat("Planter_Seafoam", new Color(.22f, .56f, .49f), .45f);
        Mat("Kiosk_Seafoam", new Color(.22f, .56f, .49f), .5f);
        Mat("Wood_Honey", new Color(.52f, .29f, .13f), .48f);
        Mat("Palm_Trunk", new Color(.47f, .30f, .16f), .68f);
        Mat("Palm_Leaf", new Color(.08f, .40f, .22f), .36f);
        Mat("Palm_Leaf_Light", new Color(.26f, .57f, .25f), .34f);
        Mat("Light_Warm", new Color(1f, .72f, .35f), .3f);
        Mat("Path_Limestone", new Color(.88f, .77f, .58f), .7f);
        Mat("Path_Coral", new Color(.72f, .25f, .18f), .58f);
        Mat("Path_Teal", new Color(.04f, .34f, .33f), .55f);
    }

    static void Build()
    {
        string sourcePath = Path.GetFullPath(Path.Combine(Application.dataPath, "..", SourceScene));
        string sourceHash = Hash(sourcePath);
        EnsureFolder(AssetRoot); EnsureFolder(MeshRoot); EnsureFolder(MaterialRoot);
        cube = MakeCube(); sphere = MakeSphere(); palmTrunk = MakeTrunk(); palmLeaves = MakeFronds();
        CreateMaterials();
        AssetDatabase.SaveAssets();
        bool outputExists = AssetDatabase.LoadAssetAtPath<SceneAsset>(OutputScene) != null;
        Scene scene = EditorSceneManager.OpenScene(outputExists ? OutputScene : SourceScene, OpenSceneMode.Single);
        var oldRoot = scene.GetRootGameObjects().FirstOrDefault(x => x.name == RootName);
        if (oldRoot != null) UnityEngine.Object.DestroyImmediate(oldRoot);
        if (!outputExists)
        {
            string fullOutput = Path.GetFullPath(Path.Combine(Application.dataPath, "..", OutputScene));
            Need(EditorSceneManager.SaveScene(scene, fullOutput), "SAVE_NEW_SCENE_FAILED");
            scene = EditorSceneManager.OpenScene(OutputScene, OpenSceneMode.Single);
        }
        var visualRoot = new GameObject(RootName);
        var walkwayRoot = new GameObject("RPF_Walkway");
        walkwayRoot.transform.SetParent(visualRoot.transform, false);
        var facadeRoot = new GameObject("RPF_FacadeDetails");
        facadeRoot.transform.SetParent(visualRoot.transform, false);
        var propsRoot = new GameObject("RPF_StreetFurniture");
        propsRoot.transform.SetParent(visualRoot.transform, false);

        int baseRenderers = scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<MeshRenderer>(true)).Count();
        var buildings = ScanBuildings(scene);
        StyleBuildings(scene);
        CreatePaverStrip(walkwayRoot.transform, new[] { Mats["Path_Limestone"], Mats["Path_Coral"], Mats["Path_Teal"] });
        int awnings = 0;
        AddFacadeDetails(buildings, facadeRoot.transform, ref awnings);
        int palms = 0, benches = 0, lights = 0;
        float[] positions = { -16f, 32f, 80f, 128f, 176f, 224f, 252f };
        for (int i = 0; i < positions.Length; i++)
        {
            AddPalm(-396.5f, positions[i], i, propsRoot.transform);
            palms++;
        }
        for (int i = 0; i < 5; i++)
        {
            float a = 8f + i * 58f;
            AddBench(-395.25f, a, i, propsRoot.transform);
            benches++;
        }
        for (int i = 0; i < 5; i++)
        {
            float a = 2f + i * 61f;
            AddStreetLight(-398.25f, a, i, propsRoot.transform);
            lights++;
        }
        AddKiosk(-397.3f, 147f, propsRoot.transform);
        TuneLighting();
        EditorSceneManager.MarkSceneDirty(scene);
        AssetDatabase.SaveAssets();
        Need(EditorSceneManager.SaveScene(scene), "SAVE_SCENE_FAILED");
        string finalHash = Hash(sourcePath);
        Need(sourceHash == finalHash, "SOURCE_SCENE_CHANGED");
        int finalRenderers = scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<MeshRenderer>(true)).Count();
        var report = new Report {
            status = "VISUAL_FINISH_BUILT_REQUIRES_NATIVE_REVIEW",
            source_scene = SourceScene, destination_scene = OutputScene,
            unity = Application.unityVersion, renderer = SystemInfo.graphicsDeviceType.ToString(),
            gpu = SystemInfo.graphicsDeviceName, source_sha256 = sourceHash,
            base_renderers = baseRenderers, final_renderers = finalRenderers,
            building_families = buildings.Count, awnings = awnings, palms = palms,
            planters = palms, benches = benches, lights = lights,
            width_m = 300f, depth_m = 300f,
            source_unchanged = sourceHash == finalHash,
            skybox_preserved = RenderSettings.skybox != null && RenderSettings.skybox.shader.name == "Skybox/Panoramic",
            original_scenes_preserved = AssetDatabase.LoadAssetAtPath<SceneAsset>(SourceScene) != null,
            fps_measured = false, art_approved = false,
            views = new[] { "Pedestrian promenade-to-city", "Mixed-use facade detail", "Beachfront street", "Aerial composition" }
        };
        string reportPath = Path.GetFullPath(Path.Combine(Application.dataPath, "../../evidence/visual_finish_build.json"));
        Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
        File.WriteAllText(reportPath, JsonUtility.ToJson(report, true));
        Debug.Log("VISUAL_FINISH_BUILD_PASS scene=" + OutputScene + " buildings=" + buildings.Count +
                  " awnings=" + awnings + " palms=" + palms + " renderers=" + finalRenderers);
    }

    [MenuItem("Resort/Visual Finish/Build tropical premium scene")]
    public static void RunMenu() { Build(); }

    public static void BuildFromBatchmode() { Build(); }
}