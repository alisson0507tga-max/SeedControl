from pathlib import Path
import shutil
import re

ROOT = Path('native/www')
SRC = Path('correcoes-3914')

arquivos = {
    'planilhas-fieis-v3914.js': ROOT / 'planilhas-fieis-v3914.js',
    'relatorio-faixa-fiel-v3914.js': ROOT / 'relatorio-faixa-fiel-v3914.js',
}
for nome, destino in arquivos.items():
    origem = SRC / nome
    if not origem.exists():
        raise SystemExit(f'Arquivo ausente: {origem}')
    shutil.copy2(origem, destino)

paginas = {
    ROOT / 'planilha.html': '<script src="planilhas-fieis-v3914.js?v=3914"></script>',
    ROOT / 'entrada-comercial.html': '<script src="planilhas-fieis-v3914.js?v=3914"></script>',
    ROOT / 'relatorio-saidas.html': '<script src="relatorio-faixa-fiel-v3914.js?v=3914"></script>',
}
for pagina, tag in paginas.items():
    if not pagina.exists():
        raise SystemExit(f'Pagina ausente: {pagina.name}')
    html = pagina.read_text(encoding='utf-8')
    if tag not in html:
        if '</body>' not in html:
            raise SystemExit(f'</body> ausente em {pagina.name}')
        html = html.replace('</body>', f'    {tag}\n</body>', 1)
    pagina.write_text(html, encoding='utf-8')

# Lote alfanumerico deve permanecer texto tambem no Excel da planilha principal.
planilha_js = ROOT / 'planilha.js'
if planilha_js.exists():
    js = planilha_js.read_text(encoding='utf-8')
    js = js.replace('Number(item.lote) || 0,', 'String(item.lote == null ? "" : item.lote),')
    planilha_js.write_text(js, encoding='utf-8')

sw = ROOT / 'service-worker.js'
if sw.exists():
    texto = sw.read_text(encoding='utf-8')
    texto = re.sub(r'seedcontrol-v3\.8-pwa-[A-Za-z0-9._-]+', 'seedcontrol-v3.8-pwa-3914', texto, count=1)
    sw.write_text(texto, encoding='utf-8')

validacoes = {
    ROOT / 'planilhas-fieis-v3914.js': ['seedcontrol-planilhas-fieis-v3914', 'Salvar Excel em Documentos', 'Salvar PDF em Documentos', 'SeedControl/'],
    ROOT / 'relatorio-faixa-fiel-v3914.js': ['seedcontrol-relatorio-faixa-fiel-v3914', 'Período (De / Até)', 'Compartilhar PDF', 'Compartilhar Excel', 'RelatoriosSaidas'],
    ROOT / 'planilha.html': ['planilhas-fieis-v3914.js?v=3914'],
    ROOT / 'entrada-comercial.html': ['planilhas-fieis-v3914.js?v=3914'],
    ROOT / 'relatorio-saidas.html': ['relatorio-faixa-fiel-v3914.js?v=3914'],
}
for arquivo, marcas in validacoes.items():
    texto = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in texto:
            raise SystemExit(f'Validacao 3914 falhou em {arquivo.name}: {marca}')

if planilha_js.exists() and 'Number(item.lote) || 0,' in planilha_js.read_text(encoding='utf-8'):
    raise SystemExit('Planilha principal ainda converte lote para numero.')

print('3914 aplicada: pre-visualizacoes fieis, salvar PDF/Excel em Documentos e Relatorio com Dia/Mes/Ano/De-Ate.')