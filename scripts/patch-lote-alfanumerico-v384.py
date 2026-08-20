from pathlib import Path
import re

ROOT = Path('native/www')
CAD_HTML = ROOT / 'cadastro.html'
CAD_JS = ROOT / 'cadastro.js'
EDIT_HTML = ROOT / 'editar.html'
EDIT_JS = ROOT / 'editar.js'
CAD_EXTRA = ROOT / 'cadastro-v384.js'
ESTOQUE_JS = ROOT / 'estoque.js'

for arquivo in (CAD_HTML, CAD_JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo obrigatorio nao encontrado: {arquivo}')


def ajustar_input_lote(path: Path):
    if not path.exists():
        return

    texto = path.read_text(encoding='utf-8')

    padrao = re.compile(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', re.I)
    m = padrao.search(texto)
    if not m:
        raise SystemExit(f'Campo lote nao encontrado em {path.name}')

    tag = m.group(0)
    novo = tag

    if re.search(r'\btype=["\']number["\']', novo, flags=re.I):
        novo = re.sub(r'\btype=["\']number["\']', 'type="text"', novo, count=1, flags=re.I)
    elif not re.search(r'\btype=', novo, flags=re.I):
        novo = novo[:-1] + ' type="text">'

    atributos = {
        'inputmode': 'text',
        'autocapitalize': 'characters',
        'autocomplete': 'off',
        'spellcheck': 'false'
    }

    for nome, valor in atributos.items():
        if not re.search(rf'\b{nome}=', novo, flags=re.I):
            novo = novo[:-1] + f' {nome}="{valor}">'

    # Deixa claro que letras e numeros sao aceitos.
    if re.search(r'placeholder=["\'][^"\']*["\']', novo, flags=re.I):
        novo = re.sub(
            r'placeholder=["\'][^"\']*["\']',
            'placeholder="Ex.: 112, AB-123 ou 24/001"',
            novo,
            count=1,
            flags=re.I
        )

    texto = texto[:m.start()] + novo + texto[m.end():]
    path.write_text(texto, encoding='utf-8')


def ajustar_js(path: Path):
    if not path.exists():
        return

    texto = path.read_text(encoding='utf-8')

    # Protecao de duplicidade antiga: lote era normalizado como numero.
    texto = texto.replace(
        'String(Number(lote && lote.lote) || "")',
        'normalizar(lote && lote.lote)'
    )

    # Candidato da protecao de duplicidade.
    texto = texto.replace(
        'lote: Number(document.getElementById("lote")?.value),',
        'lote: String(document.getElementById("lote")?.value || "").trim(),'
    )

    # Cadastro principal.
    texto = texto.replace(
        'lote: Number(document.getElementById("lote").value),',
        'lote: document.getElementById("lote").value.trim(),'
    )

    # Edicao principal.
    texto = texto.replace(
        'registro.lote = Number(document.getElementById("lote").value);',
        'registro.lote = document.getElementById("lote").value.trim();'
    )

    # Validacao antiga exigia valor numerico maior que zero.
    texto = texto.replace(
        'novoLote.lote <= 0',
        '!novoLote.lote'
    )

    # Compatibilidade com eventuais variacoes sem optional chaining.
    texto = re.sub(
        r'lote:\s*Number\(document\.getElementById\(["\']lote["\']\)\.value\)',
        'lote: document.getElementById("lote").value.trim()',
        texto
    )

    path.write_text(texto, encoding='utf-8')


ajustar_input_lote(CAD_HTML)
ajustar_input_lote(EDIT_HTML)
ajustar_js(CAD_JS)
ajustar_js(EDIT_JS)

# O complemento visual do cadastro tambem tinha uma comparacao numerica
# propria para detectar duplicidade quando ha foto da nota de entrada.
if CAD_EXTRA.exists():
    texto = CAD_EXTRA.read_text(encoding='utf-8')
    texto = texto.replace(
        'String(Number(item.lote) || "") === String(Number(valor("lote")) || "")',
        'normalizar(item.lote) === normalizar(valor("lote"))'
    )
    CAD_EXTRA.write_text(texto, encoding='utf-8')

# Se a ordenacao do Estoque ainda estiver usando subtracao numerica,
# troca por ordenacao natural que funciona para 2, 10, A2, A10, AB-123 etc.
if ESTOQUE_JS.exists():
    texto = ESTOQUE_JS.read_text(encoding='utf-8')
    texto = re.sub(
        r'Number\((\w+)\.lote\)\s*-\s*Number\((\w+)\.lote\)',
        r'String(\1.lote ?? "").localeCompare(String(\2.lote ?? ""), "pt-BR", { numeric: true, sensitivity: "base" })',
        texto
    )
    ESTOQUE_JS.write_text(texto, encoding='utf-8')

# Validacoes finais: nada de converter lote para Number no cadastro/edicao.
for path in (CAD_JS, EDIT_JS):
    if not path.exists():
        continue
    texto = path.read_text(encoding='utf-8')
    if re.search(r'Number\(document\.getElementById\(["\']lote["\']\)', texto):
        raise SystemExit(f'Ainda existe conversao numerica do lote em {path.name}')

for path in (CAD_HTML, EDIT_HTML):
    if not path.exists():
        continue
    texto = path.read_text(encoding='utf-8')
    m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', texto, flags=re.I)
    if not m or 'type="text"' not in m.group(0).lower():
        raise SystemExit(f'Campo lote ainda nao esta textual em {path.name}')

if CAD_EXTRA.exists():
    texto = CAD_EXTRA.read_text(encoding='utf-8')
    if 'String(Number(item.lote)' in texto:
        raise SystemExit('Comparacao numerica de lote ainda existe em cadastro-v384.js')

print('Lote alfanumerico preparado: cadastro, edicao e duplicidade aceitam letras, numeros, hifen e barra.')
