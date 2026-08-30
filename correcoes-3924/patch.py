from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3924/comercial-validacao-v3924.js")
DST = ROOT / "comercial-validacao-v3924.js"
SW = ROOT / "service-worker.js"

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not SRC.exists():
    raise SystemExit("comercial-validacao-v3924.js ausente")

shutil.copy2(SRC, DST)

alterados = []
for nome in ("cadastro.html", "editar.html"):
    html_path = ROOT / nome
    if not html_path.exists():
        continue
    html = html_path.read_text(encoding="utf-8")
    script = '<script src="comercial-validacao-v3924.js?v=3924"></script>'
    if "comercial-validacao-v3924.js" not in html:
        if "</body>" not in html:
            raise SystemExit(f"Nao foi possivel injetar 3924 em {nome}")
        html = html.replace("</body>", script + "\n</body>", 1)
        html_path.write_text(html, encoding="utf-8")
    alterados.append(nome)

if "cadastro.html" not in alterados:
    raise SystemExit("cadastro.html ausente para correcao 3924")

# Deixa claro no relatorio que os arquivos sao salvos no aparelho.
# O patch-exportacao-relatorios.py, aplicado antes deste arquivo no workflow,
# ja grava PDF e Excel em Documentos/SeedControl/Relatorios no Android.
relatorios = ROOT / "relatorios.html"
if relatorios.exists():
    html_rel = relatorios.read_text(encoding="utf-8")
    html_rel = html_rel.replace("Exportar PDF", "Salvar PDF no celular")
    html_rel = html_rel.replace("Exportar Excel", "Salvar Excel no celular")
    relatorios.write_text(html_rel, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3924", sw, count=1)
    SW.write_text(sw, encoding="utf-8")

js = DST.read_text(encoding="utf-8")
for marca in (
    "seedcontrol-comercial-validacao-v3924",
    "__SEEDCONTROL_NAO_APLICA_COMERCIAL_3924__",
    "protegerPersistencia",
    "prepararCamposTemporarios",
    "Storage.prototype.setItem",
    "seedControlEhComercial3924",
):
    if marca not in js:
        raise SystemExit(f"Correcao 3924 sem marca: {marca}")

for nome in alterados:
    html = (ROOT / nome).read_text(encoding="utf-8")
    if "comercial-validacao-v3924.js?v=3924" not in html:
        raise SystemExit(f"Referencia 3924 ausente em {nome}")

if relatorios.exists():
    html_rel = relatorios.read_text(encoding="utf-8")
    if "Salvar PDF no celular" not in html_rel or "Salvar Excel no celular" not in html_rel:
        raise SystemExit("Botoes de salvar no celular nao foram aplicados em relatorios.html")

print("Correcao 3924 aplicada: Comercial/PMS sem Fazenda, Talhao ou Secagem obrigatorios; relatorios com botoes para salvar no celular.")
