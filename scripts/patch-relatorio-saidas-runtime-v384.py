from pathlib import Path
import shutil
import re

ROOT = Path('native/www')
ASSETS = Path('assets')
MOV_HTML = ROOT / 'movimentacao.html'
HIST_HTML = ROOT / 'historico.html'
SW = ROOT / 'service-worker.js'

arquivos = {
    'movimentacao-destino-v3833.js': 'movimentacao-destino-v3833.js',
    'historico-saidas-v3833.js': 'historico-saidas-v3833.js',
    'relatorio-saidas-v3833.html': 'relatorio-saidas.html',
    'relatorio-saidas-v3833.css': 'relatorio-saidas-v3833.css',
    'relatorio-saidas-v3833.js': 'relatorio-saidas-v3833.js',
}

for origem_nome, destino_nome in arquivos.items():
    origem = ASSETS / origem_nome
    destino = ROOT / destino_nome
    if not origem.exists():
        raise SystemExit(f'Asset ausente: {origem}')
    shutil.copy2(origem, destino)

for pagina, src in (
    (MOV_HTML, 'movimentacao-destino-v3833.js?v=3833'),
    (HIST_HTML, 'historico-saidas-v3833.js?v=3833'),
):
    if not pagina.exists():
        raise SystemExit(f'Página ausente: {pagina}')
    html = pagina.read_text(encoding='utf-8')
    if src not in html:
        if '</body>' not in html:
            raise SystemExit(f'</body> ausente em {pagina.name}')
        html = html.replace('</body>', f'<script src="{src}"></script>\n</body>', 1)
        pagina.write_text(html, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-33', sw, count=1)
    SW.write_text(sw, encoding='utf-8')

validacoes = {
    ROOT / 'movimentacao-destino-v3833.js': ['seedcontrol-movimentacao-destino-v3833', 'grupoDestino', 'Informe o destino da saída', 'seedSnapshotSaida'],
    ROOT / 'historico-saidas-v3833.js': ['seedcontrol-historico-saidas-v3833', 'btnRelatorioSaidas', 'Relatório de Saídas'],
    ROOT / 'relatorio-saidas.html': ['Relatório de Saídas', 'relatorio-saidas-v3833.js?v=3833', 'Compartilhar'],
    ROOT / 'relatorio-saidas-v3833.js': ['seedcontrol-relatorio-saidas-v3833', 'RelatoriosSaidas', 'autoTable', 'XLSX.write'],
    ROOT / 'relatorio-saidas-v3833.css': ['seedcontrol-relatorio-saidas-v3833', 'rel-saida-card'],
}

for arquivo, marcas in validacoes.items():
    if not arquivo.exists():
        raise SystemExit(f'Arquivo final ausente: {arquivo.name}')
    texto = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in texto:
            raise SystemExit(f'Validação falhou em {arquivo.name}: {marca}')

if 'movimentacao-destino-v3833.js?v=3833' not in MOV_HTML.read_text(encoding='utf-8'):
    raise SystemExit('Hook não injetado em movimentacao.html')
if 'historico-saidas-v3833.js?v=3833' not in HIST_HTML.read_text(encoding='utf-8'):
    raise SystemExit('Hook não injetado em historico.html')

print('Relatório de Saídas v3833 aplicado por hooks runtime, sem alterar movimentacao.js/historico.js por âncoras frágeis.')
