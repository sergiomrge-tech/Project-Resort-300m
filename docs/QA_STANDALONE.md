# QA standalone — 09/10/2026

Cena criada vazia e preenchida somente com meshes dentro do recorte. As 26 malhas inteiras também foram clonadas e transformadas para coordenadas de mundo; nenhum FBX completo integra o projeto. A hierarquia, scripts e colisores antigos não foram transferidos. As referências foram medidas com `AssetDatabase.GetDependencies(..., true)` e cada GUID serializado de Assets e ProjectSettings foi resolvido pela Unity.

| Medição real | Resultado |
|---|---:|
| Unity / URP | 6000.6.2f1 / 17.6.0 |
| API / GPU | Direct3D11 / NVIDIA GeForce RTX 4060 Ti |
| Objetos da cena | 387 |
| Mesh renderers / ativos | 380 / 370 |
| Meshes locais | 380 |
| Triângulos totais / ativos | 466.319 / 422.072 |
| Materiais / texturas usados | 202 / 80 |
| Mesh colliders novos | 347 |
| Box colliders de limite | 4 |
| Consultas verticais de solo | 18/18 com colisão |
| Componentes ausentes | 0 |
| Dependências locais da cena + pipeline | 671 |
| Referências externas a assets legados | 0 |
| Maior arquivo de asset | 11.969.385 bytes |
| Arquivos distribuídos do projeto, incluindo metas e configurações | 1.383 |
| Capturas reais | 4 × 1600 × 900 |

O censo antigo somava 26 malhas inteiras e 354 recortadas, inclusive 10 renderizadores inativos. Por isso 466.319 não representa o total de triângulos ativos; a diferença foi registrada no relatório novo. Esses 10 objetos agora referenciam somente assets locais e não têm colisores criados.

Frame de recorte preservado, em metros: x local [-510, -210], y local [-40, 260], rotação 46°. Equivale aos limites GIS reportados na fonte: x [-40, 260], y [-510, -210]. Bounds observados por vértice: x [-510,000061; -209,999969], y [-40,000019; 260,006165]. A tolerância herdada do recorte é de 7 mm; não há transformação de escala 0,15. Todos os transforms geométricos novos usam escala unitária.

Skybox `Skybox/Panoramic` atribuído, panorama autoral de 2048 × 1024. As quatro capturas mostram calçadão, praia, fachadas e vista aérea; nuvens estão visíveis nas três vistas horizontais. A inspeção visual foi realizada nas quatro imagens. Não foram observados materiais rosa; shaders usados passaram pela verificação de suporte e erros. Superfícies cinzas presentes são parte da arte provisória, não confirmação de arte final.

Melhorias aplicadas: redução do brilho aparente do mosaico, intensidade de normal em asfalto/calçada/sarjeta/guia e shader PBR de areia com resposta distinta para areia seca/molhada. Foram removidas propriedades obsoletas de textura que ainda mantinham referências a fontes antigas, mesmo sem uso pelo shader.

**Limitações:** fachadas ainda repetitivas, grandes superfícies urbanas cinzas, vegetação pouco densa e nuvens suaves. O padrão visual de alta qualidade solicitado ainda não foi atingido. A física foi verificada por consultas verticais, não por deslocamento de personagem. Player, PlayMode, NPCs, saves, navegabilidade completa e FPS: **NÃO TESTADOS**. Build de player não foi executada; esta instalação reporta ausência do módulo WindowsStandalone.

Evidência: `evidence/standalone_qa.json`, quatro PNGs e SHA-256 individuais, `evidence/guid_resolution.tsv`, `evidence/files_sha256.json`, `evidence/mesh_provenance.tsv`. Os testes portáteis verificam arquivos, hashes, GUIDs, grafo de assets, dimensões e integridade das capturas; não julgam automaticamente a qualidade artística.

Verificação em clone da nuvem: pendente nesta revisão. Nenhum legado foi excluído.
