# Resort Ipanema — expansão Blender 2 × 2 km

## Arquivo principal

`D:\ProjectResort_300m_CompactPass\BlenderTest\Resort_Ipanema_2x2km.blend`

Cena ativa: `RESORT_IPANEMA_2x2KM`. Coleção principal: `MAP_2000x2000_METERS`.

## Escala e composição

- Terreno principal: **2000 × 2000 m**, 4 km², unidade métrica e escala 1.
- 90 setores de 200 × 200 m: 10 na orla e 80 no interior.
- Orla ao sul com faixa de mar dentro do limite principal; parque linear ao norte.
- Três módulos compartilhados: costeiro, bairro com jardins e bairro com mercado.
- Edifícios, materiais e detalhes derivados do padrão de 200 m aprovado. Instâncias com escala **(1, 1, 1)**; os prédios não foram ampliados para ocupar o território.
- Alternância de orientação dos setores do interior para variar fachadas e percursos.
- Malhas compartilhadas por coleções instanciadas; repetição modular permanece visível na vista geral.

## Conteúdo

Resorts, piscinas, spa, villas, prédios residenciais, comércio, terraços, varandas, pergolados, praia equipada, calçadão, ciclovia, avenidas, travessias, praças, jardins, árvores, palmeiras, espelhos d'água e mercados.

O mapa é uma composição aproximada inspirada em Ipanema. Não é um levantamento cadastral. Montanhas e uma lagoa regional completa não foram modeladas nesta expansão.

## Correções executadas

- Piscina: substituição da bacia fechada por borda em segmentos, expondo a água.
- Fachada lateral da ala de suítes: caixilhos, molduras e elementos de sombreamento.
- Jardins, caminhos e terraço de restaurante adicionados à fonte dos setores.
- Folhas de palmeiras ampliadas em largura.
- Galeria e mercado reposicionados para liberar as ruas perimetrais.
- Ruas laterais da orla limitadas à avenida, corrigindo o avanço sobre a areia.
- Câmera a pé reposicionada para remover a obstrução pelo tronco de uma palmeira.

## Texturas

17 imagens externas incorporadas ao .blend, incluindo mapas PBR e HDRI. Assets Poly Haven / CC0:

| Asset | Autores | Fonte |
| --- | --- | --- |
| asphalt_03 | Charlotte Baglioni, Dario Barresi | https://polyhaven.com/a/asphalt_03 |
| sand_03 | Charlotte Baglioni | https://polyhaven.com/a/sand_03 |
| wooden_floor_02 | Charlotte Baglioni, Rico Cilliers | https://polyhaven.com/a/wooden_floor_02 |
| checkered_pavement_tiles | Amal Kumar | https://polyhaven.com/a/checkered_pavement_tiles |
| sunflowers_puresky | Jarod Guest, Sergej Majboroda | https://polyhaven.com/a/sunflowers_puresky |

Demais materiais: shaders procedurais com cor, rugosidade e relevo; nem todas as superfícies usam imagens externas. UVs calculadas em unidades de mundo.

## Capturas reais

Renders Cycles a **1600 × 900**, 32 amostras e denoise:

- `resort_2km_aerial.png`: mapa completo.
- `resort_2km_district.png`: trecho da orla e quadras.
- `resort_2km_walk.png`: fachada vista a pé.
- `resort_2km_pool.png`: pátio e piscina.

Todos em `D:\ProjectResort_300m_CompactPass\BlenderTest`. Conferência visual realizada; correções acima foram aplicadas e as capturas afetadas foram refeitas.

## Verificação do arquivo salvo

Arquivo reaberto numa execução separada do Blender 5.2.1 LTS em modo background:

- Cena principal recuperada corretamente.
- Terreno: 2000 × 2000 m.
- 90 instâncias de setores, todas com escala 1.
- 17 imagens incorporadas; nenhuma imagem ausente ou não incorporada detectada.
- Quatro câmeras, resolução 1600 × 900, Cycles e céu HDRI recuperados.

Relatório: `resort_2km_validation.json`. Hashes de entrega: `resort_2km_hashes.json`.

Não houve teste de gameplay, colisões de runtime, streaming, FPS ou integração Unity nesta etapa. A quantidade de instâncias não é uma medida de desempenho. O conteúdo continua sendo uma cena artística Blender.

## Fontes editáveis e reprodução

- Fonte refinada: `Resort_Ipanema_SOURCE_refined_200x200.blend`.
- `build_resort_2km.py`: execute a partir da fonte refinada; requer a coleção e materiais dessa fonte.
- `refine_ipanema_new.py`: refinamento da fonte inicial de 200 m; executá-lo apenas uma vez na fonte inicial, pois adiciona geometria.
- `inspect_saved_2km.py`: inspeção do arquivo salvo; não altera geometria.

Arquivo inicial `Resort_Ipanema_NEW_200x200.blend` e versões anteriores preservados.
