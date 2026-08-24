from pathlib import Path
import re

ROOT = Path("native/www")
ARQUIVOS_JS = [ROOT / "cadastro.js", ROOT / "editar.js"]
ARQUIVOS_HTML = [ROOT / "cadastro.html", ROOT / "editar.html"]
MARCA = "seedcontrol-cadastro-parcial-v3926"

if not (ROOT / "cadastro.js").is_file() or not (ROOT / "cadastro.html").is_file():
    raise SystemExit("Base de Cadastro ausente para aplicar 3926")


def remover_required(path: Path) -> int:
    if not path.is_file():
        return 0
    texto = path.read_text(encoding="utf-8")
    novo, total = re.subn(
        r"\s+required(?:\s*=\s*(?:\"required\"|'required'|required))?",
        "",
        texto,
        flags=re.I,
    )
    # Se houver form, desliga apenas a validacao HTML nativa.
    novo = re.sub(r"<form(?![^>]*\bnovalidate\b)", "<form novalidate", novo, count=1, flags=re.I)
    path.write_text(novo, encoding="utf-8")
    return total


def liberar_bloqueio_js(path: Path) -> int:
    if not path.is_file():
        return 0
    texto = path.read_text(encoding="utf-8")
    total = 0

    # Caso normal: alert('Preencha todos os campos obrigatorios...'); return;
    padrao = re.compile(
        r"alert\s*\(\s*(?P<q>[\"'`])\s*Preencha\s+todos\s+os\s+campos\s+obrigat(?:ó|o)rios\s*[.!?]?\s*(?P=q)\s*\)\s*;"
        r"(?P<meio>[\s\r\n]*)"
        r"return(?:\s+false)?\s*;",
        flags=re.I,
    )
    texto, n = padrao.subn(
        f"/* {MARCA}: campos podem ser completados depois */",
        texto,
    )
    total += n

    # Fallback conservador: se a frase ainda existir, remove somente o alert e o
    # primeiro return antes do fechamento da mesma chave. Nao remove o IF nem o resto.
    frase = re.compile(r"Preencha\s+todos\s+os\s+campos\s+obrigat(?:ó|o)rios", flags=re.I)
    tentativas = 0
    while True:
        m = frase.search(texto)
        if not m:
            break
        tentativas += 1
        if tentativas > 8:
            raise SystemExit(f"Muitas ocorrencias inesperadas da validacao em {path.name}")

        inicio_alert = texto.rfind("alert", max(0, m.start() - 180), m.start())
        if inicio_alert < 0:
            raise SystemExit(f"Frase obrigatoria sem alert reconhecivel em {path.name}")

        fim_alert = texto.find(";", m.end())
        if fim_alert < 0 or fim_alert - inicio_alert > 500:
            raise SystemExit(f"Alert obrigatorio inesperado em {path.name}")

        fecha = texto.find("}", fim_alert + 1)
        limite = fecha if fecha >= 0 else min(len(texto), fim_alert + 500)
        trecho = texto[fim_alert + 1:limite]
        mr = re.search(r"\breturn(?:\s+false)?\s*;", trecho, flags=re.I)
        if not mr:
            raise SystemExit(f"Alert obrigatorio sem return seguro em {path.name}")

        ini_ret = fim_alert + 1 + mr.start()
        fim_ret = fim_alert + 1 + mr.end()
        texto = (
            texto[:inicio_alert]
            + f"/* {MARCA}: alerta obrigatorio removido */"
            + texto[fim_alert + 1:ini_ret]
            + f"/* {MARCA}: return obrigatorio removido */"
            + texto[fim_ret:]
        )
        total += 1

    # A camada de duplicidade e separada. Com cultivar ou lote vazio, ela nao deve
    # bloquear um cadastro provisório. O click continua para o salvamento original.
    ancora = "const candidato = valoresFormulario();\n            const chaveCandidato = chave(candidato);"
    if ancora in texto and "seedcontrol-parcial-duplicidade-v3926" not in texto:
        troca = (
            "const candidato = valoresFormulario();\n"
            "            if (!String(candidato.cultivar || \"\").trim() || !String(candidato.lote || \"\").trim()) {\n"
            "                // seedcontrol-parcial-duplicidade-v3926: sem chave completa, nao compara duplicidade\n"
            "                return;\n"
            "            }\n"
            "            const chaveCandidato = chave(candidato);"
        )
        texto = texto.replace(ancora, troca, 1)

    path.write_text(texto, encoding="utf-8")
    return total


required_total = sum(remover_required(p) for p in ARQUIVOS_HTML)
bloqueios = sum(liberar_bloqueio_js(p) for p in ARQUIVOS_JS)

if bloqueios < 1:
    raise SystemExit("3926 nao encontrou nenhum bloqueio de campos obrigatorios na base gerada")

# Validacoes finais focadas somente no problema corrigido.
for p in ARQUIVOS_JS:
    if not p.is_file():
        continue
    txt = p.read_text(encoding="utf-8")
    if re.search(r"Preencha\s+todos\s+os\s+campos\s+obrigat(?:ó|o)rios", txt, flags=re.I):
        raise SystemExit(f"Validacao obrigatoria ainda presente em {p.name}")

for p in ARQUIVOS_HTML:
    if not p.is_file():
        continue
    txt = p.read_text(encoding="utf-8")
    if re.search(r"\srequired(?:\s*=|\s|>)", txt, flags=re.I):
        raise SystemExit(f"Atributo required ainda presente em {p.name}")

print(f"Cadastro parcial 3926 aplicado: {bloqueios} bloqueio(s), {required_total} required removido(s).")
