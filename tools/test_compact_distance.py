"""Portable QA for independently baked immersive 300m layout; Unity proofs separately."""
import hashlib,json,re,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/"evidence/compact_native_qa.json"
VISUAL=ROOT/"evidence/compact_visual_qa.json"
PHOTO=ROOT/"evidence/compact_before_after"
SCENE=ROOT/"UnityProject/Assets/Scenes/ProjectResort_300m_Immersive.unity"
SOURCE=ROOT/"UnityProject/Assets/Scenes/ProjectResort_300m.unity"
SCRIPT=ROOT/"UnityProject/Assets/Editor/ResortCompactShoreCity.cs"

class CompactShoreTests(unittest.TestCase):
 def test_real_native_unity_proves_geometry(self):
  d=json.loads(NATIVE.read_text(encoding="utf-8-sig"))
  self.assertEqual(d["status"],"R15_SHORE_CITY_APPROACH_NATIVE_PASS_ART_REVIEW_PENDING")
  self.assertEqual(d["unity_version"],"6000.6.2f1")
  self.assertEqual((d["width_m"],d["depth_m"]),(300,300))
  self.assertEqual(d["meshes_copied"],380)
  self.assertEqual(d["colliders_updated"],347)
  self.assertEqual(d["triangle_count"],466319)
  self.assertEqual(d["material_count"],202)
  self.assertEqual(d["city_approach_m"],64)
  self.assertAlmostEqual(d["gap_before_m"],73.2,places=3)
  self.assertAlmostEqual(d["gap_after_m"],9.2,places=3)
  self.assertTrue(d["unchanged_city_geometry"])
  self.assertTrue(d["source_scene_preserved"])
  self.assertTrue(d["cloud_skybox_kept"])
  self.assertFalse(d["gameplay_playmode_tested"])
  self.assertFalse(d["artistic_gate_approved"])
  self.assertEqual(d["source_scene_sha256"],hashlib.sha256(SOURCE.read_bytes()).hexdigest())
  self.assertTrue(SCENE.exists())
  self.assertGreater(SCENE.stat().st_size,300000)
  self.assertGreaterEqual(len(list((ROOT/"UnityProject/Assets/R15/Compact/Meshes").glob("*.asset"))),380)
 def test_rigid_city_and_monotonic_gap_policy(self):
  c=SCRIPT.read_text(encoding="utf-8-sig")
  self.assertIn("KnotSea=-402f,KnotCity=-330f,Reduction=64f",c)
  self.assertIn("if(c>=KnotCity)return c-Reduction;",c)
  self.assertIn("AssetDatabase.GetDependencies(Output,true)",c)
  self.assertIn("OLD_COLLIDER_MESH_REFERENCE",c)
  self.assertIn("SOURCE_WAS_MUTATED",c)
  self.assertIn("BUILDING_GEOMETRY_WAS_SCALED",c)
  self.assertIn("Skybox/Panoramic",c)
 def test_six_authentic_gpu_pngs_matching_camera_before_after(self):
  d=json.loads(VISUAL.read_text(encoding="utf-8-sig"))
  self.assertEqual(d["status"],"R15_COMPACT_REAL_GPU_BEFORE_AFTER_PASS_VISUAL_REVIEW_PENDING")
  self.assertEqual(d["renderer"],"Direct3D11")
  self.assertEqual(len(d["captures"]),6)
  self.assertFalse(d["fps_measured"])
  self.assertFalse(d["art_approved"])
  groups={}
  for shot in d["captures"]:
   p=PHOTO/shot["filename"];raw=p.read_bytes()
   self.assertEqual(raw[:8],b"\x89PNG\r\n\x1a\n")
   self.assertEqual(struct.unpack(">II",raw[16:24]),(1600,900))
   self.assertEqual(hashlib.sha256(raw).hexdigest(),shot["sha256"])
   self.assertEqual(shot["warmup_frames"],5)
   self.assertGreater(len(raw),80000)
   groups.setdefault(shot["view"],[]).append(shot)
  self.assertEqual(len(groups),3)
  for pair in groups.values():
   self.assertEqual(len(pair),2)
   self.assertEqual(pair[0]["camera"],pair[1]["camera"])
   self.assertEqual(pair[0]["target"],pair[1]["target"])
   self.assertNotEqual(pair[0]["sha256"],pair[1]["sha256"])
if __name__=="__main__":unittest.main(verbosity=2)
