# Correção de serrilhado — Maré Unity

## Causa encontrada

A cena integrada estava com MSAA 1×, antialiasing da câmera em None e capturas RenderTexture sem multiamostragem.

## Configuração aplicada

- URP dedicado: `Assets/R15/BlenderIntegrated/Rendering/Mare_URP_Antialiasing.asset`, derivado do pipeline que o projeto já usava.
- MSAA 4× no pipeline ativo e câmera com MSAA permitido.
- SMAA em qualidade High na câmera principal.
- Pós-processamento mantido com o perfil ACES existente.
- Escala de renderização 1,0.
- Pipeline selecionado nas configurações gráficas e no nível de qualidade ativo do projeto.
- Capturas reais em 1600 × 900 com RenderTexture MSAA 4×; quatro perspectivas comparadas com as imagens anteriores.

As malhas e os arquivos do Blender não foram alterados nesta correção. O asset URP anterior continua disponível para comparação. Os arquivos fonte de importação e captura atualizados estão em `BlenderTest/tools/Antialiasing_v5`.

## Reprodução

Com a cena integrada aberta na Unity 6000.6.2f1, execute `FixMareAntialiasing.Apply` pelo Unity Pipeline `run_script`. Após o Editor atualizar a renderização, execute `FixMareAntialiasing.Capture`. As capturas e o relatório ficam em `BlenderTest/UnityCaptures_AA_v5`.

## Evidência e limites

O relatório `antialiasing_validation.json` registra Direct3D11, RTX 4060 Ti, MSAA 4× no pipeline e no alvo das capturas, SMAA High e pós-processamento ativo. As imagens conferidas mostram suavização das bordas da fachada, folhas e mobiliário.

A configuração aumenta o custo de renderização. Não foi realizada medição de FPS nesta correção. Detalhes muito pequenos e distantes ainda podem apresentar aliasing; facetas da geometria também exigem refinamento das malhas, independentemente do antialiasing.
