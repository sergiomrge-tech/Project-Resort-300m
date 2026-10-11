# MARÉ — evolução unificada, revisão 2

## Direção aprovada durante o trabalho

O jogador compra ampliações que se ligam ao que já possui. A mesma construção transforma-se: quiosque → restaurante → hotel simples com restaurante nos fundos → resort único. A versão anterior com edifícios espalhados foi substituída nesta revisão.

Arquivo ativo: `Mare_Evolucao_Unificada_v2.blend`. Cenas: `MARE_UNIDA_ETAPA_01` a `MARE_UNIDA_ETAPA_20`. O mapa urbano anterior está preservado.

## Cadência das compras

| Etapa | Transformação / compra |
|---|---|
| 01 | Quiosque inicial |
| 02 | Deck ligado ao balcão |
| 03 | Cozinha de apoio ligada |
| 04 | Transformar em restaurante |
| 05 | Sanitários do restaurante |
| 06 | Hotel simples com restaurante nos fundos |
| 07 | Ala esquerda de quartos |
| 08 | Ala direita de quartos |
| 09 | Cozinha e operação ampliadas |
| 10 | Pátio de piscina conectado |
| 11 | Lounge de praia ligado à ala |
| 12 | Clube infantil integrado |
| 13 | Academia no piso superior |
| 14 | Spa anexado ao corpo do hotel |
| 15 | Gastronomia no piso superior dos fundos |
| 16 | Suítes privativas sobre o spa |
| 17 | Salão de eventos nos fundos |
| 18 | Lavanderia e recursos ligados |
| 19 | Novos pisos no núcleo e ala esquerda |
| 20 | Unificar o resort e serviço cinco estrelas |

## Implementado na arte

- Quiosque com cobertura de telhas curvas, apoios do telhado, balcão, espresso, moedor, vitrine refrigerada aberta por dentro, pia com gabinete, louças, cardápio, madeira com veio longitudinal, parafusos e mobiliário.
- Restaurante fecha e amplia a construção original; reutiliza o balcão e equipamentos, com cobertura própria e mesas.
- Na transformação em hotel, o restaurante e o balcão reaproveitado passam para os fundos.
- Alas laterais encostadas no núcleo, blocos de serviço e lazer unidos, corredores de ligação, ampliação de pisos, escadas com aberturas nas lajes e representação do poço de elevador.
- Cobertura e fachada frontal contínuas na etapa final, chegada coberta, terraço, piscina de cobertura, pérgola e vegetação.
- Orla com piso curvo e meio-fio contínuo, ciclofaixa, bancos, lixeiras, iluminação, passarelas inclinadas à areia e duchas. Palmeiras com copas instanciadas refinadas.
- JSON de 20 etapas com dependências, transformações de assets, serviços, moedas fictícias e metas de qualidade provisórias.

## Evidência e limites

Renders são capturas reais do Blender/Cycles, 1600 × 900. A inspeção do arquivo reaberto é registrada em `mare_unified_validation.json`.

A revisão prepara arquitetura, assets e dados de evolução. Compra de terrenos, economia, hóspedes, funcionários, saves, classificação por serviço, elevador em movimento, animação de reformas, colisões e navegação ainda não estão implementados/testados na Unity. Os interiores dos módulos avançados são representativos; não estão acabados com o nível de detalhe do quiosque. Não há certificação arquitetônica, estrutural ou de acessibilidade, nem meta/FPS declarados. Custos e condições de compra precisam de testes de jogo.

## Fontes de pesquisa
- https://www.fourseasons.com/jimbaranbay/services-and-amenities/ — spa, piscinas, beach club, kids club, fitness, yoga, concierge, eventos, atividades de praia
- https://www.marriott.com/en-us/hotels/dxbpj-marriott-resort-palm-jumeirah-dubai/overview/ — varandas, suítes, room service 24h, restaurantes, academia, spa, kids club
- https://www.fourseasons.com/hualalai/services-and-amenities/sustainability/ — redução de descartáveis, produção local, gestão ambiental
- https://stories.forbestravelguide.com/what-makes-a-forbes-travel-guide-five-star — qualidade de serviço e instalações; edifícios sozinhos não definem cinco estrelas
- https://www.fourseasons.com/orlando/accommodations/accessibility-overview/ — acessibilidade de quartos e áreas comuns

Os serviços de cinco estrelas no jogo exigem qualidade sustentada, não apenas compra de prédios. Metas são autorais. Texturas Poly Haven têm licença CC0 conforme manifestos anteriores. Geometria nova do MARÉ criada neste projeto. A cena urbana mantém as atribuições anteriores do Cristo (CC BY); não se devem remover esses créditos ao distribuir esse modelo.
