# Manifesto de exclusão para o supervisor

**NÃO EXECUTADO.** A exclusão só pode começar depois de confirmar commit na nuvem, CI verde, clone limpo, import Unity 6000.6.2f1 e capturas GPU do projeto novo. Se qualquer gate estiver pendente, conservar as fontes. Este documento não é script de exclusão.

Projeto único a conservar: `D:\ProjectResort_300m_Standalone` e `https://github.com/sergiomrge-tech/Project-Resort-300m`.

Diretórios identificados no PC para revisão e exclusão pelo supervisor após os gates:

| Caminho exato | Conteúdo |
|---|---|
| `D:\ProjectResort_R15_300m_Sky` | Fonte de transição anterior ao standalone |
| `D:\ProjectResort_R15_300m_UnityQA` | Projeto e evidência de transição anteriores |
| `D:\ProjectResort_R14_Sol61_Orla` | Mundo legado |
| `D:\ProjectResort_R13_Sol61_Orla` | Mundo legado |
| `D:\ProjectResort_R13_Sol61_Pass2` | Mundo legado |
| `D:\ProjectResort_R10_Sol_Art` | Mundo legado |
| `D:\ProjectResort_R8_CityFix` | Mundo legado |
| `D:\ProjectResort_R8_UnityQA` | QA legado |
| `D:\ProjectResort_R7_Acabamento_Codex` | Mundo legado |
| `D:\ProjectResort_R7_Sol61` | Mundo legado |
| `D:\ProjectResort_R7_Sol61_Artifacts` | Artefatos legados |
| `D:\ProjectResort_R7_Sol61_Validated_Blend` | Artefatos legados |
| `D:\ProjectResort_R6_VisualEvidence` | QA legado |
| `D:\ProjectResort_GameIntegration_R12` | Integração do jogo descontinuado |
| `D:\sergi\Documents\Simulador-predial` | Jogo descontinuado explicitamente indicado pelo usuário |

Projetos Unity associados incluem os subdiretórios `UnityProject` das fontes acima; removê-los do Unity Hub após a exclusão. Não foi modificado o cadastro do Hub nesta execução.

Repositórios GitHub antigos confirmados: `https://github.com/sergiomrge-tech/Resort-Simulator-` pela documentação fonte, e `https://github.com/sergiomrge-tech/Simulador-predial` pelo remote local consultado. O supervisor cuidará do escopo `delete_repo` e da autorização final. Nenhuma PR antiga foi alterada.

`D:\ProjectResort_AssetLibrary`, `D:\ProjectResort_Autonomy`, `D:\ProjectResort_Entregas_ChatGPT`, `D:\ProjectResort_GitHub` e `D:\ProjectResort_Vegetacao_Codex` foram encontrados, mas seu conteúdo e eventual uso compartilhado ainda exigem classificação pelo supervisor. Não autorizar exclusão automática desses diretórios por nome. Não tocar em outros jogos e apps.

A cópia temporária `.work` no repo novo é ignorada pelo Git e contém dados intermediários do bake. Só removê-la depois da validação do standalone e da preservação do bake e da proveniência.
