# Maré — executável Windows v0.6

## Distribuição

`D:\ProjectResort_300m_CompactPass\Builds\Mare_Windows_v6\ProjectResort_Mare.exe`

Abrir o executável junto de suas bibliotecas e pasta `_Data`. Não requer Unity ou Blender. A distribuição completa também está no ZIP `ProjectResort_Mare_Windows_v6.zip`.

## Implementado

- Cena de distribuição `Assets/Scenes/ProjectResort_Mare_StandalonePreview.unity`, derivada da cena principal, preservando seu hash SHA256 original.
- Câmera livre WASD, Q/E, Shift e botão direito; atalhos F1–F5.
- Interface uGUI/TextMeshPro com alternância visual das 20 etapas, atalhos e saída.
- Referências dos módulos serializadas na cena; o Player não depende do JSON de exportação externo.
- Build Windows64 Mono, Unity 6000.6.2f1, Direct3D11, janela inicial 1600 × 900.
- MSAA 4x e SMAA High mantidos na configuração Desktop.
- Pacote com fontes essenciais TMP, licença da fonte, relatórios e manifestos SHA256.

## Verificado nesta entrega

Build concluído: zero erros, quatro avisos, 930.783.801 bytes, aproximadamente 245 segundos. Player real aberto em janela normal na RTX 4060 Ti. Capturas das quatro vistas revisadas: orla, suíte, restaurante, aérea. Teclas F1/F3/F4/F5 e mudança de etapa 20→19 pelo teclado e 19→20 pelo botão observadas no Player. Janela capturada: 1602 × 932, viewport 1600 × 900.

A tentativa inicial de captura com janela oculta retornou imagens pretas. Foi rejeitada como evidência visual e arquivada separadamente em `WindowsHiddenCaptureAttempt_v6`. Evidência válida em `Builds/Mare_Windows_v6/Evidence/window_*.jpg` e `visible_player_validation.json`.

## Avisos e limites

O build registra: pré-cálculo de colisão desabilitado em 889 malhas para versões futuras (a Unity atual ainda calcula na compilação); ausência de configuração do plugin Pipeline em runtime (automação do Editor não habilitada no Player); API de busca de objetos marcada obsoleta; pragma antigo em shader TMP do pacote. O Player registra triângulos maiores que 500 unidades em três malhas existentes.

Esta entrega é uma prévia de exploração arquitetônica. A câmera atravessa paredes. Compras, hóspedes, saves e interações permanecem pendentes. Não houve medição de FPS nem execução de suítes automatizadas nesta entrega; o limite configurado de 60 quadros não comprova desempenho. O mapa e os interiores ainda precisam de refinamento artístico e otimização geométrica.

## Reprodução

Ferramenta persistente: `Assets/R15/BlenderIntegrated/Editor/BuildMareWindows.cs`. Com o projeto aberto e salvo, executar `BuildMareWindows.Prepare()` e `BuildMareWindows.Build()`. Em lote, `BuildMareWindows.Bootstrap` importa recursos TMP ausentes, aguarda o Editor e compila a cena explícita. Não usar `-quit`, pois a ferramenta encerra o Editor após terminar no modo de lote.

Fonte runtime: `Assets/R15/BlenderIntegrated/Runtime/MareStandaloneViewer.cs`. Ferramenta de empacotamento preservada em `BlenderTest/tools/Standalone_v6`. Manifesto incremental: `mare_standalone_hashes_v6.json`; inventário da distribuição: `distribution_manifest.json`.
