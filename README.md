# Project Resort — 300 × 300 m

Projeto Unity independente de um recorte real de Copacabana, com edifícios, praia, calçadão, ruas e céu tropical com nuvens. Escala preservada: **1 unidade = 1 metro**. Toda a geometria distribuída foi recortada no quadro GIS; não foi reduzida por escala.

Abra `UnityProject` no **Unity 6000.6.2f1** e a cena `Assets/Scenes/ProjectResort_300m.unity`. URP **17.6.0**, instalado pelos manifestos de Packages. Todos os meshes, materiais, texturas e shaders da cena estão neste repositório. Não são necessárias outras cópias de projetos.

Validação local executada no Unity com **Direct3D11 / RTX 4060 Ti**: 380 malhas, 370 renderizadores ativos, quatro capturas reais de 1600 × 900, zero referência a assets legados e 18/18 consultas de solo com colisão. O projeto é uma base de paisagem em desenvolvimento. **A arte ainda não foi aprovada; Player, PlayMode, NPCs, saves e FPS não foram testados.**

Para verificar os arquivos e as evidências:

```powershell
python tools/test_standalone.py
```

Para repetir a importação e a captura nativas:

```powershell
powershell -File tools/run_unity_qa.ps1
```

O script aceita `-Editor`, `-Project` e `-Output`. Requer Unity instalado e licenciado e uma GPU disponível. O CI executa os testes de integridade portáteis; não substitui o teste nativo do Editor.

Confira [QA e limitações](docs/QA_STANDALONE.md), [direitos e atribuições](docs/ASSET_RIGHTS.md), [dependências anteriores](docs/DEPENDENCIES_BEFORE.md) e o [manifesto de exclusão para o supervisor](docs/DELETE_LEGACY_MANIFEST.md). Não excluir fontes antes da confirmação de independência na nuvem.

![Calçadão e nuvens — captura real Unity](evidence/R15_01_CoastWalk_CloudyDay_RealUnity.png)

© OpenStreetMap contributors — ODbL 1.0. Arte procedural original produzida para Project Resort; veja o registro de direitos.
