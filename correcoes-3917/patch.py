from pathlib import Path
import re

ROOT = Path("native/www")
if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")

alterados = []

for arquivo in ROOT.glob("*.js"):
    texto = arquivo.read_text(encoding="utf-8")
    original = texto

    # Somente rotinas de compressao de foto de nota usadas pelo SeedControl.
    if 'toDataURL("image/jpeg"' not in texto or "const limite = 1100" not in texto:
        continue

    texto = texto.replace("const limite = 1100;", "const limite = 2000;")
    texto = texto.replace('canvas.toDataURL("image/jpeg", 0.66)', 'canvas.toDataURL("image/jpeg", 0.86)')
    texto = texto.replace("resultado.length > 650000", "resultado.length > 1400000")
    texto = texto.replace('canvas.toDataURL("image/jpeg", 0.48)', 'canvas.toDataURL("image/jpeg", 0.74)')

    # Melhora a reamostragem ao redimensionar documentos com texto pequeno.
    marca = 'ctx.fillStyle = "#ffffff";'
    if marca in texto and 'imageSmoothingQuality = "high"' not in texto:
        texto = texto.replace(
            marca,
            'ctx.imageSmoothingEnabled = true;\n                    ctx.imageSmoothingQuality = "high";\n                    ' + marca,
            1,
        )

    if texto != original:
        arquivo.write_text(texto, encoding="utf-8")
        alterados.append(arquivo.name)

if not alterados:
    raise SystemExit("Nenhuma rotina de compressao de nota foi encontrada para atualizar")

# Validacoes: cadastro e Entrada Comercial precisam receber a qualidade nova quando existirem.
for nome in ("cadastro-v384.js", "entrada-comercial-foto-v3907.js"):
    arq = ROOT / nome
    if not arq.exists():
        continue
    conteudo = arq.read_text(encoding="utf-8")
    for marca in (
        "const limite = 2000",
        'toDataURL("image/jpeg", 0.86)',
        "resultado.length > 1400000",
        'toDataURL("image/jpeg", 0.74)',
    ):
        if marca not in conteudo:
            raise SystemExit(f"Qualidade 3917 nao entrou em {nome}: {marca}")

# Cache novo para garantir que o codigo atualizado seja carregado.
sw = ROOT / "service-worker.js"
if sw.exists():
    s = sw.read_text(encoding="utf-8")
    s = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3917", s, count=1)
    sw.write_text(s, encoding="utf-8")

print("Qualidade das notas 3917 aplicada em: " + ", ".join(alterados))
