from pathlib import Path
import re

ROOT = Path('native/www')

CAD_HTML = ROOT / 'cadastro.html'
CAD_JS = ROOT / 'cadastro.js'
EDIT_HTML = ROOT / 'editar.html'
EDIT_JS = ROOT / 'editar.js'
CAD_EXTRA = ROOT / 'cadastro-v384.js'

for obrigatorio in (CAD_HTML, CAD_JS):
    if not obrigatorio.exists():
        raise SystemExit(f'Arquivo obrigatorio ausente: {obrigatorio}')


def tornar_input_texto(path: Path):
    if not path.exists():
        return

    texto = path.read_text(encoding='utf-8')
    m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', texto, flags=re.I)
    if not m:
        raise SystemExit(f'Campo id="lote" nao encontrado em {path.name}')

    tag = m.group(0)

    if re.search(r'\btype=["\'][^"\']+["\']', tag, flags=re.I):
        tag = re.sub(r'\btype=["\'][^"\']+["\']', 'type="text"', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + ' type="text">'

    # Remove restricoes tipicas de campo numerico.
    for atributo in ('min', 'max', 'step', 'pattern'):
        tag = re.sub(rf'\s+{atributo}=["\'][^"\']*["\']', '', tag, flags=re.I)

    # Corrige/define inputmode.
    if re.search(r'\binputmode=["\'][^"\']+["\']', tag, flags=re.I):
        tag = re.sub(r'\binputmode=["\'][^"\']+["\']', 'inputmode="text"', tag, count=1, flags=re.I)
    else:
        tag = tag[:-1] + ' inputmode="text">'

    if not re.search(r'\bautocapitalize=', tag, flags=re.I):
        tag = tag[:-1] + ' autocapitalize="characters">'

    # Deixa a dica clara para lote comercial.
    if re.search(r'\bplaceholder=["\'][^"\']*["\']', tag, flags=re.I):
        tag = re.sub(
            r'\bplaceholder=["\'][^"\']*["\']',
            'placeholder="Ex.: 112, AB-123 ou 24/001"',
            tag,
            count=1,
            flags=re.I
        )

    novo = texto[:m.start()] + tag + texto[m.end():]
    path.write_text(novo, encoding='utf-8')


def tornar_lote_string(path: Path):
    if not path.exists():
        return

    texto = path.read_text(encoding='utf-8')

    # Cadastro/edicao principal.
    substituicoes = {
        'lote: Number(document.getElementById("lote").value),': 'lote: document.getElementById("lote").value.trim(),',
        "lote: Number(document.getElementById('lote').value),": "lote: document.getElementById('lote').value.trim(),",
        'registro.lote = Number(document.getElementById("lote").value);': 'registro.lote = document.getElementById("lote").value.trim();',
        "registro.lote = Number(document.getElementById('lote').value);": "registro.lote = document.getElementById('lote').value.trim();",

        # Guardas de duplicidade inseridas pelos patches anteriores.
        'lote: Number(document.getElementById("lote")?.value),': 'lote: String(document.getElementById("lote")?.value || "").trim(),',
        "lote: Number(document.getElementById('lote')?.value),": "lote: String(document.getElementById('lote')?.value || '').trim(),",
        'String(Number(lote && lote.lote) || "")': 'normalizar(lote && lote.lote)',
        "String(Number(lote && lote.lote) || '')": 'normalizar(lote && lote.lote)',
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    # Validacao do cadastro: lote deixa de ser > 0 e passa a ser obrigatorio como texto.
    texto = texto.replace('novoLote.lote <= 0', '!novoLote.lote')

    # Cobre pequenas variacoes de espaco/formato.
    texto = re.sub(
        r'lote\s*:\s*Number\(document\.getElementById\(["\']lote["\']\)\.value\)',
        'lote: document.getElementById("lote").value.trim()',
        texto
    )
    texto = re.sub(
        r'registro\.lote\s*=\s*Number\(document\.getElementById\(["\']lote["\']\)\.value\)\s*;',
        'registro.lote = document.getElementById("lote").value.trim();',
        texto
    )

    path.write_text(texto, encoding='utf-8')


tornar_input_texto(CAD_HTML)
tornar_input_texto(EDIT_HTML)
tornar_lote_string(CAD_JS)
tornar_lote_string(EDIT_JS)

# O modulo visual do cadastro tambem comparava lote como numero.
if CAD_EXTRA.exists():
    texto = CAD_EXTRA.read_text(encoding='utf-8')
    texto = texto.replace(
        'String(Number(item.lote) || "") === String(Number(valor("lote")) || "")',
        'normalizar(item.lote) === normalizar(valor("lote"))'
    )
    CAD_EXTRA.write_text(texto, encoding='utf-8')

# Validacao objetiva daquilo que o usuario precisa.
cad_html = CAD_HTML.read_text(encoding='utf-8')
cad_js = CAD_JS.read_text(encoding='utf-8')

m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', cad_html, flags=re.I)
if not m or not re.search(r'\btype=["\']text["\']', m.group(0), flags=re.I):
    raise SystemExit('Falha: campo Lote do cadastro nao virou texto.')

if 'lote: document.getElementById("lote").value.trim(),' not in cad_js and "lote: document.getElementById('lote').value.trim()," not in cad_js:
    raise SystemExit('Falha: cadastro ainda nao salva Lote como texto.')

if EDIT_HTML.exists() and EDIT_JS.exists():
    edit_html = EDIT_HTML.read_text(encoding='utf-8')
    edit_js = EDIT_JS.read_text(encoding='utf-8')
    me = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', edit_html, flags=re.I)
    if not me or not re.search(r'\btype=["\']text["\']', me.group(0), flags=re.I):
        raise SystemExit('Falha: campo Lote da edicao nao virou texto.')
    if 'registro.lote = document.getElementById("lote").value.trim();' not in edit_js and "registro.lote = document.getElementById('lote').value.trim();" not in edit_js:
        raise SystemExit('Falha: edicao ainda nao salva Lote como texto.')

print('Lote como codigo preparado: aceita numeros e letras sem converter para Number.')
