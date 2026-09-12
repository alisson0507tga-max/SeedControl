# SeedControl — fonte oficial v3.8.4

Este repositório agora usa como fonte oficial o aplicativo anexado pelo usuário:

`SeedControl-v3.8.4-uso-imediato-3934-signed.apk`

A pasta pública foi extraída diretamente de `assets/public` desse APK, sem misturar os arquivos da interface antiga. O pacote correspondente é:

`SeedControl_v3.8.4_uso_imediato_source.zip`

## Conteúdo confirmado

A fonte atual contém 99 arquivos públicos e inclui a interface mais recente, dashboard atualizado, entrada comercial, relatórios, módulos de saída, visualização de notas, planilhas, scripts de dados de soja, suporte ao teclado nativo e bibliotecas jsPDF/XLSX para geração de PDF e Excel.

O APK não contém arquivos PDF estáticos. Os PDFs são gerados pelo aplicativo em tempo de execução através dos módulos de relatório e das bibliotecas jsPDF incluídas.

## Fonte de verdade

- APK de referência: `SeedControl-v3.8.4-uso-imediato-3934-signed.apk`
- Código público extraído: `SeedControl_v3.8.4_uso_imediato_source.zip`
- Script de importação reproduzível: `scripts/importar-fonte-apk-atual.py`

Para reimportar outro APK com a mesma estrutura, atualize o caminho `APK` no script e execute:

```bash
python3 scripts/importar-fonte-apk-atual.py
```

Os ZIPs de versões anteriores foram removidos da raiz para evitar que uma interface antiga seja utilizada por engano.
