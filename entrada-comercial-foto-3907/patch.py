from pathlib import Path
import shutil

SRC = Path("entrada-comercial-foto-3907")
DST = Path("native/www")
ENTRADA = DST / "entrada-comercial.html"
PLANILHA = DST / "planilha.html"

ARQUIVOS = [
    "entrada-comercial-foto-v3907.js",
    "planilha-mobile-v3907.js",
]

for nome in ARQUIVOS:
    origem = SRC / nome
    if not origem.exists():
        raise SystemExit(f"Arquivo fonte ausente: {origem}")

for pagina in (ENTRADA, PLANILHA):
    if not pagina.exists():
        raise SystemExit(f"Página ausente: {pagina}")

for nome in ARQUIVOS:
    shutil.copy2(SRC / nome, DST / nome)

entrada = ENTRADA.read_text(encoding="utf-8")
script_foto = '<script src="entrada-comercial-foto-v3907.js?v=3907"></script>'
if "entrada-comercial-foto-v3907.js" not in entrada:
    if "</body>" in entrada:
        entrada = entrada.replace("</body>", f"    {script_foto}\n</body>", 1)
    else:
        entrada += "\n" + script_foto + "\n"
    ENTRADA.write_text(entrada, encoding="utf-8")

planilha = PLANILHA.read_text(encoding="utf-8")
script_mobile = '<script src="planilha-mobile-v3907.js?v=3907"></script>'
if "planilha-mobile-v3907.js" not in planilha:
    if "</body>" in planilha:
        planilha = planilha.replace("</body>", f"    {script_mobile}\n</body>", 1)
    else:
        planilha += "\n" + script_mobile + "\n"
    PLANILHA.write_text(planilha, encoding="utf-8")

validacoes = [
    (ENTRADA, "entrada-comercial-foto-v3907.js?v=3907"),
    (PLANILHA, "planilha-mobile-v3907.js?v=3907"),
    (DST / "entrada-comercial-foto-v3907.js", "seedcontrol-entrada-comercial-foto-v3907"),
    (DST / "entrada-comercial-foto-v3907.js", "seedcontrol_entrada_comercial_notas_2026"),
    (DST / "entrada-comercial-foto-v3907.js", "notaEntradaFoto"),
    (DST / "entrada-comercial-foto-v3907.js", "📷 Tirar foto"),
    (DST / "entrada-comercial-foto-v3907.js", "🖼️ Galeria"),
    (DST / "entrada-comercial-foto-v3907.js", "📄 Ver nota"),
    (DST / "planilha-mobile-v3907.js", "seedcontrol-planilha-mobile-v3907"),
    (DST / "planilha-mobile-v3907.js", "seed-planilha-scroll-v3907"),
    (DST / "planilha-mobile-v3907.js", "seedcontrol-entrada-comercial-atalho-v3904"),
]

for arquivo, trecho in validacoes:
    if not arquivo.exists():
        raise SystemExit(f"Arquivo não encontrado na validação: {arquivo}")
    if trecho not in arquivo.read_text(encoding="utf-8"):
        raise SystemExit(f"Validação 3907 falhou em {arquivo.name}: {trecho}")

print("3907 aplicada: foto na Entrada Comercial sincronizada com Estoque e Planilha mobile corrigida em runtime.")
