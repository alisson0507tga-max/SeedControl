from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3916")

COMERCIAL_SRC = SRC / "comercial-campos-v3916.js"
ZOOM_SRC = SRC / "nota-zoom-pan-v3916.js"
COMERCIAL_DST = ROOT / COMERCIAL_SRC.name
ZOOM_DST = ROOT / ZOOM_SRC.name

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
for arq in (COMERCIAL_SRC, ZOOM_SRC):
    if not arq.exists():
        raise SystemExit(f"Arquivo 3916 ausente: {arq}")

shutil.copy2(COMERCIAL_SRC, COMERCIAL_DST)
shutil.copy2(ZOOM_SRC, ZOOM_DST)


def injetar(pagina: Path, tag: str, marca: str):
    if not pagina.exists():
        return False
    html = pagina.read_text(encoding="utf-8")
    if marca not in html:
        if "</body>" in html:
            html = html.replace("</body>", f"    {tag}\n</body>", 1)
        else:
            html += "\n" + tag + "\n"
        pagina.write_text(html, encoding="utf-8")
    return True

# Comercial: cadastro e edicao devem ter o mesmo comportamento.
tag_comercial = '<script src="comercial-campos-v3916.js?v=3916"></script>'
injetadas_comercial = 0
for nome in ("cadastro.html", "editar.html"):
    if injetar(ROOT / nome, tag_comercial, "comercial-campos-v3916.js"):
        injetadas_comercial += 1
if injetadas_comercial < 1:
    raise SystemExit("Nenhuma tela recebeu a regra do modo Comercial 3916")

# Zoom: Estoque, detalhes de cultivar e Entrada Comercial.
tag_zoom = '<script src="nota-zoom-pan-v3916.js?v=3916"></script>'
paginas_zoom = [ROOT / "estoque.html", ROOT / "entrada-comercial.html"]
paginas_zoom.extend(sorted(ROOT.glob("*cultivar*.html")))

injetadas_zoom = 0
vistos = set()
for pagina in paginas_zoom:
    if pagina in vistos:
        continue
    vistos.add(pagina)
    if injetar(pagina, tag_zoom, "nota-zoom-pan-v3916.js"):
        injetadas_zoom += 1
if injetadas_zoom < 1:
    raise SystemExit("Nenhuma tela recebeu zoom da nota 3916")

# Forca nova revisao do cache para as paginas receberem os scripts novos.
sw = ROOT / "service-worker.js"
if sw.exists():
    texto = sw.read_text(encoding="utf-8")
    texto = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3916", texto, count=1)
    sw.write_text(texto, encoding="utf-8")

checks = {
    COMERCIAL_DST: (
        "seedcontrol-comercial-campos-v3916",
        "situacao da secagem",
        "seed-modo-comercial-v3916",
        "required",
    ),
    ZOOM_DST: (
        "seedcontrol-nota-zoom-pan-v3916",
        "pointerdown",
        "pointermove",
        "Use dois dedos",
        "scale(${estado.scale})",
    ),
}
for arquivo, marcas in checks.items():
    conteudo = arquivo.read_text(encoding="utf-8")
    for marca in marcas:
        if marca not in conteudo:
            raise SystemExit(f"Validacao 3916 falhou em {arquivo.name}: {marca}")

cadastro = ROOT / "cadastro.html"
if cadastro.exists() and "comercial-campos-v3916.js?v=3916" not in cadastro.read_text(encoding="utf-8"):
    raise SystemExit("Regra Comercial 3916 nao entrou em cadastro.html")

estoque = ROOT / "estoque.html"
if estoque.exists() and "nota-zoom-pan-v3916.js?v=3916" not in estoque.read_text(encoding="utf-8"):
    raise SystemExit("Zoom 3916 nao entrou em estoque.html")

print("Correcoes 3916 aplicadas: modo Comercial sem Fazenda/Talhao/Secagem visiveis e nota com zoom/arraste.")
