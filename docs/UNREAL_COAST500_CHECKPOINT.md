# Checkpoint Unreal — 10/10/2026

A versão ativa é Unreal Engine 5.8.3, projeto `UnrealProject/ProjectResortUE.uproject`.
Mapa de abertura: `/Game/Resort/Maps/Resort_HalfWest`.
Área atual: **1.000 × 500 metros**, preservando a orla e o resort.

## Conteúdo publicado

- Projeto, configurações e assets locais da Unreal, incluindo materiais/texturas, colisões, Nanite e personagem Third Person de exploração.
- Fonte Blender principal `BlenderTest/Resort_Main_Map_Mare_Houses_v7.blend`, com texturas empacotadas. Este arquivo é a base de autoria anterior de 2 × 1 km; o recorte atual de 1 × 0,5 km está aplicado nas malhas e no nível Unreal.
- Scripts e descrições das 20 etapas arquitetônicas no Blender. A evolução/compras dessas etapas ainda não está implementada no runtime Unreal.
- Ferramentas de exportação, recorte e importação; relatórios e capturas reais em `evidence/unreal_coast500`.
- Modelos/assets binários distribuídos por Git LFS. Caches, builds, cópias de segurança `.blend1` e FBX intermediários não são necessários para abrir o nível salvo e não integram este checkpoint.

## Como abrir

```powershell
git clone --branch codex/r15-close-proximity-beach-city https://github.com/sergiomrge-tech/Project-Resort-300m.git
cd Project-Resort-300m
git lfs pull
```

Abra `UnrealProject/ProjectResortUE.uproject` na Unreal 5.8.3. A engine e seus plugins de Editor precisam estar instalados; não fazem parte do repositório. O nível costeiro reduzido é configurado para abrir automaticamente. Use Play para explorar com o personagem padrão.

Para reconstruir as malhas, os scripts atuais usam o caminho de trabalho Windows `D:/ProjectResort_300m_CompactPass`; adapte-o caso o clone esteja em outro local. O exportador Blender produz os setores de 200 m, `extract_blender_pbr.py` extrai materiais/superfícies e `crop_coast500.py` faz o corte. A importação final é feita por `build_coast500.py` dentro do Editor Unreal. Os intermediários em `SourceArt` devem ser regenerados antes de executar essa rotina.

## Verificações reais

- Nível salvo no pacote correto, 16 atores de geometria e limite posterior conferido.
- Quatro sondagens de colisão atingiram o chão.
- Play In Editor iniciado; personagem criado no ponto inicial e apoiado no chão.
- Captura real de 1600 × 900 do teste, além da vista aérea do mapa.

Não há benchmark de FPS, executável Unreal validado, teste exaustivo de movimentação/interiores ou simulador completo de hóspedes/compras/saves. O próximo trabalho é melhorar a arte e portar a evolução arquitetônica para gameplay.

## Direitos e procedência

Atribuições e registros das texturas PBR: `BlenderTest/TexturesPBR_Urban/sources.json` (Poly Haven, CC0, conforme registro local). Modelo de Cristo Redentor na fonte Blender: Parlin Sitorus, CC BY 4.0, com origem/licença em `BlenderTest/AssetsExternal/cristo_source_license.json`. Isso não afirma que o Cristo esteja presente no recorte Unreal ativo. Assets do template Third Person seguem os termos da Unreal/Epic. Dados cartográficos históricos e demais atribuições: `docs/ASSET_RIGHTS.md`.

Os checkpoints Unity anteriores permanecem no histórico da branch. As alterações experimentais Unity ainda locais não foram incluídas neste checkpoint da migração Unreal.
