# Reproduzir o standalone

Para abrir, importar ou construir a cena, usar somente `UnityProject` deste repositório. Packages resolve URP 17.6.0; todos os assets de cena são locais. Não transferir caches de outra máquina ou de fontes antigas.

1. Clonar o repositório em uma pasta vazia.
2. Executar `python tools/test_standalone.py`.
3. Abrir Unity 6000.6.2f1 com Direct3D11, ou usar `tools/run_unity_qa.ps1` com os parâmetros de Editor, Project e Output.
4. Conferir os relatórios, log e PNGs produzidos. O script usa cinco requisições reais de render URP por câmera antes da leitura GPU.

Hashes de imagens podem variar entre sessões por animação do mar e driver. Os hashes distribuídos comprovam os arquivos de evidência armazenados; não exigem que todo render futuro seja idêntico. Geometria, escala, GUIDs e dependências são conferidos em cada execução.

Os arquivos `tools/StandaloneBake.cs`, `StandaloneFinish.cs`, `export_bake.py` e `record_provenance.py` são ferramentas de migração/auditoria usadas nesta entrega. **Não são dependências do jogo nem do build.** A evidência existente preserva os resultados da migração, inclusive após excluir suas fontes. O bake é executado em uma cópia temporária, nunca no projeto fonte; a cena é criada vazia. O finish remove slots/propriedades obsoletos e aplica ajustes de superfície. O export usa o grafo medido pela Unity. `improve_sand.py` aplica o refinamento PBR no shader local exportado. `.work` não é distribuída.

Para gerar build de player depois, instalar o módulo de plataforma compatível com Unity 6000.6.2f1 e testar Player/PlayMode e física. Não há FPS ou executável de player certificado nesta entrega.
