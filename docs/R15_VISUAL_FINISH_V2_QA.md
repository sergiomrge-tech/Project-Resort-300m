# Project Resort — passe visual imersivo v2

## O que foi gerado

O Editor Unity 6000.6.2f1 abriu o projeto pelo Unity Hub com o Package Manager conectado e gerou `Assets/Scenes/ProjectResort_300m_Immersive_v2.unity`. A cena de origem permaneceu intacta. O lote segue com 300 × 300 m e conserva o recuo compacto documentado entre edifícios e calçadão; a ferramenta e os testes de compacidade não alteram a escala-base dos edifícios.

O passe adiciona uma faixa de pavimentação costeira, acabamentos de fachada, toldo e letreiro comercial, quiosque, sete palmeiras em floreiras, cinco bancos e cinco luminárias. O relatório do Builder registra 22 grupos de edifícios e 511 renderers no total. A variação cromática usa `MaterialPropertyBlock` sobre os materiais existentes para manter os mapas de superfície conectados; as peças novas usam materiais reutilizáveis em `Assets/R15/VisualFinish`.

A iluminação preserva o skybox panorâmico original e reduz a exposição/tinta para recuperar o azul do céu. O mapa foi reconstruído pelo comando oficial `Resort > Visual Finish > Build tropical premium scene`.

## Capturas verificadas

As cinco imagens PNG abaixo foram renderizadas pelo Universal Render Pipeline no Editor, em 1600 × 900, Direct3D12, NVIDIA GeForce RTX 4060 Ti, com cinco quadros de aquecimento:

- `evidence/visual_finish/ProjectResort_v2_01_PromenadeToBuildings_UnityGPU.png`
- `evidence/visual_finish/ProjectResort_v2_02_AvenueAndFacades_UnityGPU.png`
- `evidence/visual_finish/ProjectResort_v2_03_BeachSkyClouds_UnityGPU.png`
- `evidence/visual_finish/ProjectResort_v2_04_Aerial300m_UnityGPU.png`
- `evidence/visual_finish/ProjectResort_v2_05_CloseFacade_UnityGPU.png`

O relatório `evidence/visual_finish/visual_finish_qa.json` registra dispositivo, resolução, coordenadas de câmera e SHA-256. A aérea enquadra a faixa costeira e o tecido urbano; os demais ângulos mostram calçadão, avenida, fachadas e praia.

## Validação e limites

- `python tools/test_compact_distance.py`: 3 testes de geometria/compacidade e evidência de captura.
- `python tools/test_standalone.py`: 7 testes portáteis, incluindo referências GUID, fechamento de dependências e hashes.
- `evidence/files_sha256.json` e `evidence/guid_resolution.tsv` devem refletir todos os assets gerados.
- O log do Editor contém o marcador `VISUAL_FINISH_BUILD_PASS`; a abertura e renderização da cena foram feitas em Unity, não por mockup.
- A checagem artística confirma paleta e enquadramentos, mas ainda há leitura estilizada no conjunto original. Não foi medido FPS nem aprovado desempenho em jogo, caminhada, colisões novas de mobiliário, iluminação em outras plataformas ou qualidade fotorrealista. O relatório mantém `fps_measured=false` e `art_approved=false`.
