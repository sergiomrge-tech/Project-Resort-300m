# EXECUCAO PRIORITARIA DO SOL 6.1 MEDIUM — UNICO PROJECT RESORT 300x300

## ORDEM MAIS RECENTE DO USUARIO 09/10/2026
O usuario nao voltara ao mapa 2km nem ao antigo jogo Simulador Predial. Ele quer EXCLUIR tudo que nao pertencer a nova versao 300x300 m, do PC, Unity e GitHub. Portanto CANCELAR toda tarefa de arte R14/R13/2km, nenhuma atualizacao do Simulador Predial. O produto UNICO e novo e o Resort 300x300 m, trecho real de Copacabana e ceu com nuvens. A geografia deve ser recortada em metros, NUNCA escalada 0.15.

## DIRETORIOS
SEU UNICO REPO GRAVAVEL E CANONICO: D:\ProjectResort_300m_Standalone
GITHUB NOVO JA EXISTE: https://github.com/sergiomrge-tech/Project-Resort-300m (vazio, main)
AS FONTES ANTIGAS SAO APENAS LEITURA, NAO ALTERAR NEM APAGAR:
- D:\ProjectResort_R15_300m_Sky — geradores R15, shaders, quatro prints reais
- D:\ProjectResort_R15_300m_UnityQA\UnityProject — projeto Unity COMPLETO existente, cena real Assets/Scenes/R15_Copacabana_300x300_Cloudy.unity e meshes ja recortados
- D:\ProjectResort_R15_300m_UnityQA\build\R15_QA — QA real Unity e 4 prints com SHA
- D:\ProjectResort_R14_Sol61_Orla — legado SOMENTE LEITURA
- D:\ProjectResort_GameIntegration_R12 / D:\sergi\Documents\Simulador-predial — antigo jogo nao desejado, somente leitura
O supervisor so apagara legados DEPOIS que R15 standalone funcionar; NAO execute git clean nem Remove-Item -Recurse nesses diretorios.

## ATUAL R15 VALIDADO MAS AINDA NAO INDEPENDENTE
Unity 6000.6.2f1 Direct3D11 RTX4060Ti, cena 300x300 real com Skybox/Panoramic de nuvens autorais 2048x1024. 1390 renderizadores fonte, 26 inteiros, 354 clips, 1010 fora; 466319 triangulos visiveis. 4 screenshots reais 1600x900 verificadas por SHA. Fonte R14 original inalterada. Materialidade do ceu e do solo ainda necessita acabamento. CERCA DE MIL OBJETOS LEGADOS EXTERNOS PODEM ESTAR DESATIVADOS MAS REFERENCIADOS, e isso impede apagar R14.

## MISSAO P0 — CRIAR PROJETO UNITY COMPLETAMENTE AUTONOMO
1. Ler AGENTS/README antigos para contexto e inspecionar scripts de R15 existentes, QA e screenshots. Inspecionar real AssetDatabase.GetDependencies da cena Assets/Scenes/R15_Copacabana_300x300_Cloudy.unity para saber precisamente quais referencias apontam a R7-R14, including FBX/Material/Texture/GUID. Criar docs/DEPENDENCIES_BEFORE.md com lista e contagens. NAO supor renderer.enabled=false elimina dependencias.
2. Criar UnityProject em ESTE novo repo, apenas com Packages manifest/lock, ProjectSettings, Assets/Scenes/ProjectResort_300m.unity, Assets/R15/Meshes, Materials, Textures, Scripts e rendering URP necessarios. Reutilizar a versao de Unity e URP que esta funcionando, nao introduzir novas engines ou Unity diferente.
3. Criar um Editor bake executavel em copia temporaria QA: nova cena from scratch em vez de salvar toda a hierarquia R14. Traga SOMENTE os 380 mesh renderers internos/cortados, os seus meshes .asset proprios (CLONAR os 26 mesh inteiros ainda apontando FBX originais) e materiais PBR com mapas realmente usados, mais camera, luzes/volume URP e skybox de nuvens. Nada fora dos limites 300m. Duplicar materiais e texturas necessarios para pasta Assets/R15 com GUIDs estaveis, nunca deixar Assets/Architecture/R7...R14 ou FBX externos referenciados. Nao deixar componentes scripts legados nem referencias a fontes 2km em scene.
4. Ajustar colisores da nova cena: eliminar todos colliders antigos dos 2km (mesmo quando renderer.enabled=false), construir limites reais de 300m e superficies solo/rua coerentes, conferir navegabilidade em futuro teste Unity; marcar Player/PlayMode/NPC/saves como NAO TESTADOS ate testar de verdade. Nao carregar antigos gameplay Simulador Predial.
5. Preservar geometria GIS em 1m=1m, coordenadas de recorte atuais reportadas no R15 QA, ceu tropical com nuvens visiveis em 2+ capturas GPU reais. Melhorar material PBR de mosaico preto/branco, areia seca/molhada, fachada nao repetitiva, rua/calcada/sarjetas e vegetacao tropical de ALTA QUALIDADE dentro do quadrado somente. Nada low-poly aparente, nada de 2km.
6. Reproducibilidade: o novo GitHub tem que conter TODOS ASSETS realmente necessarios, independente do PC ligado ou de clonar R14. Nao copiar Library/Temp/Logs/obj/BuildCache. Nao usar links ou caminho D antigos em build scripts ou README. Criar arquivo .gitignore. Arquivos individuais <=100MB GitHub; dividir asset maior. Criar testes Python e Github Actions verificando arquivos, hashes, GUIDs, dependencias zero R7-R14, dimensoes 300x300 e cobertura visual.
7. Validar abrindo projeto novo de ZERO em outra pasta Unity 6000.6.2f1 com Direct3D11: parser sem erros, zero materiais faltantes/rosas/brancos fallback, skybox atribuido, geometria de piso e fachada presente. Gerar 4 a 6 PNGs REAIS Unity 1600x900 com SHA, mostrando nuvens, calçadão, praia, rua e predios, sem obstrucao por parede. Nunca gerar fake/montagem/mockup sob nome RealUnity. FPS so apos benchmark PlayMode/Standalone.
8. Construir README apenas do Project Resort 300m, docs/QA_STANDALONE.md com contagem real de objs, materiais, meshes, arquivos e dependencia; docs/DELETE_LEGACY_MANIFEST.md com paths EXATOS dos legados do PC/Unity/GitHub que o supervisor podera apagar DEPOIS DA INDEPENDENCIA. Nenhuma entrega R7-R14 deve ficar no novo repo, salvo formatos de arte devidamente RENOMEADOS E COPIADOS COMO R15, com direitos e atribuicoes preservados.
9. Comitar e fazer PUSH apenas no NOVO repo Project-Resort-300m. Se git push ou CI falhar, registrar log e preservar commits locais, supervisionado com gh depois. Nao alterar nem fazer merge nas antigas PRs R14 R13 ou repo Simulador Predial.

## RESTRICOES DE DELECAO
O usuario quer exclusao definitiva, mas nao apague material antes de ter a unica copia standalone verificada na nuvem. GitHub CLI da conta nao possui o escopo delete_repo; supervisor cuidara do pedido de autorizacao e eliminacao dos repos antigos. Nao tocar em outros jogos/apps do usuario.

## CRITERIO DE SUCESSO
Novo repo Project-Resort-300m com UnityProject e uma cena real 300x300 m de paisagem com nuvens, materiais e meshes TODOS locais, nenhum asset/R7..R14 no grafo de dependencias, CI verde, Unity import e GPU reais, novo manifest de exclusao pronta. O usuario nao quer voltar a 2km nem Simulador Predial. Entregar TRABALHO REAL e resultados verificaveis, nao apenas plano. Trabalhar autonomamente ate limite da sessao; sem microperguntas.
