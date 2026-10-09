"""Upgrade the project-owned local sand shader to the URP PBR lighting model."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
paths = list((root / 'UnityProject/Assets/R15/Shaders').glob('*Pass2Sand.shader'))
if len(paths) != 1:
    raise RuntimeError(f'Expected one sand shader, got {paths}')
path = paths[0]
source = path.read_text()
old = '''    Light sun=GetMainLight(TransformWorldToShadowCoord(v.world));
    half3 diffuse=albedo*(max(SampleSH(n),0)+sun.color*saturate(dot(n,sun.direction))*sun.shadowAttenuation);
    return half4(MixFog(diffuse,v.fog),1);'''
new = '''    // Local R15 refinement: dielectric sand, smoother and darker when wet.
    InputData input=(InputData)0;
    input.positionWS=v.world;
    input.normalWS=n;
    input.viewDirectionWS=GetWorldSpaceNormalizeViewDir(v.world);
    input.shadowCoord=TransformWorldToShadowCoord(v.world);
    input.bakedGI=SampleSH(n);
    input.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(v.positionCS);
    input.shadowMask=half4(1,1,1,1);
    SurfaceData surface=(SurfaceData)0;
    surface.albedo=albedo*.88;
    surface.metallic=0;
    surface.specular=half3(.04,.04,.04);
    surface.smoothness=lerp(.48,.12,dry);
    surface.normalTS=half3(0,0,1);
    surface.occlusion=1;
    surface.alpha=1;
    half4 color=UniversalFragmentPBR(input,surface);
    return half4(MixFog(color.rgb,v.fog),1);'''
if old not in source:
    if new in source:
        print('Sand PBR already applied')
    else:
        raise RuntimeError('Sand shader changed; inspect before replacing')
else:
    path.write_text(source.replace(old, new), encoding='utf-8')
    print('Applied URP PBR to local dry/wet sand shader')
