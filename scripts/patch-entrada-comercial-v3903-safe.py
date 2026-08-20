from pathlib import Path
import re

ROOT = Path("native/www")
SOURCE = Path("scripts/patch-entrada-comercial-v384.py")
PLANILHA_HTML = ROOT / "planilha.html"
CADASTRO_HTML = ROOT / "cadastro.html"
BACKUP_HTML = ROOT / "backup.html"
SW = ROOT / "service-worker.js"

for arquivo in (SOURCE, PLANILHA_HTML, CADASTRO_HTML):
    if not arquivo.exists():
        raise SystemExit(f"Arquivo obrigatório não encontrado: {arquivo}")

fonte = SOURCE.read_text(encoding="utf-8")

def extrair_bloco(nome: str) -> str:
    marcador = f"{nome} = r'''"
    inicio = fonte.find(marcador)
    if inicio < 0:
        raise SystemExit(f"Bloco {nome} não encontrado no patch comercial")
    inicio += len(marcador)
    fim = fonte.find("'''", inicio)
    if fim < 0:
        raise SystemExit(f"Fim do bloco {nome} não encontrado")
    return fonte[inicio:fim]

CORE = extrair_bloco("CORE")
HTML = extrair_bloco("HTML")
CSS = extrair_bloco("CSS")
JS = extrair_bloco("JS")

(ROOT / "entrada-comercial-core-v3903.js").write_text(CORE, encoding="utf-8")
(ROOT / "entrada-comercial.html").write_text(HTML, encoding="utf-8")
(ROOT / "entrada-comercial-v3903.css").write_text(CSS, encoding="utf-8")
(ROOT / "entrada-comercial-v3903.js").write_text(JS, encoding="utf-8")

def inserir_antes_fechamento(texto: str, trecho: str) -> str:
    minusculo = texto.lower()
    for marcador in ("</main>", "</body>"):
        pos = minusculo.rfind(marcador)
        if pos >= 0:
            return texto[:pos] + trecho + "\n" + texto[pos:]
    return texto + "\n" + trecho + "\n"

def injetar_core(path: Path):
    if not path.exists():
        return
    texto = path.read_text(encoding="utf-8")
    if "entrada-comercial-core-v3903.js" in texto:
        return
    script = '<script src="entrada-comercial-core-v3903.js?v=3903"></script>'
    texto = inserir_antes_fechamento(texto, script)
    path.write_text(texto, encoding="utf-8")

injetar_core(CADASTRO_HTML)
injetar_core(BACKUP_HTML)

planilha = PLANILHA_HTML.read_text(encoding="utf-8")
if "entrada-comercial.html?v=3903" not in planilha:
    bloco = '''<div class="card entrada-comercial-atalho-v3903" style="border:1px solid rgba(74,222,128,.28);background:linear-gradient(145deg,rgba(9,48,37,.78),rgba(7,27,35,.92));margin:14px 0;padding:16px;border-radius:16px">
<h2>📥 Entrada Comercial de Sementes</h2>
<p style="color:#aebdc2">Recebimentos de sementes de fora, com estimativa comercial baseada no PMS.</p>
<button type="button" onclick="window.location.href='entrada-comercial.html?v=3903'">Abrir Entrada Comercial 2026</button>
</div>'''
    planilha = inserir_antes_fechamento(planilha, bloco)
    PLANILHA_HTML.write_text(planilha, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3903", sw, count=1)
    SW.write_text(sw, encoding="utf-8")

validacoes = {
    ROOT / "entrada-comercial-core-v3903.js": ("registrarEntradaComercial3903", "estimarBagsComerciaisPorKg"),
    ROOT / "entrada-comercial.html": ("ENTRADA DE SEMENTES SOJA", "entrada-comercial-v3903.js"),
    ROOT / "entrada-comercial-v3903.js": ("SeedControl_Entrada_Comercial_2026.xlsx", "PMS × 5"),
    CADASTRO_HTML: ("entrada-comercial-core-v3903.js",),
    PLANILHA_HTML: ("entrada-comercial.html?v=3903",),
}

for arquivo, trechos in validacoes.items():
    if not arquivo.exists():
        raise SystemExit(f"Falha: {arquivo.name} não foi criado")
    conteudo = arquivo.read_text(encoding="utf-8")
    for trecho in trechos:
        if trecho not in conteudo:
            raise SystemExit(f"Validação falhou em {arquivo.name}: {trecho}")

print("Entrada Comercial 3903 aplicada por patch seguro, sem fixer nem âncoras frágeis.")
