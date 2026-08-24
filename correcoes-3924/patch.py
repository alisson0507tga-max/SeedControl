from pathlib import Path
import re

ROOT = Path("native/www")
CAD_JS = ROOT / "cadastro.js"
EDIT_JS = ROOT / "editar.js"
CAD_HTML = ROOT / "cadastro.html"
EDIT_HTML = ROOT / "editar.html"

for path in (CAD_JS, CAD_HTML):
    if not path.exists():
        raise SystemExit(f"Arquivo obrigatorio ausente: {path}")

MARCA = "seedcontrol-cadastro-parcial-v3924"


def remover_required(path: Path):
    if not path.exists():
        return 0
    texto = path.read_text(encoding="utf-8")
    novo, total = re.subn(
        r"\s+required(?:\s*=\s*(?:\"required\"|'required'|required))?",
        "",
        texto,
        flags=re.I,
    )
    path.write_text(novo, encoding="utf-8")
    return total


def liberar_validacao_obrigatoria(path: Path):
    if not path.exists():
        return 0

    texto = path.read_text(encoding="utf-8")
    total = 0

    # Remove somente o bloco que exibe o alerta mostrado no video e interrompe o salvamento.
    padrao = re.compile(
        r"if\s*\((?P<cond>[\s\S]{0,1800}?)\)\s*\{\s*"
        r"alert\s*\(\s*[\"']Preencha todos os campos obrigat(?:ó|o)rios\.?[\"']\s*\)\s*;\s*"
        r"return(?:\s+false)?\s*;\s*\}",
        flags=re.I,
    )

    texto, n = padrao.subn(
        f"/* {MARCA}: campos podem ficar em branco e ser completados depois */",
        texto,
    )
    total += n

    # Se a frase existir em uma variante de formatacao que o regex acima nao capturou,
    # remove o bloco simples mais proximo com seguranca.
    frase = re.compile(r"Preencha todos os campos obrigat(?:ó|o)rios\.?", re.I)
    while True:
        m = frase.search(texto)
        if not m:
            break

        alert_pos = texto.rfind("alert", 0, m.start())
        abre = texto.rfind("{", 0, alert_pos)
        if_pos = texto.rfind("if", 0, abre)
        fecha = texto.find("}", m.end())

        if min(alert_pos, abre, if_pos, fecha) < 0 or abre - if_pos > 1800:
            raise SystemExit(f"Nao foi seguro remover a validacao obrigatoria em {path.name}")

        bloco = texto[if_pos:fecha + 1]
        if "return" not in bloco or "alert" not in bloco:
            raise SystemExit(f"Bloco inesperado da validacao obrigatoria em {path.name}")

        texto = texto[:if_pos] + f"/* {MARCA}: validacao obrigatoria removida */" + texto[fecha + 1:]
        total += 1

    # A protecao de duplicidade continua ativa quando cultivar + lote existem.
    # Se um dos dois estiver vazio, o cadastro e considerado provisório e nao deve ser bloqueado.
    ancora = "const candidato = valoresFormulario();"
    guarda = (
        'const candidato = valoresFormulario();\n'
        '            if (!String(candidato.cultivar || "").trim() || !String(candidato.lote || "").trim()) return;'
    )
    if ancora in texto and "candidato.cultivar ||" not in texto:
        texto = texto.replace(ancora, guarda, 1)

    path.write_text(texto, encoding="utf-8")
    return total


required_total = remover_required(CAD_HTML) + remover_required(EDIT_HTML)
validacoes = liberar_validacao_obrigatoria(CAD_JS) + liberar_validacao_obrigatoria(EDIT_JS)

if validacoes < 1:
    raise SystemExit("Nao encontrei a validacao 'Preencha todos os campos obrigatorios' para remover.")

# Validacao final: o alerta antigo nao pode permanecer.
for path in (CAD_JS, EDIT_JS):
    if not path.exists():
        continue
    texto = path.read_text(encoding="utf-8")
    if re.search(r"Preencha todos os campos obrigat(?:ó|o)rios", texto, flags=re.I):
        raise SystemExit(f"Alerta obrigatorio ainda presente em {path.name}")

for path in (CAD_HTML, EDIT_HTML):
    if not path.exists():
        continue
    texto = path.read_text(encoding="utf-8")
    if re.search(r"\srequired(?:\s*=|\s|>)", texto, flags=re.I):
        raise SystemExit(f"Atributo required ainda presente em {path.name}")

print(f"Cadastro parcial 3924 aplicado: {validacoes} trava(s) removida(s), {required_total} required removido(s).")
