# Project Resort 300m — orla, calçadão e prédios mais próximos

**Data** 2026-10-09. **Branch de integração separada:** `codex/r15-close-proximity-beach-city` sobre o **único repositório canônico** `sergiomrge-tech/Project-Resort-300m`.

## Solicitação do usuário
Diminuir fortemente a distância entre praia, passeio, avenida e fachadas. Construir um espaço compacto e mais imersivo. A decisão autoriza ajustar **distâncias do ambiente**, então esta variação **NÃO é métrica fiel** do OSM entre calçadão e prédios — preservar a escala 1:1 de edifícios, objetos e os 300 × 300 m, não reconstruir a cidade de 2 km, não reativar Simulador Predial.

## Medição nativa dos elementos na Unity
Script `Assets/Editor/ResortCompactLayoutAudit.cs` enumera os **370 renderizadores ativos / 380 totais** e mede `cross=0.69465837*x-0.71933980*z` em metros, alinhado à direção costa-cidade:
- Mosaico: `cross` de aproximadamente **−425,6 a −402,4 m**.
- Avenida urbana, guia/sarjeta: aproximadamente **−320,4 a −290,6 m**.
- Frente construída mais próxima: aproximadamente **−329,2 m**.
- Distância transversal de referência, antes: `−329,2 - (−402,4) = 73,2 m`.
- Faixa cinza/pavimento excessivamente larga estava visível em foto real a pé.

## Modificação implementada e testada
`ResortCompactShoreCity.Run` gera uma cena NOVA `Assets/Scenes/ProjectResort_300m_Immersive.unity`; a original `ProjectResort_300m.unity` não é alterada. Para cada vértice, aplica mapa **monótono e contínuo apenas no eixo costa-cidade**:
- `cross <= −402`: praia e mosaico permanecem no lugar.
- `−402 < cross < −330`: segmento de 72 m condensado para 8 m, preservando continuidade da malha e sem buracos.
- `cross >= −330`: cidade/avenida movida rigidamente **64 metros em direção à praia**. Edifícios nessa zona NÃO são redimensionados.
- Relação de referência depois: fachada `−393,2`, mosaico `−402,4` → **9,2 m** (redução aproximada de 87% nessa medida).
- Guia com início `−320,4` passa a `−384,4`, a aproximadamente **18 m** da borda interna do calçadão. Há espaço para rua/acessos; geometrias preservadas em sua sequência topológica.
- Limites de mapa continuam **300 × 300 m**; céu com nuvens `Skybox/Panoramic` conservado.

A malha compactada é BAKED em 380 novos `Assets/R15/Compact/Meshes/R15_Compact_*.asset` independentes (preserva malhas originais da R15 até gate artístico); todos os 347 `MeshCollider` que dependem das malhas são ligados aos novos arquivos. Sem referência antiga de mesh na cena compacta; materiais e texturas são os atuais próprios da R15. Não há dependência nova de R7–R14 ou Simulador Predial.

## QA REAL, não mockup
- Unity 6000.6.2f1 / Direct3D11 no PC: **`R15_COMPACT_SHORE_CITY_NATIVE_PASS`**; 380 mesh assets, 347 colliders sincronizados, **466.319 triângulos preservados**, verificação matemática de translação rígida de todos os vértices de cidade, SHA da cena-fonte inalterado, skybox panorâmico presente. `evidence/compact_native_qa.json`.
- Seis imagens comparativas **REAL Unity GPU**, em três posições exatas, par ANTES/DEPOIS com mesma câmera, FOV 57 e cinco quadros de aquecimento. Todos os SHA-256 e dimensões PNG 1600×900 em `evidence/compact_visual_qa.json`, imagens em `evidence/compact_before_after/`.
- A foto `01_MosaicToCity_AFTER` mostra edifícios bem mais próximos, resolvendo o grande vazio cinza da foto BEFORE. A análise aérea também foi executada.
- Testes em `tools/test_compact_distance.py` validam os hashes, invariantes, contagem de colisores, ausência de escala no prédio e pares de câmera.

## O que NÃO foi aprovado
Essa é uma **primeira versão geométrica para avaliação**. Ainda restam: detalhamento PBR realista das fachadas, quiosques, vegetação, passagem de pedestres com rampas e vagas, diferenças de nível e cruzamentos, integração de personagem/colisão efetiva em Play Mode, NavMesh, testes de FPS e avaliação da cena em PC jogável. O recorte continua visualmente simplificado e as relações de distância foram **artisticamente compactadas**, não reproduzem distâncias reais de Copacabana. Não declarar versão final nem jogo instalável; PR draft até validação de arte e gameplay.

## Integração sem regressão
Esta tarefa ocorreu em **clone independente**, para não conflitar com o trabalho simultâneo do Sol 6.1 em `main`. Após QA/PR, fundir a nova cena ao repositório único e escolher `ProjectResort_300m_Immersive.unity` como padrão. Só então remover a R15 pré-compactação e seus meshes redundantes, com audit de dependências Unity; nunca apagar o único projeto standalone.
