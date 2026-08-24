from pathlib import Path
import re

ROOT = Path('native/www')
CAD_JS = ROOT / 'cadastro.js'
EDIT_JS = ROOT / 'editar.js'
CAD_HTML = ROOT / 'cadastro.html'
EDIT_HTML = ROOT / 'editar.html'

for p in (CAD_JS, CAD_HTML):
    if not p.exists():
        raise SystemExit(f'Arquivo obrigatorio ausente: {p}')

MARCA = 'seedcontrol-cadastro-parcial-v3925'

# Remove somente validacao HTML nativa; nao mexe na estrutura dos formularios.
def remover_required(path: Path):
    if not path.exists():
        return 0
    texto = path.read_text(encoding='utf-8')
    novo, n = re.subn(r'\s+required(?:\s*=\s*(?:"required"|\'required\'|required))?', '', texto, flags=re.I)
    # Garante que um <form> eventual nao reative validacao nativa.
    novo = re.sub(r'<form(\s|>)', lambda m: '<form novalidate' + m.group(1) if 'novalidate' not in m.group(0).lower() else m.group(0), novo, count=1, flags=re.I)
    path.write_text(novo, encoding='utf-8')
    return n

# Remove APENAS o par alerta + return. O if, as chaves e todo o resto do JS ficam intactos.
def liberar_alerta_return(path: Path):
    if not path.exists():
        return 0
    texto = path.read_text(encoding='utf-8')
    padrao = re.compile(
        r'alert\s*\(\s*(["\'])Preencha todos os campos obrigat(?:ó|o)rios\.?\1\s*\)\s*;\s*return(?:\s+false)?\s*;',
        flags=re.I,
    )
    texto, n = padrao.subn(f'/* {MARCA}: permite salvar e completar depois */', texto)

    # A protecao de duplicidade so deve rodar quando cultivar E lote estiverem informados.
    ancora = 'const candidato = valoresFormulario();'
    guarda = (
        'const candidato = valoresFormulario();\n'
        '            if (!String(candidato.cultivar || "").trim() || !String(candidato.lote || "").trim()) return;'
    )
    if ancora in texto and 'candidato.cultivar || ""' not in texto:
        texto = texto.replace(ancora, guarda, 1)

    path.write_text(texto, encoding='utf-8')
    return n

required = remover_required(CAD_HTML) + remover_required(EDIT_HTML)
removidos = liberar_alerta_return(CAD_JS) + liberar_alerta_return(EDIT_JS)

# Cadastro precisa ter sido realmente liberado. Editar pode nao possuir a mesma trava na base.
if removidos < 1:
    raise SystemExit('Nao encontrei a sequencia segura alerta + return da validacao obrigatoria.')

# Validacao final sem regex estrutural agressivo.
for p in (CAD_JS, EDIT_JS):
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8')
    if re.search(r'alert\s*\(\s*["\']Preencha todos os campos obrigat(?:ó|o)rios', txt, flags=re.I):
        raise SystemExit(f'Alerta obrigatorio ainda presente em {p.name}')

for p in (CAD_HTML, EDIT_HTML):
    if not p.exists():
        continue
    txt = p.read_text(encoding='utf-8')
    if re.search(r'\srequired(?:\s*=|\s|>)', txt, flags=re.I):
        raise SystemExit(f'Atributo required ainda presente em {p.name}')

print(f'Cadastro parcial 3925 aplicado com seguranca: {removidos} bloqueio(s) removido(s), {required} required removido(s).')
