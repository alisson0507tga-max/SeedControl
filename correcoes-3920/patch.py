from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3920/safe-area-v3920.css")
DST = ROOT / "safe-area-v3920.css"

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not SRC.exists():
    raise SystemExit("safe-area-v3920.css ausente")

shutil.copy2(SRC, DST)

# Telas em que o usuario mostrou conteudo encostando nas barras do Android.
paginas = [
    "index.html",
    "detalhes-dashboard.html",
    "estoque.html",
    "planilha.html",
    "entrada-comercial.html",
    "relatorio-saidas.html",
]

alteradas = 0
for nome in paginas:
    arq = ROOT / nome
    if not arq.exists():
        # Algumas bases podem nao ter uma tela opcional; as essenciais sao validadas abaixo.
        continue
    html = arq.read_text(encoding="utf-8")

    # Garante viewport apropriado para barras/safe-area.
    if "viewport-fit=cover" not in html:
        html = re.sub(
            r'(<meta\s+name=["\']viewport["\'][^>]*content=["\'])([^"\']*)(["\'][^>]*>)',
            lambda m: m.group(1) + (m.group(2).rstrip() + ", viewport-fit=cover") + m.group(3),
            html,
            count=1,
            flags=re.I,
        )

    if "safe-area-v3920.css" not in html:
        tag = '<link rel="stylesheet" href="safe-area-v3920.css?v=3920">'
        if "</head>" not in html:
            raise SystemExit(f"</head> ausente em {nome}")
        html = html.replace("</head>", f"    {tag}\n</head>", 1)

    arq.write_text(html, encoding="utf-8")
    alteradas += 1

# Cache novo.
sw = ROOT / "service-worker.js"
if sw.exists():
    txt = sw.read_text(encoding="utf-8")
    txt = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3920", txt, count=1)
    sw.write_text(txt, encoding="utf-8")

# Validacoes essenciais.
for nome in ("index.html", "estoque.html", "planilha.html", "entrada-comercial.html", "relatorio-saidas.html"):
    arq = ROOT / nome
    if not arq.exists():
        raise SystemExit(f"Tela essencial ausente: {nome}")
    if "safe-area-v3920.css?v=3920" not in arq.read_text(encoding="utf-8"):
        raise SystemExit(f"Area segura 3920 nao injetada em {nome}")

css = DST.read_text(encoding="utf-8")
for marca in ("padding-top: 6px", "padding-bottom: 18px", "scroll-padding-bottom: 28px"):
    if marca not in css:
        raise SystemExit(f"CSS 3920 sem marca: {marca}")

print(f"Area segura visual 3920 aplicada em {alteradas} telas.")
