# Resort — correção de vegetação e objetos suspensos

## Arquivo entregue

`D:\ProjectResort_300m_CompactPass\BlenderTest\Resort_Ipanema_2x1km_Comercio_Ruas_Corrigido.blend`

Mapa de 2.000 × 1.000 metros, 40 setores com escala 1. O arquivo anterior `Resort_Ipanema_2x1km_Comercio_Ruas.blend` foi preservado.

## Implementação

- Criadas três variantes de setor com malhas privadas para os elementos modificados. Arquitetura e dimensões dos edifícios preservadas.
- Palmeiras, árvores, jardineiras e arbustos associados foram reposicionados como conjuntos. Copas, galhos e troncos acompanham a mesma translação.
- Posicionamento considera avenidas, ruas transversais, vias perimetrais, curvas nos cantos, volumes dos prédios e distância entre plantas.
- Altura das bases calculada por projeção sobre as malhas reais de areia, pavimentação, jardins e decks. Bases penetram 1,5 cm no suporte para eliminar frestas.
- 1.140 instâncias de vegetação/jardineiras reposicionadas em XY; 3.480 conjuntos receberam ajuste de altura. São totais instanciados do mapa, não objetos únicos.
- Pés adicionados a cadeiras, espreguiçadeiras e bancos; bases dos guarda-sóis; duas vigas sob as ripas de cada pergolado de cobertura; vigas nos cabanas da piscina.
- Apoios nas lojas: menus, vasos e hastes das plantas, suportes das pranchas e expositores de roupas.
- Pisos sólidos adicionais nas mesas dos cafés dos setores interiores e nas duas frestas entre calçadão, ciclovia e avenida.

## Conferência realizada

- Três renders reais Cycles de 1.600 × 900: cruzamento interior, orla e lojas de perto.
- Inspeção visual dos renders: árvores dos cruzamentos fora do asfalto; copas e troncos coerentes; vigas sob pergolados; menu e vaso em contato com o piso; transições da orla fechadas.
- Arquivo final reaberto em outro processo Blender 5.2.1 LTS: dimensões 2.000 × 1.000 m, 40 instâncias dos setores corrigidos, 17/17 imagens incorporadas ao arquivo.
- Relatório estruturado: `grounding_validation.json`. Manifesto SHA256: `grounding_hashes.json`.

## Fontes e regeneração

1. Abrir `Resort_Ipanema_2x1km_Comercio_Ruas.blend`.
2. Executar `fix_floating_assets.py` uma vez no Blender.
3. Executar `finish_grounding_details.py` uma vez.
4. Salvar e executar `inspect_grounded_resort.py` no Blender em segundo plano para atualizar o relatório.

Os scripts de alteração possuem guardas contra execução repetida na mesma cena. As malhas não alteradas e materiais continuam compartilhados. As posições dos arbustos nas jardineiras seguem os recipientes.

## Limites

Esta entrega trata de geometria e composição no Blender. Não inclui validação de colisões, NavMesh, física de jogo ou FPS na Unity. A conferência das três câmeras não constitui inspeção visual individual de todas as instâncias; setores repetidos usam as mesmas variantes corrigidas. Sombras muito escuras entre edifícios e o acabamento artístico dos materiais podem receber outro passe.
