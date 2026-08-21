from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3915")
INDEX = ROOT / "index.html"
DASH_CSS = ROOT / "dashboard-v384.css"

ARQUIVOS = [
    "detalhes-dashboard.html",
    "detalhes-dashboard-v3915.css",
    "detalhes-dashboard-v3915.js",
    "dashboard-cards-v3915.js",
]

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not INDEX.exists():
    raise SystemExit("index.html nao encontrado")

for nome in ARQUIVOS:
    origem = SRC / nome
    if not origem.exists():
        raise SystemExit(f"Arquivo 3915 ausente: {origem}")
    shutil.copy2(origem, ROOT / nome)

html = INDEX.read_text(encoding="utf-8")
tag = '<script src="dashboard-cards-v3915.js?v=3915"></script>'
if tag not in html:
    if "</body>" not in html:
        raise SystemExit("</body> ausente em index.html")
    html = html.replace("</body>", f"    {tag}\n</body>", 1)
INDEX.write_text(html, encoding="utf-8")

if DASH_CSS.exists():
    css = DASH_CSS.read_text(encoding="utf-8")
    marca = "/* seedcontrol-dashboard-cards-click-v3915 */"
    if marca not in css:
        css += """

/* seedcontrol-dashboard-cards-click-v3915 */
#dashboard .metric-card[data-seed-detalhe3915]{cursor:pointer;transition:transform .12s ease,border-color .12s ease,background .12s ease}
#dashboard .metric-card[data-seed-detalhe3915]:active{transform:scale(.985);border-color:rgba(74,222,128,.68)}
#dashboard .metric-card[data-seed-detalhe3915]:focus-visible{outline:2px solid #4ade80;outline-offset:2px}
"""
        DASH_CSS.write_text(css, encoding="utf-8")

sw = ROOT / "service-worker.js"
if sw.exists():
    texto = sw.read_text(encoding="utf-8")
    texto = re.sub(r"seedcontrol-v3\.8-pwa-[A-Za-z0-9._-]+", "seedcontrol-v3.8-pwa-3915", texto, count=1)
    sw.write_text(texto, encoding="utf-8")

validacoes = [
    (INDEX, "dashboard-cards-v3915.js?v=3915"),
    (ROOT / "dashboard-cards-v3915.js", "seedcontrol-dashboard-cards-v3915"),
    (ROOT / "dashboard-cards-v3915.js", "detalhes-dashboard.html?tipo="),
    (ROOT / "detalhes-dashboard.html", "detalhes-dashboard-v3915.js?v=3915"),
    (ROOT / "detalhes-dashboard-v3915.js", 'localStorage.getItem("estoque")'),
    (ROOT / "detalhes-dashboard-v3915.js", '"fazendas"'),
    (ROOT / "detalhes-dashboard-v3915.js", '"cultivares"'),
    (ROOT / "detalhes-dashboard-v3915.js", '"lotes"'),
    (ROOT / "detalhes-dashboard-v3915.css", "seedcontrol-detalhes-dashboard-v3915"),
]
for arquivo, trecho in validacoes:
    if not arquivo.exists():
        raise SystemExit(f"Arquivo nao encontrado: {arquivo}")
    if trecho not in arquivo.read_text(encoding="utf-8"):
        raise SystemExit(f"Validacao 3915 falhou em {arquivo.name}: {trecho}")

print("3915 aplicada: cards do Dashboard abrem detalhamento por fazenda, cultivar, lote, Bags, Kg e Sacas.")
