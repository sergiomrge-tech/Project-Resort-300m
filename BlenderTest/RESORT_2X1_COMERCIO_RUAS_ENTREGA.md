# Resort — 2 km de largura × 1 km de profundidade

## Arquivo atual

`D:\ProjectResort_300m_CompactPass\BlenderTest\Resort_Ipanema_2x1km_Comercio_Ruas.blend`

Cena ativa: `RESORT_2x1KM_COMERCIO`. Coleção principal: `MAP_2000x1000_COMERCIO`.

## Redução do mapa

Terreno principal de **2000 × 1000 m**, 2 km², centrado em X=-1000..1000 e Y=-500..500. Retiradas cinco fileiras de setores do fundo: agora 40 setores, 10 costeiros e 30 no interior, além de mar e parque linear. Escala dos setores e prédios mantida em 1; edifícios não foram comprimidos. Arquivos anteriores preservados.

## Comércio da orla

13 estabelecimentos e uma recepção por módulo costeiro; 130 estabelecimentos comerciais e 10 recepções no mapa. São repetições modulares das 13 identidades criadas, não 130 marcas diferentes.

Tipos: cafés, padaria, restaurantes, sorveteria, mercados, farmácia, boutique, loja de surf, presentes e galeria. Nomes fictícios.

O térreo dos cinco edifícios de frente para a avenida recebeu:

- Vitrines e portas com caixilhos, puxadores e soleiras.
- Toldos listrados e letreiros individuais.
- Pavimento, paredes, divisórias e tetos de interiores rasos de exposição.
- Balcões, caixa, mesas, cadeiras, prateleiras, embalagens, pranchas e produtos conforme o tipo de loja.
- Iluminação interna e vidro com transparência predominante para legibilidade estilizada.
- Mesas externas seletivas, vasos e placas de menu junto às vitrines.

Interiores são conteúdo visual; portas, compras, atendimento e navegação de NPCs não têm lógica de jogo nesta etapa.

## Ruas e conexões

- Avenidas do interior alinhadas entre os setores.
- 40 ligações elevadas entre ruas locais e avenida, atravessando os antigos bloqueios de calçada; conectores adicionais nas ruas transversais.
- 45 cruzamentos com remates curvos de asfalto e meios-fios arredondados.
- 193 travessias zebradas novas, contabilizadas no script; as marcações antigas também permanecem onde não foram substituídas.
- 63 rampas modeladas com placas táteis de aviso.
- Linhas duplas amarelas, linhas de parada e setas direcionais.
- Placas PARE, limite de velocidade, orientação à orla e modelos de semáforo.
- 32 assets de piso recortados para liberar os corredores; 11 assets de pavimentação receberam cantos arredondados.

A sinalização é cenográfica e aproximada. Semáforos são estáticos. Não foi feita auditoria de normas viárias, acessibilidade, dinâmica de veículos ou colisões.

## Capturas reais

Renders Blender/Cycles, 1600 × 900:

- `resort_2x1_retail_walk.png`: comércio da orla.
- `resort_2x1_retail_cafe.png`: portas e vitrines próximas.
- `resort_2x1_retail_shops.png`: outras fachadas comerciais.
- `resort_2x1_aerial.png`: mapa reduzido antes do passe viário.
- `resort_2x1_street_coast.png`: ligação com a avenida da orla após as correções.
- `resort_2x1_street_grid.png`: cruzamento interno e curvas após as correções.

As primeiras capturas levaram ao ajuste de transparência e iluminação das vitrines, ao recorte dos pisos que cobriam ruas e ao arredondamento da pavimentação. A câmera do cruzamento interno foi elevada para remover o telhado que escondia parte da composição.

## Verificação do arquivo salvo

Reabertura concluída em execução separada do Blender 5.2.1 LTS. Confirmados: terreno 2000 × 1000 m, 40 setores, escala 1, 130 comércios, inventário de conexões, 17 imagens incorporadas e nenhuma imagem ausente/não incorporada detectada. Relatório `retail_roads_validation.json`.

Não foram medidos FPS, gameplay, runtime, colisões ou integração Unity. As ruas têm geometria de conexão, mas a dirigibilidade só pode ser confirmada quando integrada e testada com veículos na engine.

## Scripts e reprodução

Abrir `Resort_Ipanema_2x2km.blend`, então executar nesta ordem, uma vez:

1. `build_resort_2x1km_commerce.py`
2. `connect_streets_2x1km.py`
3. `clear_street_corridors.py`
4. `round_sidewalk_corners.py`

Os scripts de passes adicionam conteúdo; reexecutá-los sobre o resultado pode duplicar assets. O arquivo final já contém todos os passes.

Texturas externas são os cinco assets Poly Haven / CC0 documentados em `RESORT_2KM_ENTREGA.md`; materiais novos de comércio e sinalização são shaders criados no Blender.
