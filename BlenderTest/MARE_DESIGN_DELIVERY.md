# MARÉ — quiosque e evolução em 20 etapas

Data: 10 de outubro de 2026.

## Estrutura criada no Blender

Arquivo: `Mare_Quiosque_20Etapas_v1.blend`. A cena urbana anterior permanece no mesmo arquivo e no seu arquivo original. As cenas `MARE_ETAPA_01` até `MARE_ETAPA_20` mostram evolução cumulativa. As coleções numeradas permitem separar a compra de cada módulo.

O quiosque inicial tem mais de 600 objetos: cobertura com telhas curvas e beirais, treliças e apoios de madeira, gabinete sob a pia, estrutura e pranchas de madeira, balcão de pedra, caixa, espresso, moedor com café, pia com cuba, torneira, refrigerador, prateleiras, garrafas, louças, cocos, placas, luminárias, bancos e cadeiras com trama. As etapas seguintes têm modelos arquitetônicos com equipamentos e mobiliário representativos; não receberam o mesmo acabamento de perto do quiosque.

A orla tem calçadão curvo, meio-fio seguindo a curva, faixa ciclável, bancos, lixeiras, luminárias, passarelas de acesso à areia, duchas e palmeiras instanciadas. O lote de evolução mede 240 × 240 m. Trata-se de uma cena de autoria dos assets, sem substituir o mapa urbano de 2 × 1 km.

## Cadência proposta

Custos são moedas fictícias e provisórias. Cada compra exige a etapa anterior, reputação e capital de operação. Não houve teste de economia.

| Etapa | Compra / serviço principal | Custo inicial proposto |
|---|---|---:|
| 01 | Quiosque original | 12,000 |
| 02 | Deck e mesas | 18,000 |
| 03 | Preparo e estoque | 28,000 |
| 04 | Sanitários | 35,000 |
| 05 | Lounge com pérgola | 42,000 |
| 06 | Beach club | 60,000 |
| 07 | Restaurante | 110,000 |
| 08 | Operação e equipe | 120,000 |
| 09 | Recepção e jardins | 150,000 |
| 10 | Primeiros bangalôs | 210,000 |
| 11 | Piscina e deck | 230,000 |
| 12 | Ala de suítes | 390,000 |
| 13 | Clube infantil | 180,000 |
| 14 | Academia e yoga | 190,000 |
| 15 | Spa | 290,000 |
| 16 | Gastronomia autoral | 360,000 |
| 17 | Villas premium | 550,000 |
| 18 | Eventos e celebrações | 410,000 |
| 19 | Lavanderia e recursos | 280,000 |
| 20 | Resort cinco estrelas | 950,000 |

## Serviços do resort completo

Além da arquitetura: reservas, recepção/concierge, alimentação, atendimento de quarto, governança, enxoval e lavanderia, estoque frio/seco, energia e água, descarte, manutenção, segurança, monitoria infantil, atividades, spa, academia, eventos, personalização do atendimento e acessibilidade. O JSON associa novos serviços e cargos às etapas.

A classificação de cinco estrelas no jogo terá metas sustentadas de serviço, higiene, conforto, manutenção e satisfação. São regras autorais propostas para o jogo, não uma certificação real.

## Preparação para integração

- Coordenadas em metros; IDs de módulo e etapa em propriedades dos objetos.
- Módulo 01 com sockets de pedido, preparo e abastecimento.
- JSON com lotes, dependências, custos provisórios, cargos, serviços e metas.
- 20 cenas para visualizar as transições sem sobrepor módulos futuros à etapa inicial.
- Compra de terrenos, progressão, clientes, funcionários, saves, navegação e colisões ainda precisam ser implementados e testados na Unity.
- Interiores das ampliações são representativos, sem detalhamento completo de suítes/banheiros/MEP; hidrodinâmica, acessibilidade normativa e procedimentos operacionais não foram simulados.
- Portabilidade do Blender e renders reais devem constar de `mare_validation.json` e imagens de entrega.

## Referências pesquisadas
- https://www.fourseasons.com/jimbaranbay/services-and-amenities/ — spa, piscinas, beach club, kids club, fitness, yoga, concierge, eventos, atividades de praia
- https://www.marriott.com/en-us/hotels/dxbpj-marriott-resort-palm-jumeirah-dubai/overview/ — varandas, suítes, room service 24h, restaurantes, academia, spa, kids club
- https://www.fourseasons.com/hualalai/services-and-amenities/sustainability/ — redução de descartáveis, produção local, gestão ambiental
- https://stories.forbestravelguide.com/what-makes-a-forbes-travel-guide-five-star — qualidade de serviço e instalações; edifícios sozinhos não definem cinco estrelas
- https://www.fourseasons.com/orlando/accommodations/accessibility-overview/ — acessibilidade de quartos e áreas comuns

## Texturas e licenças

Materiais PBR reaproveitados da entrega urbana, com imagens incorporadas ao .blend; texturas Poly Haven CC0 conforme `TexturesPBR_Urban/sources.json` e fontes anteriores. Modelagem nova do MARÉ gerada neste projeto. O modelo de Cristo preservado na cena urbana mantém sua licença CC BY e atribuição anteriores. Não foram usados nomes ou logotipos de resorts reais no modelo.
