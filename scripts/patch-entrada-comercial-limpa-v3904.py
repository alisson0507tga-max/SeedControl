from pathlib import Path
import shutil
import re

SRC = Path("entrada-comercial-3904")
DST = Path("native/www")
CADASTRO = DST / "cadastro.html"
PLANILHA = DST / "planilha.html"
SW = DST / "service-worker.js"

arquivos = [
    "entrada-comercial.html",
    "entrada-comercial-v3904.css",
    "entrada-comercial-core-v3904.js",
    "entrada-comercial-v3904.js",
]

for nome in arquivos:
    origem = SRC / nome
    if not origem.exists():
        raise SystemExit(f"Arquivo fonte ausente: {origem}")

for obrigatorio in (CADASTRO, PLANILHA):
    if not obrigatorio.exists():
        raise SystemExit(f"Arquivo do app ausente: {obrigatorio}")

for nome in arquivos:
    shutil.copy2(SRC / nome, DST / nome)

cadastro = CADASTRO.read_text(encoding="utf-8")
marcador_cadastro = "registrarEntradaComercial3904"
script_core = f'<!-- {marcador_cadastro} -->\n<script src="entrada-comercial-core-v3904.js?v=3904"></script>'
if "entrada-comercial-core-v3904.js" not in cadastro:
    if "</body>" in cadastro:
        cadastro = cadastro.replace("</body>", f"    {script_core}\n</body>", 1)
    else:
        cadastro += "\n" + script_core + "\n"
    CADASTRO.write_text(cadastro, encoding="utf-8")

planilha = PLANILHA.read_text(encoding="utf-8")
marcador = "seedcontrol-entrada-comercial-atalho-v3904"
if marcador not in planilha:
    bloco = '''
<section class="card" id="seedcontrol-entrada-comercial-atalho-v3904" style="border:1px solid rgba(74,222,128,.28);background:linear-gradient(145deg,rgba(9,48,37,.78),rgba(7,27,35,.92));margin:14px 0;padding:16px;border-radius:16px">
  <h2 style="margin:0 0 7px">📥 Entrada Comercial de Sementes</h2>
  <p style="color:#aebdc2;margin:0 0 12px;line-height:1.45">Controle das sementes recebidas de fora, com estimativa de Bags baseada no PMS.</p>
  <button type="button" onclick="window.location.href='entrada-comercial.html?v=3904'" style="width:100%;min-height:48px;border-radius:12px;border:1px solid rgba(74,222,128,.35);background:#0d6435;color:#fff;font-weight:700">Abrir Entrada Comercial 2026</button>
</section>
'''
    if "</main>" in planilha:
        planilha = planilha.replace("</main>", bloco + "\n</main>", 1)
    elif "</body>" in planilha:
        planilha = planilha.replace("</body>", bloco + "\n</body>", 1)
    else:
        planilha += bloco
    PLANILHA.write_text(planilha, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3904", sw, count=1)
    SW.write_text(sw, encoding="utf-8")

for nome in arquivos:
    if not (DST / nome).exists():
        raise SystemExit(f"Falha ao copiar: {nome}")

cad_final = CADASTRO.read_text(encoding="utf-8")
plan_final = PLANILHA.read_text(encoding="utf-8")
if "entrada-comercial-core-v3904.js" not in cad_final:
    raise SystemExit("Core 3904 não entrou no cadastro.html")
if marcador_cadastro not in cad_final:
    raise SystemExit("Marcador de integração comercial 3904 não entrou no cadastro.html")
if marcador not in plan_final or "entrada-comercial.html?v=3904" not in plan_final:
    raise SystemExit("Atalho 3904 não entrou em planilha.html")

print("Entrada Comercial 3904 aplicada de forma isolada sobre a base verde 3902.")
