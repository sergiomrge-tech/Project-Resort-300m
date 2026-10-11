from pathlib import Path
import json
root=Path('D:/ProjectResort_300m_CompactPass/BlenderTest')
sources=json.loads((root/'mare_progression_20.json').read_text(encoding='utf-8'))['sources']
rows=[
('Quiosque inicial','quiosque',12000,['café','coco','sucos','lanches'],0,'core_original'),
('Deck ligado ao balcão','ampliar',18000,['mesas externas'],0,'deck'),
('Cozinha de apoio ligada','ampliar',28000,['preparo','estoque'],0,'cozinha'),
('Transformar em restaurante','reformar',75000,['restaurante','salão','terraço'],0,'restaurante'),
('Sanitários do restaurante','ampliar',35000,['sanitários','limpeza'],0,'sanitarios'),
('Hotel simples com restaurante nos fundos','reformar',240000,['recepção','hospedagem','restaurante nos fundos','governança'],4,'hotel_core'),
('Ala esquerda de quartos','ampliar',270000,['mais quartos','varandas'],6,'ala_esquerda'),
('Ala direita de quartos','ampliar',270000,['mais quartos','varandas'],6,'ala_direita'),
('Cozinha e operação ampliadas','ampliar',130000,['abastecimento','apoio de equipe','manutenção','segurança'],0,'operacao'),
('Pátio de piscina conectado','ampliar',180000,['piscina','solário'],0,'piscina'),
('Lounge de praia ligado à ala','ampliar',95000,['cabanas','toalhas','descanso'],0,'lounge'),
('Clube infantil integrado','ampliar',180000,['monitoria infantil'],0,'kids'),
('Academia no piso superior','ampliar_vertical',190000,['fitness','yoga'],0,'academia'),
('Spa anexado ao corpo do hotel','ampliar',240000,['massagens','tratamentos'],0,'spa'),
('Gastronomia no piso superior dos fundos','ampliar_vertical',230000,['gastronomia autoral'],0,'gastronomia'),
('Suítes privativas sobre o spa','ampliar_vertical',280000,['suítes privativas','atendimento personalizado'],3,'suites_privativas'),
('Salão de eventos nos fundos','ampliar',330000,['casamentos','reuniões','celebrações'],0,'eventos'),
('Lavanderia e recursos ligados','ampliar',240000,['lavanderia','solar','gestão de água e resíduos'],0,'recursos'),
('Novos pisos no núcleo e ala esquerda','ampliar_vertical',450000,['suítes premium'],7,'pisos_premium'),
('Unificar o resort e serviço cinco estrelas','acabamento',650000,['ala direita premium','terraço de lazer','piscina de cobertura','chegada coberta','auditoria de qualidade','concierge','room service'],3,'resort_final'),
]
stages=[]
for i,(title,action,cost,services,rooms,asset) in enumerate(rows,1):
    st={'id':i,'title':title,'action':action,'scene':f'MARE_UNIDA_ETAPA_{i:02}','asset_id':asset,'requires_stages':[] if i==1 else [i-1],'cost_game_coins_draft':cost,'new_services':services,'rooms_represented_delta':rooms,'runtime_status':'not integrated','unlock_rule_draft':{'reputation_min':0 if i==1 else min(90,15+4*i),'positive_operating_profit_days':0 if i==1 else 3,'working_capital_days':3 if i<6 else 7}}
    if i==4:st['renovation']={'remove_visual':['original_kiosk_shell','original_kiosk_roof'],'retain':['founding_bar_equipment','kitchen_equipment','player_inventory','staff','recipes'],'add':['restaurant_shell','restaurant_roof','dining_room'],'relocate_terrace_m':[2,-6,0],'bar_transform_m':[0,0,0]}
    if i==6:st['renovation']={'replace_visual':['restaurant_original_shell','restaurant_original_roof'],'add':['two_floor_hotel_core','rear_restaurant'],'retain':['founding_bar_equipment','kitchen_equipment','player_inventory','staff','recipes'],'founding_bar_transform_m':[0,31,0],'kitchen_transform_m':[0,26,0],'restaurant_center_m':[0,15]}
    if i==15:st['renovation']={'replace_visual':['rear_restaurant_pitched_roof'],'add':['upper_dining_floor'],'retain':['ground_restaurant','founding_bar_equipment']}
    if i==20:st['game_five_star_audit']={'service_min':95,'hygiene_min':95,'comfort_min':90,'maintenance_min':90,'guest_satisfaction_min':90,'sustained_days':7,'all_previous_stages_required':True,'status':'authorial game targets, not an official hotel classification'}
    stages.append(st)
data={'schema_version':2,'date':'2026-10-10','blender_file':'Mare_Evolucao_Unificada_v2.blend','design':'same business transforms from kiosk to restaurant, to hotel with rear restaurant, to one connected resort','balance_status':'draft, not playtested','currency':'fictional game coins','growth_policy':'buy new land strips or floors; replace only obsolete shell assets; retain inventory and reusable equipment','urban_map_preserved':'2 x 1 km scene preserved; this is an asset study, not a replacement city map','final_building_and_deck_envelope_m':{'x':[-48,50],'y':[-31,56]},'public_promenade':'outside bought modules, permanent and unobstructed','sources':sources,'stages':stages}
(root/'mare_unified_progression_20.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# MARÉ — evolução unificada, revisão 2','','## Direção aprovada durante o trabalho','','O jogador compra ampliações que se ligam ao que já possui. A mesma construção transforma-se: quiosque → restaurante → hotel simples com restaurante nos fundos → resort único. A versão anterior com edifícios espalhados foi substituída nesta revisão.','',
'Arquivo ativo: `Mare_Evolucao_Unificada_v2.blend`. Cenas: `MARE_UNIDA_ETAPA_01` a `MARE_UNIDA_ETAPA_20`. O mapa urbano anterior está preservado.','','## Cadência das compras','','| Etapa | Transformação / compra |','|---|---|']
for st in stages:lines.append(f"| {st['id']:02} | {st['title']} |")
lines += ['','## Implementado na arte','','- Quiosque com cobertura de telhas curvas, apoios do telhado, balcão, espresso, moedor, vitrine refrigerada aberta por dentro, pia com gabinete, louças, cardápio, madeira com veio longitudinal, parafusos e mobiliário.','- Restaurante fecha e amplia a construção original; reutiliza o balcão e equipamentos, com cobertura própria e mesas.','- Na transformação em hotel, o restaurante e o balcão reaproveitado passam para os fundos.','- Alas laterais encostadas no núcleo, blocos de serviço e lazer unidos, corredores de ligação, ampliação de pisos, escadas com aberturas nas lajes e representação do poço de elevador.','- Cobertura e fachada frontal contínuas na etapa final, chegada coberta, terraço, piscina de cobertura, pérgola e vegetação.','- Orla com piso curvo e meio-fio contínuo, ciclofaixa, bancos, lixeiras, iluminação, passarelas inclinadas à areia e duchas. Palmeiras com copas instanciadas refinadas.','- JSON de 20 etapas com dependências, transformações de assets, serviços, moedas fictícias e metas de qualidade provisórias.','',
'## Evidência e limites','','Renders são capturas reais do Blender/Cycles, 1600 × 900. A inspeção do arquivo reaberto é registrada em `mare_unified_validation.json`.','',
'A revisão prepara arquitetura, assets e dados de evolução. Compra de terrenos, economia, hóspedes, funcionários, saves, classificação por serviço, elevador em movimento, animação de reformas, colisões e navegação ainda não estão implementados/testados na Unity. Os interiores dos módulos avançados são representativos; não estão acabados com o nível de detalhe do quiosque. Não há certificação arquitetônica, estrutural ou de acessibilidade, nem meta/FPS declarados. Custos e condições de compra precisam de testes de jogo.','',
'## Fontes de pesquisa']
for s in sources:lines.append('- '+s['url']+' — '+', '.join(s['supports']))
lines += ['','Os serviços de cinco estrelas no jogo exigem qualidade sustentada, não apenas compra de prédios. Metas são autorais. Texturas Poly Haven têm licença CC0 conforme manifestos anteriores. Geometria nova do MARÉ criada neste projeto. A cena urbana mantém as atribuições anteriores do Cristo (CC BY); não se devem remover esses créditos ao distribuir esse modelo.']
(root/'MARE_UNIFIED_DELIVERY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Unified progression and delivery documentation written')
