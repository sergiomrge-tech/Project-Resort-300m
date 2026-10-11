# Project Resort — passe PBR urbano no Blender

Data: 9 de outubro de 2026.

Arquivo: `Resort_Rio_Urban_Textures_v3.blend`, na pasta BlenderTest.
Base preservada: `Resort_Rio_Cristo_Montanhas_Vegetacao_v2.blend`.

## Implementado

- 10 materiais novos e 16 mapas JPG 4K: cor, normal OpenGL, rugosidade e altura de quatro conjuntos.
- Pavimentação de pedra nas calçadas; blocos de concreto nos espaços diante das lojas.
- Concreto com textura para meio-fio, molduras, varandas e elementos selecionados.
- Reboco com relevo e variação discreta nas fachadas coral, verde, turquesa, ocre e marfim.
- UVs em coordenadas métricas nas 152 malhas afetadas, reutilizadas pelos setores existentes. Repetição de 2 m para pisos e 3 m para reboco; ajuste artístico, não levantamento arquitetônico.
- Reflexos e rugosidade do vidro ajustados.
- Texturas incorporadas ao arquivo Blender. Geometria das curvas e escala dos prédios preservadas.
- Piso contínuo nos espaços urbanos descobertos dos três módulos, acima das bases coplanares e abaixo das ruas/calçadas elevadas. Correção da faixa preta observada entre os prédios na captura ampla.

## Evidência

- Renders reais em Cycles, 1600 × 900, 48 amostras: `urban_pbr_walk.png`, `urban_pbr_facade.png`, `urban_pbr_street.png`.
- Arquivo salvo reaberto em processo separado do Blender 5.2.1 LTS. `urban_pbr_validation.json` registra imagens 4096 × 4096 incorporadas e 40 setores com escala unitária.
- As vistas permitem inspecionar juntas da pavimentação, relevo do reboco, concreto e reflexos do comércio.

## Fontes e licença

Texturas Poly Haven, CC0: https://polyhaven.com/license

- https://polyhaven.com/a/concrete_pavers_02
- https://polyhaven.com/a/pavement_03
- https://polyhaven.com/a/grey_plaster_02
- https://polyhaven.com/a/concrete

URLs e arquivos individuais em `TexturesPBR_Urban/sources.json`. A licença e atribuição do modelo de Cristo continuam nos documentos da entrega anterior; CC0 destas texturas não altera a licença daquele modelo.

## Limites desta entrega

Este passe é de materiais no Blender. Mapas de altura alimentam bump, sem deslocamento geométrico. Os prédios e a vegetação conservam a modelagem existente; esta etapa não transforma todos os elementos em modelos realistas. A cidade conserva a composição de 2 km × 1 km, com montanhas de contexto fora desse retângulo. Exportação, materiais equivalentes na Unity, colisões e desempenho em jogo ainda precisam ser validados na etapa de integração.
