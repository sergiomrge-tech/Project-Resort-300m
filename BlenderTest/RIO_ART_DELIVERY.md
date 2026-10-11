# Resort — entorno do Rio e Cristo Redentor v2

## Arquivo atual

`Resort_Rio_Cristo_Montanhas_Vegetacao_v2.blend`, na pasta `D:\ProjectResort_300m_CompactPass\BlenderTest`.

A cidade continua com 2.000 × 1.000 m e 40 setores em escala 1. O entorno, oceano e montanhas ficam além desse retângulo, conforme solicitado. Os arquivos anteriores permanecem disponíveis.

## Cristo Redentor: substituição após crítica visual

A escultura procedural inicial foi rejeitada visualmente. Ela está desativada na cena final. A versão visível utiliza a malha **Christ the Redeemer (Cristo Redentor)** de **Parlin Sitorus**, com 55.600 triângulos e 30.553 vértices importados (divisões de UV/normais podem aumentar os vértices em relação ao catálogo).

- Fonte original: https://sketchfab.com/3d-models/christ-the-redeemer-cristo-redentor-157dbdb9d8654651a5e5c9af7b412398
- Licença: Creative Commons Attribution 4.0 — https://creativecommons.org/licenses/by/4.0/
- A licença e autoria foram confirmadas pela API pública do Sketchfab e registradas em `AssetsExternal/cristo_source_license.json`.
- Arquivo GLB obtido da cópia pública creditada em https://github.com/ariellinfy/CPSC-581-PostcARds . O README foi preservado em `AssetsExternal`.
- Alterações realizadas: escala uniforme para altura total de 38 m, shader de pedra com variação e relevo, normais suaves e posição sobre o Corcovado adaptado. O mirante, escadas e guarda-corpos foram modelados neste projeto.
- A autoria da malha deve acompanhar futuras distribuições e créditos do jogo; a escultura importada não é de autoria do Codex.

Referência de proporções: https://cristoredentoroficial.com.br/curiosidades — 30 m de monumento e 8 m de pedestal. A malha importada inclui a própria base; foi escalada pelo conjunto, sem afirmar reconstrução arquitetônica exata da capela.

## Entorno e vegetação

- Seis malhas de relevo: Corcovado, Pedra da Gávea, duas massas inspiradas nos Dois Irmãos, montanha nordeste e contrafortes florestais.
- Relevo, posições e distâncias são **aproximações artísticas**, não uma reprodução topográfica do Rio. O Corcovado usa pico nominal de 704 m como referência do Parque Nacional da Tijuca: https://parquenacionaldatijuca.rio/locais/corcovado/ .
- Palmeiras com folíolos curvos e pontiagudos, copas de árvores compostas por folhas, materiais verdes variados e casca com relevo.
- 6.482 instâncias de árvores nas encostas, apoiadas por projeção sobre o relevo final; fontes geométricas compartilhadas.
- Céu azul e nuvens procedurais para a câmera. O HDRI incorporado permanece responsável pela iluminação ambiente.
- Terreno e oceano de contexto eliminam a visualização do céu sob as bordas dos módulos.
- Calçadas da frente urbana e meios-fios reconstruídos a partir do mesmo contorno: raios de 5 m nos cantos perimetrais e 3 m nas entradas laterais.

## Capturas reais

Renders Cycles de 1.600 × 900, sem imagens ilustrativas substituindo o jogo/modelo:

- `rio_cristo_artist_mesh.png`: escultura e pedestal.
- `rio_cristo_face_final.png`: close do rosto.
- `rio_city_mountains_final.png`: cidade e montanhas.
- `rio_vegetation_street_final.png`: vegetação na orla e calçadas.

## Fontes de edição

Sequência sobre `Resort_Ipanema_2x1km_Comercio_Ruas_Corrigido.blend`: `align_sidewalk_curves.py`, `resort_rio_landscape.py`, `sculpt_cristo_redentor.py`, `refine_rio_landscape_cristo.py`, `replace_cristo_with_artist_mesh.py`, `finish_rio_environment.py`, `seal_rio_context.py`. Não repetir passes incrementais na cena pronta. A fase inicial de escultura é preservada como histórico, mas seu resultado fica oculto após a substituição.

Conferência do arquivo salvo: `inspect_rio_delivery.py`. Metadados: `rio_delivery_validation.json`. Integridade dos arquivos: `rio_delivery_hashes.json`.

## Limites atuais

O Cristo atual é uma representação artística modelada, não fotogrametria. Montanhas e vegetação receberam um passe inicial de cenário e ainda permitem refinamento artístico, especialmente variedade de espécies e detalhes das faces rochosas. Não foi feita integração na Unity, medição de FPS, teste de colisões, LODs ou desempenho de runtime. O número de folhas e instâncias não deve ser tratado como orçamento de jogo validado.
