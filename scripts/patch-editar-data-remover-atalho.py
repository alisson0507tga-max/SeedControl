from argparse import ArgumentParser
from pathlib import Path
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = ArgumentParser(description="Torna a data do lote editável e remove o atalho de arquivos do menu inicial.")
parser.add_argument("--source", type=Path, default=ROOT / "SeedControl_v3.8.4_uso_imediato_source.zip", help="ZIP fonte de entrada")
parser.add_argument("--output", type=Path, default=ROOT / "SeedControl_v3.8.5_data_editavel_source.zip", help="ZIP fonte de saída")
args = parser.parse_args()
SOURCE = args.source if args.source.is_absolute() else ROOT / args.source
OUTPUT = args.output if args.output.is_absolute() else ROOT / args.output

if not SOURCE.exists():
    raise SystemExit(f"Fonte-base não encontrada: {SOURCE}")

with tempfile.TemporaryDirectory(prefix="seedcontrol-v385-") as temp_dir:
    work = Path(temp_dir)
    with zipfile.ZipFile(SOURCE) as archive:
        archive.extractall(work)
    projects = list(work.glob("*/editar.html"))
    if len(projects) != 1:
        raise SystemExit("Não foi possível identificar unicamente a pasta do aplicativo no ZIP.")
    project = projects[0].parent

    html_path = project / "editar.html"
    html = html_path.read_text(encoding="utf-8")
    marker = '<div class="card">'
    metadata = '''<div style="margin-bottom:20px;padding:12px;background:rgba(0,0,0,0.08);border-radius:10px;">
<p style="margin:4px 0;"><strong>📅 Data:</strong>
<input id="dataCadastro" type="date" aria-label="Data de cadastro do lote">
</p>
<p style="margin:4px 0;"><strong>🆔 ID:</strong> <span id="idCadastro"></span></p>
</div>
'''
    if 'id="dataCadastro"' not in html:
        if marker not in html:
            raise SystemExit("Não foi encontrado o card da tela Editar Lote.")
        html = html.replace(marker, marker + "\n" + metadata, 1)
    html = html.replace('<script src="editar.js"></script>', '<script src="editar.js?v=3850"></script>')
    html_path.write_text(html, encoding="utf-8")

    edit_path = project / "editar.js"
    edit_js = edit_path.read_text(encoding="utf-8")
    anchor = '    const btnSalvar =\n        document.getElementById("salvar");'
    init = '''    const campoDataCadastro = document.getElementById("dataCadastro");
    const textoIdCadastro = document.getElementById("idCadastro");
    function dataParaCampoEdicao(valor, idLote) {
        const texto = String(valor || "").trim();
        let correspondencia = texto.match(/^(\\d{4})-(\\d{2})-(\\d{2})/);
        if (correspondencia) return correspondencia[1] + "-" + correspondencia[2] + "-" + correspondencia[3];
        correspondencia = texto.match(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})$/);
        if (correspondencia) return correspondencia[3] + "-" + correspondencia[2] + "-" + correspondencia[1];
        const idComoData = Number(idLote);
        if (Number.isFinite(idComoData) && idComoData > Date.UTC(2020, 0, 1)) {
            return new Date(idComoData).toISOString().slice(0, 10);
        }
        return new Date().toISOString().slice(0, 10);
    }
    if (campoDataCadastro) campoDataCadastro.value = dataParaCampoEdicao(registro.dataCadastro, registro.id);
    if (textoIdCadastro) textoIdCadastro.textContent = String(registro.id ?? "");
'''
    if 'const campoDataCadastro = document.getElementById("dataCadastro");' not in edit_js:
        if anchor not in edit_js:
            raise SystemExit("Não foi encontrada a declaração do botão Salvar no editar.js.")
        edit_js = edit_js.replace(anchor, anchor + "\n" + init, 1)
    field_anchor = '                const novoLote = {\n'
    date_prop = '                    dataCadastro: campoDataCadastro ? campoDataCadastro.value : (registro.dataCadastro || ""),\n'
    if date_prop not in edit_js:
        if field_anchor not in edit_js:
            raise SystemExit("Não foi encontrado o objeto novoLote no editar.js.")
        edit_js = edit_js.replace(field_anchor, field_anchor + date_prop, 1)
    edit_path.write_text(edit_js, encoding="utf-8")

    db_path = project / "database.js"
    db = db_path.read_text(encoding="utf-8")
    db_pattern = re.compile(r'(const atualizadoBase\s*=\s*\{\s*\.\.\.estoque\[indice\],\s*id:\s*estoque\[indice\]\.id,)')
    db, inseridos = db_pattern.subn(r'\1\n        dataCadastro:\n            String(novoLote.dataCadastro || estoque[indice].dataCadastro || "").trim(),', db, count=1)
    if inseridos == 0 and 'String(novoLote.dataCadastro || estoque[indice].dataCadastro || "").trim()' not in db:
        raise SystemExit("Não foi encontrada a montagem do lote atualizado no database.js.")
    db_path.write_text(db, encoding="utf-8")

    index_path = project / "index.html"
    index = index_path.read_text(encoding="utf-8")
    pattern = re.compile(r'\s*<p>\s*<button\s+type="button"\s+onclick="window\.location\.href=\'arquivos\.html\'">📁\s*PDFs, Excel e Planilhas</button>\s*</p>\s*', re.I)
    index, removidos = pattern.subn("\n", index, count=1)
    if removidos == 0 and 'PDFs, Excel e Planilhas</button>' in index:
        raise SystemExit("O atalho 'PDFs, Excel e Planilhas' não foi encontrado uma única vez no menu inicial.")
    index_path.write_text(index, encoding="utf-8")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(work.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(work))

print(f"Fonte editada criada: {OUTPUT}")
print("Alterações: data de cadastro editável/persistida; atalho removido do menu inicial.")
