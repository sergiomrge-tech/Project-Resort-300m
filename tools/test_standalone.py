"""Portable static gates; Unity/GPU results are recorded separately, never inferred."""
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'UnityProject'
LEGACY = re.compile(r'R(?:[1-9]|1[0-4])(?:[_/\.])', re.I)

class StandaloneTests(unittest.TestCase):
    def test_complete_project(self):
        for file in ['Packages/manifest.json', 'Packages/packages-lock.json',
                     'ProjectSettings/ProjectVersion.txt', 'Assets/Scenes/ProjectResort_300m.unity']:
            self.assertTrue((PROJECT / file).is_file(), file)
        self.assertIn('6000.6.2f1', (PROJECT / 'ProjectSettings/ProjectVersion.txt').read_text())
        manifest = json.loads((PROJECT / 'Packages/manifest.json').read_text())
        self.assertEqual('17.6.0', manifest['dependencies']['com.unity.render-pipelines.universal'])
        self.assertFalse(any('file:' in x for x in manifest['dependencies'].values()))

    def test_assets_have_unique_guids_and_no_legacy(self):
        guids = {}
        for p in (PROJECT / 'Assets').rglob('*'):
            self.assertFalse(p.is_symlink(), str(p))
            self.assertFalse(LEGACY.search(p.as_posix()), str(p))
            if not p.is_file():
                continue
            self.assertLess(p.stat().st_size, 100_000_000, str(p))
            if p.suffix == '.meta':
                guid = re.search(r'^guid: ([0-9a-f]{32})$', p.read_text(), re.M)
                self.assertIsNotNone(guid, str(p))
                self.assertNotIn(guid[1], guids, str(p))
                guids[guid[1]] = p
            else:
                self.assertTrue(Path(str(p)+'.meta').is_file(), str(p))
                self.assertNotEqual('.fbx', p.suffix.lower(), str(p))
        self.assertGreater(len(guids), 400)

    def test_hash_manifest(self):
        manifest = json.loads((ROOT / 'evidence/files_sha256.json').read_text())
        files = {p.relative_to(ROOT).as_posix() for p in PROJECT.rglob('*')
                 if p.is_file() and not any(x in p.parts for x in ('Library','Logs','Temp','UserSettings','obj'))}
        self.assertEqual(files, set(manifest))
        for path, sha in manifest.items():
            self.assertEqual(sha, hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), path)

    def test_all_serialized_guid_references(self):
        mapping = {}
        for row in (ROOT / 'evidence/guid_resolution.tsv').read_text().splitlines():
            guid, path = row.split('\t')
            if guid != 'guid':
                mapping[guid] = path
        guids = {re.search(r'^guid: ([a-f0-9]{32})$', p.read_text(), re.M)[1]
                 for p in (PROJECT / 'Assets').rglob('*.meta')}
        for folder in ('Assets','ProjectSettings'):
            for p in (PROJECT / folder).rglob('*'):
                if not p.is_file() or p.suffix == '.meta':
                    continue
                for guid in re.findall(rb'guid: ([a-f0-9]{32})', p.read_bytes()):
                    guid = guid.decode()
                    if guid.startswith('0000000000000000'):
                        continue
                    self.assertIn(guid, mapping, str(p))
                    path = mapping[guid]
                    if path.startswith('Assets/'):
                        self.assertIn(guid, guids, str(p))
                        self.assertTrue((PROJECT / path).is_file(), path)
                    else:
                        self.assertTrue(path.startswith('Packages/'), path)
                    self.assertFalse(LEGACY.search(path), path)

    def test_unity_dependency_closure_and_crop(self):
        qa = json.loads((ROOT / 'evidence/standalone_qa.json').read_text())
        self.assertEqual(300, qa['width_m'])
        self.assertEqual(300, qa['depth_m'])
        self.assertEqual(1, qa['units_per_meter'])
        self.assertGreaterEqual(qa['min_observed_x'], -510.02)
        self.assertLessEqual(qa['max_observed_x'], -209.98)
        self.assertGreaterEqual(qa['min_observed_y'], -40.02)
        self.assertLessEqual(qa['max_observed_y'], 260.02)
        self.assertEqual(380, qa['renderers'])
        self.assertEqual(380, qa['meshes'])
        self.assertEqual(0, qa['missing_scripts'])
        self.assertTrue(qa['skybox_assigned'])
        self.assertEqual('Direct3D11', qa['renderer'])
        scene = PROJECT / 'Assets/Scenes/ProjectResort_300m.unity'
        self.assertEqual(qa['scene_sha256'], hashlib.sha256(scene.read_bytes()).hexdigest())
        for path in qa['dependencies']:
            self.assertTrue(path == 'Assets/Scenes/ProjectResort_300m.unity' or path.startswith('Assets/R15/'), path)
            self.assertTrue((PROJECT / path).is_file(), path)
            self.assertFalse(LEGACY.search(path), path)
        self.assertEqual(4, qa['box_colliders'])
        self.assertGreater(qa['ground_hits'], 0)

    def test_real_capture_hashes_and_coverage(self):
        qa = json.loads((ROOT / 'evidence/standalone_qa.json').read_text())
        self.assertGreaterEqual(len(qa['captures']), 4)
        for shot in qa['captures']:
            blob = (ROOT / 'evidence' / shot['filename']).read_bytes()
            self.assertEqual(b'\x89PNG\r\n\x1a\n', blob[:8])
            self.assertEqual((1600,900), struct.unpack('>II', blob[16:24]))
            self.assertEqual(shot['sha256'], hashlib.sha256(blob).hexdigest())
            self.assertGreater(shot['pixel_span'], 75)
            self.assertLess(shot['magenta_pixels'], 1440)
        self.assertEqual(4, len({s['sha256'] for s in qa['captures']}))
        self.assertFalse(qa['fps_measured'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
