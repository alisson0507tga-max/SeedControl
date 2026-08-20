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

LOTE_EXPR = 'String(document.getElementById("lote").value || "").trim()'


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

    path.write_text(texto[:m.start()] + tag + texto[m.end():], encoding='utf-8')


def substituir_conversoes_do_lote(texto: str):
    alteracoes = 0

    # Acesso direto ao input #lote.
    padroes = [
        r'Number\s*\(\s*document\.getElementById\(\s*["\']lote["\']\s*\)\.value\s*\)',
        r'parseInt\s*\(\s*document\.getElementById\(\s*["\']lote["\']\s*\)\.value(?:\s*,\s*\d+)?\s*\)',
        r'parseFloat\s*\(\s*document\.getElementById\(\s*["\']lote["\']\s*\)\.value\s*\)',
        r'document\.getElementById\(\s*["\']lote["\']\s*\)\.valueAsNumber',
        r'\+\s*document\.getElementById\(\s*["\']lote["\']\s*\)\.value\b',
    ]

    for padrao in padroes:
        texto, n = re.subn(padrao, LOTE_EXPR, texto)
        alteracoes += n

    # Se o codigo guarda primeiro o elemento em uma variavel, cobre tambem esse formato.
    variaveis = set(re.findall(
        r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*document\.getElementById\(\s*["\']lote["\']\s*\)',
        texto
    ))

    for var in variaveis:
        v = re.escape(var)
        padroes_var = [
            rf'Number\s*\(\s*{v}\.value\s*\)',
            rf'parseInt\s*\(\s*{v}\.value(?:\s*,\s*\d+)?\s*\)',
            rf'parseFloat\s*\(\s*{v}\.value\s*\)',
            rf'{v}\.valueAsNumber',
            rf'\+\s*{v}\.value\b',
        ]
        for padrao in padroes_var:
            texto, n = re.subn(padrao, f'String({var}.value || "").trim()', texto)
            alteracoes += n

    return texto, alteracoes, variaveis


def tornar_lote_string(path: Path):
    if not path.exists():
        return set()

    texto = path.read_text(encoding='utf-8')

    # Guardas de duplicidade inseridas pelos patches anteriores.
    texto = texto.replace(
        'String(Number(lote && lote.lote) || "")',
        'normalizar(lote && lote.lote)'
    )
    texto = texto.replace(
        "String(Number(lote && lote.lote) || '')",
        'normalizar(lote && lote.lote)'
    )

    # Compatibilidade com candidatos de duplicidade que liam o campo como Number.
    texto = texto.replace(
        'lote: Number(document.getElementById("lote")?.value),',
        'lote: String(document.getElementById("lote")?.value || "").trim(),'
    )
    texto = texto.replace(
        "lote: Number(document.getElementById('lote')?.value),",
        "lote: String(document.getElementById('lote')?.value || '').trim(),"
    )

    texto, alteracoes, variaveis = substituir_conversoes_do_lote(texto)

    # Validacoes numericas conhecidas passam a exigir somente codigo preenchido.
    texto = texto.replace('novoLote.lote <= 0', '!String(novoLote.lote || "").trim()')
    texto = texto.replace('registro.lote <= 0', '!String(registro.lote || "").trim()')

    path.write_text(texto, encoding='utf-8')
    print(f'{path.name}: {alteracoes} conversao(oes) numerica(s) do lote substituida(s).')
    return variaveis


def validar_sem_conversao_numerica(path: Path, variaveis):
    if not path.exists():
        return

    texto = path.read_text(encoding='utf-8')

    diretos = [
        r'Number\s*\(\s*document\.getElementById\(\s*["\']lote["\']',
        r'parseInt\s*\(\s*document\.getElementById\(\s*["\']lote["\']',
        r'parseFloat\s*\(\s*document\.getElementById\(\s*["\']lote["\']',
        r'document\.getElementById\(\s*["\']lote["\']\s*\)\.valueAsNumber',
    ]

    for padrao in diretos:
        if re.search(padrao, texto):
            raise SystemExit(f'Falha: ainda existe conversao numerica direta do Lote em {path.name}.')

    for var in variaveis:
        v = re.escape(var)
        if re.search(rf'(?:Number|parseInt|parseFloat)\s*\(\s*{v}\.value|{v}\.valueAsNumber', texto):
            raise SystemExit(f'Falha: ainda existe conversao numerica do Lote pela variavel {var} em {path.name}.')


tornar_input_texto(CAD_HTML)
tornar_input_texto(EDIT_HTML)
vars_cad = tornar_lote_string(CAD_JS)
vars_edit = tornar_lote_string(EDIT_JS)

# O modulo visual do cadastro tambem comparava lote como numero.
if CAD_EXTRA.exists():
    texto = CAD_EXTRA.read_text(encoding='utf-8')
    texto = texto.replace(
        'String(Number(item.lote) || "") === String(Number(valor("lote")) || "")',
        'normalizar(item.lote) === normalizar(valor("lote"))'
    )
    CAD_EXTRA.write_text(texto, encoding='utf-8')

# Validacao objetiva: campo textual e nenhuma conversao numerica conhecida do #lote.
for html_path in (CAD_HTML, EDIT_HTML):
    if not html_path.exists():
        continue
    texto = html_path.read_text(encoding='utf-8')
    m = re.search(r'<input\b[^>]*\bid=["\']lote["\'][^>]*>', texto, flags=re.I)
    if not m or not re.search(r'\btype=["\']text["\']', m.group(0), flags=re.I):
        raise SystemExit(f'Falha: campo Lote de {html_path.name} nao virou texto.')

validar_sem_conversao_numerica(CAD_JS, vars_cad)
validar_sem_conversao_numerica(EDIT_JS, vars_edit)

if CAD_EXTRA.exists():
    texto = CAD_EXTRA.read_text(encoding='utf-8')
    if 'String(Number(item.lote)' in texto:
        raise SystemExit('Falha: comparacao numerica de lote ainda existe em cadastro-v384.js.')

print('Lote como codigo preparado: aceita letras e numeros sem depender do formato interno do cadastro.')
