# Project Resort — mapa costeiro reduzido

O mapa ativo é `/Game/Resort/Maps/Resort_HalfWest` no projeto `ProjectResortUE.uproject`.

## Recorte aprovado

- Largura: aproximadamente 1.000 m (metade oeste já aprovada).
- Profundidade: 500 m, removendo os 500 m do fundo da cidade.
- Coordenadas Blender: X de -1000 a 0 m; Y de -500 a 0 m.
- Coordenadas Unreal: X de -100000 a 0 cm; Y de 0 a 50000 cm.
- Orla, edifícios costeiros e resort preservados. Nenhuma escala de edifício foi redesenhada.
- As fileiras 4 e 5 ficam fora do nível ativo. A fileira 3 e as superfícies contínuas foram cortadas fisicamente no Blender.
- Malhas das fileiras 1 e 2 reutilizadas, sem duplicar a base.

## Ferramentas reproduzíveis

1. `Tools/crop_coast500.py`: executado no Blender em segundo plano; produz seis FBX recortados e relatório de limites.
2. `Tools/build_coast500.py`: executado na Unreal via `Tools/remote_ue.py`; importa o recorte, reutiliza materiais, configura Nanite/colisão e salva o nível ativo.
3. `Tools/validate_coast500.py`: confirma o nível, os 16 atores de geometria, o limite posterior e sondagens de colisão.

Relatórios gerados ficam em `Saved/coast500_build.json`, `Saved/coast500_validation.json` e `SourceArt/Coast1000x500/crop_report.json`.

Os arquivos de referência anteriores permanecem disponíveis para recuperação. A configuração de abertura do Editor e do jogo aponta para o nível costeiro reduzido.

Este recorte não constitui validação de todos os interiores, das 20 etapas de evolução ou do desempenho do jogo. Esses sistemas precisam de desenvolvimento e testes próprios.

## Verificação concluída

Nível salvo, 16 atores de geometria, limite posterior conferido e quatro sondagens de colisão com resultado positivo. Sessão Play In Editor iniciada; personagem Third Person criado no ponto inicial e apoiado na superfície. Sessão encerrada após a conferência. Captura real do teste em Saved/coast500_gameplay_1600.png (1600 × 900). Não foi realizado benchmark de FPS nem teste exaustivo de movimentação/interiores.
