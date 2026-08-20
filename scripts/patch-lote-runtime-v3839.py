from pathlib import Path

ROOT = Path('native/www')
ASSET = Path('assets/lote-alfanumerico-runtime-v3839.js')
DEST = ROOT / 'lote-alfanumerico-runtime-v3839.js'

if not ASSET.exists():
    raise SystemExit('Asset lote-alfanumerico-runtime-v3839.js nao encontrado.')

DEST.write_text(ASSET.read_text(encoding='utf-8'), encoding='utf-8')

for nome in ('cadastro.html', 'editar.html'):
    path = ROOT / nome
    if not path.exists():
        continue
    html = path.read_text(encoding='utf-8')
    tag = '<script src="lote-alfanumerico-runtime-v3839.js?v=3839"></script>'
    if tag not in html:
        if '</body>' not in html:
            raise SystemExit(f'Nao foi possivel localizar </body> em {nome}')
        html = html.replace('</body>', f'    {tag}\n</body>', 1)
    path.write_text(html, encoding='utf-8')

for nome in ('cadastro.html', 'editar.html'):
    path = ROOT / nome
    if path.exists() and 'lote-alfanumerico-runtime-v3839.js?v=3839' not in path.read_text(encoding='utf-8'):
        raise SystemExit(f'Runtime nao injetado em {nome}')

print('Runtime v3839 de lote alfanumerico injetado sem reescrever cadastro.js/editar.js.')
