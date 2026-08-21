from pathlib import Path
import re

ROOT = Path('native/www')
SRC = Path('correcoes-3911/lote-texto-guard-v3911.js')
DEST = ROOT / 'lote-texto-guard-v3911.js'

if not ROOT.exists():
    raise SystemExit('native/www nao encontrado')
if not SRC.exists():
    raise SystemExit('Guard 3911 nao encontrado')

DEST.write_text(SRC.read_text(encoding='utf-8'), encoding='utf-8')

# Corrige as formas conhecidas de conversao numerica do campo lote,
# inclusive variacoes que os patches anteriores podiam nao alcancar.
for nome in ('cadastro.js', 'editar.js', 'database.js'):
    path = ROOT / nome
    if not path.exists():
        continue
    js = path.read_text(encoding='utf-8')

    # lote: Number/parseInt/parseFloat(document.getElementById('lote')...)
    js = re.sub(
        r'lote\s*:\s*(?:Number|parseInt|parseFloat)\(\s*document\.getElementById\(["\']lote["\']\)(?:\?\.)?\.value\s*\)',
        'lote: String(document.getElementById("lote")?.value || "").trim()',
        js,
        flags=re.I,
    )

    # registro.lote = Number/parseInt/parseFloat(document.getElementById('lote')...)
    js = re.sub(
        r'([A-Za-z_$][\w$]*\.lote\s*=\s*)(?:Number|parseInt|parseFloat)\(\s*document\.getElementById\(["\']lote["\']\)(?:\?\.)?\.value\s*\)',
        r'\1String(document.getElementById("lote")?.value || "").trim()',
        js,
        flags=re.I,
    )

    # Variacoes que usam helper valor('lote').
    js = re.sub(
        r'lote\s*:\s*(?:Number|parseInt|parseFloat)\(\s*valor\(["\']lote["\']\)\s*\)',
        'lote: String(valor("lote") || "").trim()',
        js,
        flags=re.I,
    )
    js = re.sub(
        r'([A-Za-z_$][\w$]*\.lote\s*=\s*)(?:Number|parseInt|parseFloat)\(\s*valor\(["\']lote["\']\)\s*\)',
        r'\1String(valor("lote") || "").trim()',
        js,
        flags=re.I,
    )

    path.write_text(js, encoding='utf-8')

# Injeta o guard depois dos scripts existentes, no fim da pagina.
tag = '<script src="lote-texto-guard-v3911.js?v=3911"></script>'
for nome in ('cadastro.html', 'editar.html'):
    path = ROOT / nome
    if not path.exists():
        continue
    html = path.read_text(encoding='utf-8')
    if tag not in html:
        if '</body>' not in html:
            raise SystemExit(f'</body> nao encontrado em {nome}')
        html = html.replace('</body>', f'    {tag}\n</body>', 1)
    path.write_text(html, encoding='utf-8')

# Validacoes finais.
for nome in ('cadastro.html', 'editar.html'):
    path = ROOT / nome
    if path.exists() and 'lote-texto-guard-v3911.js?v=3911' not in path.read_text(encoding='utf-8'):
        raise SystemExit(f'Guard 3911 nao injetado em {nome}')

if 'seedcontrol-lote-texto-guard-v3911' not in DEST.read_text(encoding='utf-8'):
    raise SystemExit('Marcador do guard 3911 ausente')

print('Correcao 3911 aplicada: lote alfanumerico preservado no cadastro e na edicao.')
