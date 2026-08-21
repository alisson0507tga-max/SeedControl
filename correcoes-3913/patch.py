from pathlib import Path
import shutil
import re

ROOT = Path('native/www')
SRC = Path('correcoes-3913/relatorio-periodos-share-v3913.js')
DEST = ROOT / 'relatorio-periodos-share-v3913.js'
REL = ROOT / 'relatorio-saidas.html'

if not ROOT.exists():
    raise SystemExit('native/www nao encontrado')
if not SRC.exists():
    raise SystemExit('Arquivo 3913 ausente')
if not REL.exists():
    raise SystemExit('relatorio-saidas.html ausente')

shutil.copy2(SRC, DEST)

html = REL.read_text(encoding='utf-8')
tag = '<script src="relatorio-periodos-share-v3913.js?v=3913"></script>'
if tag not in html:
    if '</body>' not in html:
        raise SystemExit('</body> ausente em relatorio-saidas.html')
    html = html.replace('</body>', f'    {tag}\n</body>', 1)
REL.write_text(html, encoding='utf-8')

sw = ROOT / 'service-worker.js'
if sw.exists():
    texto = sw.read_text(encoding='utf-8')
    texto = re.sub(r'seedcontrol-v3\.8-pwa-[A-Za-z0-9._-]+', 'seedcontrol-v3.8-pwa-3913', texto, count=1)
    sw.write_text(texto, encoding='utf-8')

marcas = [
    'seedcontrol-relatorio-periodos-share-v3913',
    'Filtrar por',
    'Compartilhar PDF',
    'Compartilhar Excel',
    'Share',
    'Mês',
    'Ano',
]
texto = DEST.read_text(encoding='utf-8')
for marca in marcas:
    if marca not in texto:
        raise SystemExit(f'Validacao 3913 falhou: {marca}')
if 'relatorio-periodos-share-v3913.js?v=3913' not in REL.read_text(encoding='utf-8'):
    raise SystemExit('Script 3913 nao injetado')

print('Correcao 3913 aplicada: filtros Dia/Mes/Ano e compartilhar PDF/Excel com cancelamento silencioso.')
