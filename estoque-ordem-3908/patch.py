from pathlib import Path
import shutil

SRC = Path("estoque-ordem-3908/ordem.js")
DST = Path("native/www/estoque-ordem-v3908.js")
PAGINAS = [
    Path("native/www/cadastro.html"),
    Path("native/www/estoque.html"),
]

if not SRC.exists():
    raise SystemExit("ordem.js 3908 nao encontrado")

for pagina in PAGINAS:
    if not pagina.exists():
        raise SystemExit(f"Pagina ausente: {pagina}")

shutil.copy2(SRC, DST)

for pagina in PAGINAS:
    html = pagina.read_text(encoding="utf-8")
    if "estoque-ordem-v3908.js" not in html:
        tag = '<script src="estoque-ordem-v3908.js?v=3908"></script>'
        if "</body>" in html:
            html = html.replace("</body>", tag + "\n</body>", 1)
        else:
            html += "\n" + tag + "\n"
        pagina.write_text(html, encoding="utf-8")

final_js = DST.read_text(encoding="utf-8")

for marca in (
    "seedcontrol-estoque-ordem-recente-v3908",
    "dataCadastro",
    "isoPeloId",
    "setItem3908",
    "data_desc",
):
    if marca not in final_js:
        raise SystemExit(f"Marca 3908 ausente: {marca}")

for pagina in PAGINAS:
    final_html = pagina.read_text(encoding="utf-8")
    if "estoque-ordem-v3908.js?v=3908" not in final_html:
        raise SystemExit(f"Script 3908 nao entrou em {pagina.name}")

print("Ordem recente 3908 aplicada: lote novo recebe dataCadastro e registros sem data usam ID temporal quando possivel.")
