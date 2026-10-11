# MARÉ — interiores e operação do resort, revisão 3

Arquivo Blender: `Mare_Evolucao_Interiores_v3_1.blend`.
Cenas de evolução: `MARE_UNIDA_ETAPA_01` a `MARE_UNIDA_ETAPA_20`.

Esta revisão acrescenta interiores à evolução unificada do mesmo estabelecimento: quiosque → restaurante → hotel com restaurante nos fundos → alas e serviços conectados. Os arquivos v2 e o mapa urbano anterior permanecem preservados. A construção exterior mantém suas dimensões.

## Ambientes modelados

| Área | Conteúdo de arte e uso previsto no jogo |
|---|---|
| Quiosque | Equipamentos detalhados já existentes, pia apoiada, café, vitrine, balcão, cardápio, armazenamento e deck |
| Restaurante inicial | Mesas e cadeiras com louças, recepção de clientes, cozinha, preparo, fogão/coifa, geladeira, lavagem e passe |
| Restaurante nos fundos | Balcão fundador reaproveitado, salão mobiliado, cozinha equipada e circulação em torno do bar |
| Recepção | Balcão ripado com pedra, terminais, identificação, sala de espera, concierge, bagagens e iluminação |
| Quartos | 59 unidades físicas na etapa final, instanciadas de um módulo en-suite; cama, roupa de cama, cabeceira, mesas/luminárias, armário, minibar, bagageiro, TV, cortinas, planta e banheiro privativo |
| Banheiros | Louças com centro aberto, cuba, torneira, espelho, amenidades, toalha, box, chuveiro e iluminação; banheiros públicos com privacidade |
| Administração | Posto de gestão com mesa, computador, cadeira e arquivos |
| Operação | Estoque em prateleiras com caixas, preparo e cozinha de serviço, mesa de funcionários e armários |
| Lavanderia | Máquinas com portas de vidro, controles, mesas de separação e pilhas de roupa limpa |
| Infantil | Piso acolchoado, mesas e assentos, nichos e cestos de brinquedos |
| Academia | Esteiras com consoles, tapetes de yoga, espelho e iluminação |
| Spa | Macas de tratamento, toalhas, divisões, cubas, plantas e balcão de acolhimento |
| Gastronomia superior | Mesas postas, cadeiras, iluminação e ponto de serviço |
| Eventos | Mesas, palco, tela e iluminação |
| Suítes sobre spa | Quartos en-suite e espaço adicional de estar com sofás e mesas |
| Cobertura | Bar de piscina acrescentado ao terraço, pérgola, espreguiçadeiras e piscina existentes |

## Circulação e reaproveitamento

- As camas soltas anteriores foram substituídas por quartos divididos.
- Os corredores das alas têm faixa central livre; uma faixa transversal em y = -9 liga alas e núcleo. Algumas unidades foram retiradas para garantir esse espaço.
- O núcleo mantém passagem central para os fundos, acesso à escada e ao elevador representado.
- Divisórias de vidro nas ligações entre núcleo, alas e serviços receberam aberturas reais na geometria.
- Móveis provisórios antigos nas áreas substituídas foram removidos para evitar sobreposição.
- Quartos usam instâncias para reutilizar malha e materiais. Cada unidade tem um identificador próprio para futura integração.

## Atividades preparadas para integração

Objetos vazios `GAME_*` identificam locais de check-in/check-out, concierge, gestão de pessoal e finanças, preparo/cozimento/passe, atendimento, estoque, limpeza da cama, reposição de minibar, lavanderia, atividades infantis, fitness, spa, eventos e bar de piscina. Os pontos de quartos são identificados pelo caminho `room_id/GAME_*`.

São referências espaciais e metadados. Não existem controladores de tarefas, hóspedes, economia, animação de equipamentos, interação de portas, água corrente ou efeitos de comida implementados nesta revisão. O manifesto registra `runtime_implemented: false`.

## Inspeção e evidências

- Arquivo salvo e reaberto em Blender separado para inspecionar cenas, distribuição dos quartos, etapas, texturas empacotadas e metadados.
- Capturas reais dos setores isolados para inspeção em Blender/Cycles, 1600 × 900: recepção, quarto, restaurante, cozinha, spa e lavanderia. Os objetos vêm do arquivo final; os renders de inspeção não mostram todos os setores simultaneamente.
- As capturas foram usadas para corrigir posicionamento de câmera, mesas invadindo a área de trabalho, privacidade dos sanitários e móveis duplicados.
- `mare_interiors_manifest_v3.json` contém os quartos, coleções, etapas e pontos de atividade expandidos.
- `mare_interiors_validation_v3.json` registra a inspeção técnica. Isso não é teste de navegação, colisão ou desempenho na Unity.
- `mare_progression_interiors_v3.json` atualiza a capacidade física: 4 quartos na etapa 6, 20 na etapa 7, 36 na etapa 8, 39 na etapa 16, 51 na etapa 19 e 59 na etapa 20. Preços e metas continuam provisórios.
- Na etapa final há 139 pontos espaciais de atividade, incluindo os pontos de cama e minibar expandidos das instâncias dos quartos. Esses pontos não executam ações por conta própria.
- Após um timeout do MCP, a conclusão foi executada em Blender separado. O arquivo final é a revisão `v3_1`; a janela original pode continuar mostrando `v3`.

## Limites desta entrega

Há mobiliário nos setores internos previstos, mas esta revisão ainda é um passe de arte modular. Os quartos reutilizam um modelo; não há 59 projetos de decoração exclusivos. Os ambientes avançados precisam de mais variedade de objetos, acabamento localizado, portas funcionais e animações. Colisores, NavMesh, exportação/importação na Unity e mecânicas de operação ainda precisam ser desenvolvidos e testados. A classificação cinco estrelas é uma meta do jogo, não uma certificação desta arquitetura.

As fontes de pesquisa e os créditos dos materiais/modelos preservados estão em `MARE_UNIFIED_DELIVERY.md` e nos manifestos anteriores. Não remover os créditos ao distribuir o mapa ou o Cristo existente.
