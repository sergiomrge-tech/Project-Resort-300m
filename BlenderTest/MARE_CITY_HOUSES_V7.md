# Project Resort — casas e comércio no bairro (v7)

O mapa mantém a área de **2 km × 1 km** e as torres da primeira faixa da orla. Nas quadras internas, 30 setores agora usam casas térreas e sobrados, e 10 setores de transição mantêm os edifícios da frente marítima com casas atrás. O bairro contém 1.132 lotes de casa, incluindo 478 fachadas comerciais distribuídas em 12 categorias. As piscinas e espelhos d’água urbanos repetidos foram removidos; a piscina do resort e suas 20 etapas permanecem.

## Arquivos principais

- Blender editável: `Resort_Main_Map_Mare_Houses_v7.blend`
- Unity — cena principal clonada: `ProjectResort_Main_2x1km_HousesV7.unity`
- Unity — cena para executar: `ProjectResort_Mare_StandalonePreview_HousesV7.unity`
- Build Windows x64: `Builds/Mare_Windows_v7/ProjectResort_Mare_v7.exe`
- Capturas renderizadas no Blender: `BlenderCaptures_Houses_v7/`
- Manifesto de verificações e hashes: `city_houses_v7_hashes.json`

## Validação realizada

- O Blender 5.2.1 salvou e reabriu o mapa v7; auditoria de dados: 40 setores, dimensões de 2.000 × 1.000 m, nenhuma piscina urbana ativa, 8 componentes das torres preservados, sem imagens externas ausentes e 20 etapas do resort presentes.
- O exportador gerou os dados de casas e ruas e a integração criou as duas cenas Unity v7. Os arquivos originais v4/v6 e a cena standalone v6 permanecem disponíveis.
- O relatório do build registra Unity 6000.6.2f1 e resultado `Succeeded`. Também contém um timeout de 5 s da chamada de automação e avisos de colisão pré-cozida e configuração URP. Não há captura verificada de execução real do player v7, medição de FPS ou aprovação artística dentro da Unity nesta entrega.
- As três imagens de revisão são renders reais do Blender, não capturas da Unity.

## Reprodução

O gerador é `tools/revise_city_houses_v7.py` e `tools/audit_houses_v7.py`; ele parte de `Resort_Main_Map_Mare_Integrated_v4.blend` e escreve a versão v7 sem substituir o original. A exportação seletiva para Unity está em `tools/export_city_houses_v7_unity.py`; o importador do Editor está em `UnityProject/Assets/Editor/ImportCityHousesV7.cs`.
