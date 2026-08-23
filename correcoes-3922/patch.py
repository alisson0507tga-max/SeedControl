from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3922/entrada-comercial-lote-v3922.js")
DST = ROOT / "entrada-comercial-lote-v3922.js"
HTML = ROOT / "entrada-comercial.html"
SW = ROOT / "service-worker.js"

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not SRC.exists():
    raise SystemExit("entrada-comercial-lote-v3922.js ausente")
if not HTML.exists():
    raise SystemExit("entrada-comercial.html ausente")

shutil.copy2(SRC, DST)

html = HTML.read_text(encoding="utf-8")
script = '<script src="entrada-comercial-lote-v3922.js?v=3922"></script>'

if "entrada-comercial-lote-v3922.js" not in html:
    ancora = '<script src="entrada-comercial-core-v3904.js"></script>'
    if ancora not in html:
        raise SystemExit("Core Entrada Comercial 3904 nao encontrado para injecao 3922")
    html = html.replace(ancora, ancora + "\n" + script, 1)
    HTML.write_text(html, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3922", sw, count=1)
    SW.write_text(sw, encoding="utf-8")

final = HTML.read_text(encoding="utf-8")n = final.find("entrada-comercial-lote-v3922.js")
core = final.find("entrada-comercial-core-v3904.js")
ui = final.find("entrada-comercial-v3904.js")

if min(core, n, ui) < 0:
    raise SystemExit("Scripts obrigatorios da Entrada Comercial ausentes")
if not (core < n < ui):
    raise SystemExit("Ordem de scripts invalida: 3922 precisa carregar entre core e UI")

js = DST.read_text(encoding="utf-8")
for marca in (
    "seedcontrol-entrada-comercial-lote-v3922",
    "origemLoteId",
    "origemChave",
    "acharLote3922",
    "repararLista3922",
    "window.carregarEntradasComerciais3904",
    "window.salvarEntradasComerciais3904",
):
    if marca not in js:
        raise SystemExit(f"Correcao 3922 sem marca: {marca}")

print("Correcao 3922 aplicada: lote ausente da Entrada Comercial e exportacoes recuperado do Estoque.")
