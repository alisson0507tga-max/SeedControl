from pathlib import Path
import re

ROOT = Path("native/www")
HTML = ROOT / "planilha.html"
SW = ROOT / "service-worker.js"

for arquivo in (HTML, SW):
    if not arquivo.exists():
        raise SystemExit(f"Arquivo não encontrado: {arquivo}")

html = HTML.read_text(encoding="utf-8")
html = re.sub(
    r'src=["\']planilha\.js(?:\?v=[^"\']*)?["\']',
    'src="planilha.js?v=3830"',
    html,
    count=1,
    flags=re.I
)
HTML.write_text(html, encoding="utf-8")

sw = SW.read_text(encoding="utf-8")
sw = re.sub(
    r'seedcontrol-v3\.8-pwa-\d+',
    'seedcontrol-v3.8-pwa-30',
    sw,
    count=1
)

if '"./dados-soja2026-v3830.js"' not in sw:
    ancora = '    "./database.js",'
    if ancora in sw:
        sw = sw.replace(
            ancora,
            ancora + '\n\n    "./dados-soja2026-v3830.js",',
            1
        )

SW.write_text(sw, encoding="utf-8")

html_final = HTML.read_text(encoding="utf-8")
sw_final = SW.read_text(encoding="utf-8")

if 'planilha.js?v=3830' not in html_final:
    raise SystemExit("planilha.html não recebeu a versão 3830 do JS.")
if 'seedcontrol-v3.8-pwa-30' not in sw_final:
    raise SystemExit("Service Worker não foi atualizado para pwa-30.")
if './dados-soja2026-v3830.js' not in sw_final:
    raise SystemExit("Importador Soja 2026 não entrou no cache principal.")

print("Cache Soja 2026 preparado: planilha v3830 e importador incluídos.")
