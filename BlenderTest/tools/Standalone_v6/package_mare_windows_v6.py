from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone

root = Path(r'D:\ProjectResort_300m_CompactPass')
build = root / 'Builds' / 'Mare_Windows_v6'
exe = build / 'ProjectResort_Mare.exe'
assert exe.is_file(), 'Build executable missing'
report = json.loads((build / 'build_report.json').read_text(encoding='utf-8-sig'))
assert report['result'] == 'Succeeded', report
readme = '''PROJECT RESORT — MARÉ | PRÉVIA EXECUTÁVEL v0.6

Windows 64 bits / Direct3D11 / Unity 6000.6.2f1
Abra ProjectResort_Mare.exe. Não exige instalar Unity ou Blender.
Mantenha o EXE junto com ProjectResort_Mare_Data, UnityPlayer.dll e
as demais pastas e bibliotecas desta distribuição.

CONTROLES
WASD: deslocar a câmera. Q/E: descer/subir.
Botão direito segurado + mouse: olhar. Shift: acelerar.
F1: orla; F2: recepção; F3: suíte; F4: restaurante; F5: aérea.
Page Up/Page Down ou botões do painel: visualizar etapas 1–20.
Tab: ocultar/exibir painel. Esc ou Sair: fechar.

CONTEÚDO
Mapa integrado de 2 km × 1 km, resort e interiores provenientes do Blender.
Prévia visual de 20 etapas conectadas da evolução arquitetônica.
MSAA 4x + SMAA High na configuração gráfica Desktop.

ESTADO DE DESENVOLVIMENTO
Esta versão permite explorar a arquitetura usando câmera livre.
Não inclui compras, economia, hóspedes, saves ou interação com objetos.
A câmera livre atravessa paredes; não é um controlador de caminhada.
O mapa ainda tem alta densidade geométrica e precisa de otimização com LODs.
O limite de 60 quadros é apenas uma configuração, sem garantia de FPS.
As capturas de validação foram geradas pelo Player real e estão em Evidence.

Reprodução do build no Editor: BuildMareWindows.Prepare() e .Build().
Cena: Assets/Scenes/ProjectResort_Mare_StandalonePreview.unity.
A cena principal original foi preservada.
'''
(build / 'LEIA-ME.txt').write_text(readme, encoding='utf-8')
tool_dir = root / 'BlenderTest' / 'tools' / 'Standalone_v6'
tool_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(__file__, tool_dir / Path(__file__).name)
shutil.copy2(Path(__file__).with_name('BuildMareWindows.cs'), tool_dir / 'BuildMareWindows.cs')
project=root/'UnityProject'
shutil.copy2(project/'Assets/TextMesh Pro/Fonts/LiberationSans - OFL.txt',build/'LiberationSans - OFL.txt')
source_paths=[project/'Packages/manifest.json',project/'Packages/packages-lock.json',project/'ProjectSettings/ProjectSettings.asset',project/'Assets/Scenes/ProjectResort_Mare_StandalonePreview.unity',project/'Assets/Scenes/ProjectResort_Mare_StandalonePreview.unity.meta',project/'Assets/R15/BlenderIntegrated/Runtime.meta']
source_paths += list((project/'Assets/R15/BlenderIntegrated/Runtime').rglob('*'))
source_paths += list((project/'Assets/TextMesh Pro').rglob('*'))
source_paths += [project/'Assets/TextMesh Pro.meta',project/'Assets/R15/BlenderIntegrated/Editor/BuildMareWindows.cs',project/'Assets/R15/BlenderIntegrated/Editor/BuildMareWindows.cs.meta']
source_records=[]
for path in sorted(set(source_paths)):
    if path.is_file(): source_records.append({'path':path.relative_to(project).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
main=project/'Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity'
main_hash=hashlib.sha256(main.read_bytes()).hexdigest()
assert main_hash=='468261f847e310ac8bdff143f7b23fa628deb42315da184a302bab3eed2784bd','Main scene changed'
(root/'BlenderTest/mare_standalone_hashes_v6.json').write_text(json.dumps({'version':6,'base_manifest':'mare_antialiasing_hashes_v5.json','main_scene_preserved':True,'main_scene_sha256':main_hash,'unity_files':source_records},indent=2),encoding='utf-8')
records=[]
for path in sorted(build.rglob('*')):
    if path.is_file() and path.name != 'distribution_manifest.json':
        h=hashlib.sha256()
        with path.open('rb') as src:
            for block in iter(lambda:src.read(4*1024*1024),b''): h.update(block)
        records.append({'path':path.relative_to(build).as_posix(),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
(build / 'distribution_manifest.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'build':report,'files':records},indent=2),encoding='utf-8')
zip_path=build.parent / 'ProjectResort_Mare_Windows_v6.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as archive:
    for path in sorted(build.rglob('*')):
        if path.is_file(): archive.write(path,path.relative_to(build.parent).as_posix())
print(json.dumps({'executable':str(exe),'zip':str(zip_path),'zip_bytes':zip_path.stat().st_size,'files':len(records),'uncompressed_bytes':sum(x['bytes'] for x in records)}))
