from pathlib import Path
import re

PATCH = Path("scripts/patch-entrada-comercial-v384.py")
if not PATCH.exists():
    raise SystemExit("patch-entrada-comercial-v384.py não encontrado")

texto = PATCH.read_text(encoding="utf-8")

novo_injetar = r'''def injetar_core(path: Path):
    if not path.exists():
        return

    texto = path.read_text(encoding="utf-8")
    if "entrada-comercial-core-v3903.js" in texto:
        return

    script = '\n<script src="entrada-comercial-core-v3903.js?v=3903"></script>\n'

    if re.search(r'</body\s*>', texto, re.I):
        texto = re.sub(r'</body\s*>', script + '</body>', texto, count=1, flags=re.I)
    else:
        texto += script

    path.write_text(texto, encoding="utf-8")

injetar_core(CADASTRO_HTML)
injetar_core(BACKUP_HTML)
'''

padrao_injetar = re.compile(
    r'def injetar_core\(path: Path\):.*?injetar_core\(BACKUP_HTML\)\n',
    re.S,
)
texto, qtd1 = padrao_injetar.subn(lambda _: novo_injetar, texto, count=1)
if qtd1 != 1:
    raise SystemExit("Não foi possível substituir injetar_core() no patch comercial")

novo_planilha = r'''planilha = PLANILHA_HTML.read_text(encoding="utf-8")
if "entrada-comercial.html?v=3903" not in planilha:
    bloco = """<div class="card entrada-comercial-atalho-v3903" style="border:1px solid rgba(74,222,128,.28);background:linear-gradient(145deg,rgba(9,48,37,.78),rgba(7,27,35,.92));margin:14px 0;padding:16px;border-radius:16px">
<h2>📥 Entrada Comercial de Sementes</h2>
<p style="color:#aebdc2">Recebimentos de sementes de fora, com estimativa comercial baseada no PMS.</p>
<button type="button" onclick="window.location.href='entrada-comercial.html?v=3903'">Abrir Entrada Comercial 2026</button>
</div>"""

    padrao_container = re.compile(
        r'<(?:div|main|section)\b[^>]*class=["\'][^"\']*\bcontainer\b[^"\']*["\'][^>]*>',
        re.I,
    )
    achou = padrao_container.search(planilha)

    if achou:
        pos = achou.end()
        planilha = planilha[:pos] + "\n" + bloco + "\n" + planilha[pos:]
    elif re.search(r'</body\s*>', planilha, re.I):
        planilha = re.sub(r'</body\s*>', bloco + "\n</body>", planilha, count=1, flags=re.I)
    else:
        planilha += "\n" + bloco + "\n"

    PLANILHA_HTML.write_text(planilha, encoding="utf-8")

'''

padrao_planilha = re.compile(
    r'planilha = PLANILHA_HTML\.read_text\(encoding="utf-8"\).*?PLANILHA_HTML\.write_text\(planilha, encoding="utf-8"\)\n\n',
    re.S,
)
texto, qtd2 = padrao_planilha.subn(lambda _: novo_planilha, texto, count=1)
if qtd2 != 1:
    raise SystemExit("Não foi possível substituir o bloco de atalho da Planilha")

compile(texto, str(PATCH), "exec")
PATCH.write_text(texto, encoding="utf-8")

print("Patch Entrada Comercial corrigido: injeções tolerantes ao HTML atual.")
