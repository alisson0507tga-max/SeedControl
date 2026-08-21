from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3919")
JS_SRC = SRC / "fazendas-contagem-v3919.js"
JS_DST = ROOT / JS_SRC.name
INDEX = ROOT / "index.html"

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not JS_SRC.exists():
    raise SystemExit("fazendas-contagem-v3919.js ausente")
if not INDEX.exists():
    raise SystemExit("index.html ausente")

shutil.copy2(JS_SRC, JS_DST)

html = INDEX.read_text(encoding="utf-8")
if "fazendas-contagem-v3919.js" not in html:
    tag = '<script src="fazendas-contagem-v3919.js?v=3919"></script>'
    html = html.replace("</body>", f"    {tag}\n</body>", 1) if "</body>" in html else html + "\n" + tag
    INDEX.write_text(html, encoding="utf-8")

sw = ROOT / "service-worker.js"
if sw.exists():
    txt = sw.read_text(encoding="utf-8")
    txt = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3919", txt, count=1)
    sw.write_text(txt, encoding="utf-8")

index_final = INDEX.read_text(encoding="utf-8")
js_final = JS_DST.read_text(encoding="utf-8")
if 'fazendas-contagem-v3919.js?v=3919' not in index_final:
    raise SystemExit("Script 3919 nao entrou no Dashboard")
for marca in (
    "seedcontrol-fazendas-contagem-v3919",
    "seedcontrol_entrada_comercial_2026",
    "ehComercial",
    "fazendaValida",
    'document.getElementById("fazendas")',
):
    if marca not in js_final:
        raise SystemExit(f"Validacao 3919 falhou: {marca}")

print("Correcao 3919 aplicada: contador de Fazendas da Home usa a mesma regra dos detalhes e exclui sementes comerciais.")
