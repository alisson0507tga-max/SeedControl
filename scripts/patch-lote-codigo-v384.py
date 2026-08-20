from pathlib import Path
import re

ROOT = Path('native/www')
ASSET = Path('assets/lote-alfanumerico-runtime-v3839.js')
DEST = ROOT / 'lote-alfanumerico-runtime-v3839.js'

if not ASSET.exists():
    raise SystemExit('Asset runtime de lote alfanumerico nao encontrado.')

DEST.write_text(ASSET.read_text(encoding='utf-8'), encoding='utf-8')


def ajustar_pagina(nome):
    path = ROOT / nome
    if not path.exists():
        return

    html = path.read_text(encoding='utf-8')
    m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', html, flags=re.I)
    if not m:
        raise SystemExit(f'Campo Lote nao encontrado em {nome}')

    tag = m.group(0)

    if re.search(r'\btype=["\'][^"\']+["\']', tag, flags=re.I):
        tag = re.sub(r'\btype=["\'][^"\']+["\']', 'type="text"', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + ' type="text">'

    for atributo in ('min', 'max', 'step', 'pattern'):
        tag = re.sub(rf'\s+{atributo}=["\'][^"\']*["\']', '', tag, flags=re.I)

    if re.search(r'\binputmode=["\'][^"\']+["\']', tag, flags=re.I):
        tag = re.sub(r'\binputmode=["\'][^"\']+["\']', 'inputmode="text"', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + ' inputmode="text">'

    if not re.search(r'\bautocapitalize=', tag, flags=re.I):
        tag = tag[:-1] + ' autocapitalize="characters">'

    if re.search(r'\bplaceholder=["\'][^"\']*["\']', tag, flags=re.I):
        tag = re.sub(
            r'\bplaceholder=["\'][^"\']*["\']',
            'placeholder="Ex.: 112, AB-123 ou 24/001"',
            tag,
            count=1,
            flags=re.I
        )

    html = html[:m.start()] + tag + html[m.end():]

    script = '<script src="lote-alfanumerico-runtime-v3839.js?v=3839"></script>'
    if script not in html:
        if '</body>' not in html:
            raise SystemExit(f'Nao foi possivel localizar </body> em {nome}')
        html = html.replace('</body>', f'    {script}\n</body>', 1)

    path.write_text(html, encoding='utf-8')


ajustar_pagina('cadastro.html')
ajustar_pagina('editar.html')

for nome in ('cadastro.html', 'editar.html'):
    path = ROOT / nome
    if not path.exists():
        continue
    html = path.read_text(encoding='utf-8')
    m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', html, flags=re.I)
    if not m or not re.search(r'\btype=["\']text["\']', m.group(0), flags=re.I):
        raise SystemExit(f'Campo Lote nao virou texto em {nome}')
    if 'lote-alfanumerico-runtime-v3839.js?v=3839' not in html:
        raise SystemExit(f'Runtime de lote nao foi injetado em {nome}')

print('Lote alfanumerico preparado por runtime: HTML textual + gravacao preservada sem reescrever cadastro.js.')
