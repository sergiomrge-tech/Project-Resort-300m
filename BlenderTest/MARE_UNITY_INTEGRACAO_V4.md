# Maré — integração Blender → Unity

## Projeto e arquivos

- Projeto Unity: `D:\ProjectResort_300m_CompactPass\UnityProject`.
- Cena nova: `Assets/Scenes/ProjectResort_Main_2x1km_Mare.unity`.
- Assets nativos: `Assets/R15/BlenderIntegrated`.
- Fonte editável: `D:\ProjectResort_300m_CompactPass\BlenderTest\Resort_Main_Map_Mare_Integrated_v4.blend`.
- Intermediários: `BlenderTest/UnityExport_v4`.
- Capturas reais e relatórios: `BlenderTest/UnityCaptures_v4`.

## Integração

O mapa urbano principal mede 2.000 × 1.000 m. O contexto de montanhas e mar permanece ao redor. O resort ocupa um lote no setor costeiro 03, com tradução Blender (-340, -295, 0), sem redimensionar os edifícios. A avenida e o calçadão públicos do mapa original foram preservados. A composição antiga dentro do lote foi substituída, evitando sobrepor o resort às construções anteriores.

As 20 etapas arquitetônicas estão organizadas em módulos compartilhados. A etapa 20 inclui 59 quartos com banheiro privativo, além de recepção, restaurantes, cozinhas, administração, áreas de equipe, lavanderia, spa, academia, espaço infantil e eventos. As variantes iniciais de quiosque e restaurante são ocultadas quando substituídas pela construção maior. O contexto repetido de praia e orla do modelo independente foi excluído da integração.

As malhas foram convertidas para coordenadas Unity (x, z, y), com correção da orientação dos triângulos, normais, UVs e tangentes. A Unity utiliza Mesh assets e prefabs compartilhados. Os buffers `.meshbin` são intermediários de importação, não dependências de execução da cena.

## Materiais

85 materiais de origem foram convertidos para URP Lit. Canais procedurais de cor e rugosidade foram gravados em texturas; os mapas normais existentes foram reaproveitados ou gerados. Os mapas metálicos usam R para metallic e A para smoothness. O céu panorâmico HDR foi importado como asset local. Água, vidro e luzes são aproximações de shaders e iluminação Blender em URP, não uma reprodução exata do Cycles.

## Etapas no Editor

Abra a cena e use **Resort → Blender Mare → Visualizar evolução 1 a 20**. A ferramenta mostra os módulos correspondentes à etapa selecionada. Salvar a cena registra a etapa visual ativa.

Isso é uma prévia de composição: compras, progressão econômica, hóspedes, funcionários, interações e saves ainda precisam de implementação no jogo. Os pontos de atividade modelados são referências para essa implementação.

## Reproduzir a importação

1. Execute `integrate_mare_into_main_map.py` em Blender 5.2, tendo a fonte de interiores v3.1 disponível.
2. Execute `export_main_map_unity.py` com o `.blend` integrado.
3. Na Unity 6000.6.2f1 com URP, execute `ImportMareUnity.Main` via Unity Pipeline `run_script`, usando o arquivo C# salvo em `BlenderTest/tools`.
4. Execute `ImportMareUnity.FinishLighting` para criar o perfil ACES da cena e ajustar as luzes.
5. Execute `ImportMareUnity.Capture` e `ImportMareUnity.GeometryReport` para atualizar as evidências.

O importador usa caminhos absolutos desta máquina para localizar os intermediários. Ajuste a constante `Src` se mover os arquivos. Assets nativos e a cena importada utilizam dependências locais do projeto.

## Limites de validação

Os relatórios registram a versão Unity, API gráfica, materiais e malhas ausentes, quantidade de renderizadores, triângulos e colisores, dependências e amostras de piso por raycast. Capturas são geradas pela câmera URP da cena, em 1600 × 900.

Raycasts pontuais não comprovam navegação completa. Este passe não entrega controlador de jogador ou NavMesh. Quantidade de triângulos e objetos não equivale a FPS; a otimização para lançamento ainda requer medição com gameplay, LODs, occlusion culling e perfil por plataforma.

## Resultado registrado em 10/10/2026

- Unity 6000.6.2f1, Direct3D11.
- 5.481 malhas compartilhadas, 85 materiais e 72 prefabs de coleções.
- Todas as 20 etapas verificadas no Editor, sem referências de malhas ou materiais ausentes e sem materiais com shader não suportado.
- Etapa 20: 59 quartos ativos confirmados pela hierarquia.
- 35.503 MeshRenderers ativos e 3.928 MeshColliders ativos na etapa final.
- 110.819.128 triângulos somados em toda a cena ativa, incluindo o contexto externo; isso não representa a quantidade visível por quadro.
- 5.767 dependências locais, nenhuma dependência externa identificada na cena.
- Sete raycasts com colisores encontrados: orla, avenida, calçada, lobby, restaurante, quarto e praia. No quarto, a amostra atinge a plataforma da cama; na praia, o piso-base do setor. Não são testes completos de caminhada.
- Seis imagens reais da Unity em 1600 × 900: orla/resort, aérea do bairro, mapa completo, lobby, quarto e restaurante.
- Perfil local ACES, exposição +0,35, bloom 0,08 e iluminação ambiente em três cores.

A integração técnica está concluída. A cena ainda é pesada e precisa de LODs, agrupamento de objetos pequenos e medição real de desempenho antes de ser tratada como pronta para lançamento. As capturas também mostram que montanhas, vegetação distante, água e repetição urbana ainda precisam de refinamento artístico. A integração não equivale à aprovação final da arte.
