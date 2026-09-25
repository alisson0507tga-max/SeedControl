from argparse import ArgumentParser
from pathlib import Path
import re
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = ArgumentParser(description="Torna a data do lote digitável e remove o atalho de arquivos do menu inicial.")
parser.add_argument("--source", type=Path, default=ROOT / "SeedControl_v3.8.4_uso_imediato_source.zip", help="ZIP fonte de entrada")
parser.add_argument("--output", type=Path, default=ROOT / "SeedControl_v3.8.6_data_digitavel_source.zip", help="ZIP fonte de saída")
args = parser.parse_args()
SOURCE = args.source if args.source.is_absolute() else ROOT / args.source
OUTPUT = args.output if args.output.is_absolute() else ROOT / args.output

if not SOURCE.exists():
    raise SystemExit(f"Fonte-base não encontrada: {SOURCE}")

with tempfile.TemporaryDirectory(prefix="seedcontrol-datefix-") as temp_dir:
    work = Path(temp_dir)
    with zipfile.ZipFile(SOURCE) as archive:
        archive.extractall(work)
    projects = list(work.glob("*/editar.html"))
    if len(projects) != 1:
        raise SystemExit("Não foi possível identificar unicamente a pasta do aplicativo no ZIP.")
    project = projects[0].parent

    html_path = project / "editar.html"
    html = html_path.read_text(encoding="utf-8")
    metadata = '''<div style="margin-bottom:20px;padding:12px;background:rgba(0,0,0,0.08);border-radius:10px;">
<p style="margin:4px 0;"><strong>📅 Data:</strong>
<input id="dataCadastro" type="text" inputmode="numeric" maxlength="10" placeholder="DD/MM/AAAA" autocomplete="off" aria-label="Data de cadastro, formato dia mês ano" style="width:100%;box-sizing:border-box;padding:12px 14px;border-radius:10px;background:#071720;color:#f4f8fa;border:1px solid rgba(255,255,255,.18);font:inherit">
</p>
<p style="margin:4px 0;"><strong>🆔 ID:</strong> <span id="idCadastro"></span></p>
</div>
'''
    if 'id="dataCadastro"' not in html:
        marker = '<div class="card">'
        if marker not in html:
            raise SystemExit("Não foi encontrado o card da tela Editar Lote.")
        html = html.replace(marker, marker + "\n" + metadata, 1)
    else:
        html = re.sub(r'<input\b(?=[^>]*\bid="dataCadastro")[^>]*>', metadata.splitlines()[2].strip(), html, count=1)
    html = html.replace('<script src="editar.js"></script>', '<script src="editar.js?v=3860"></script>')
    html_path.write_text(html, encoding="utf-8")

    edit_path = project / "editar.js"
    edit_js = edit_path.read_text(encoding="utf-8")
    init = '''    const campoDataCadastro = document.getElementById("dataCadastro");
    const textoIdCadastro = document.getElementById("idCadastro");
    function formatarDataCadastro(valor, idLote) {
        const texto = String(valor || "").trim();
        let partes = texto.match(/^(\\d{4})-(\\d{2})-(\\d{2})/);
        if (partes) return partes[3] + "/" + partes[2] + "/" + partes[1];
        partes = texto.match(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})$/);
        if (partes) return partes[1] + "/" + partes[2] + "/" + partes[3];
        const idComoData = Number(idLote);
        const data = Number.isFinite(idComoData) && idComoData > Date.UTC(2020, 0, 1) ? new Date(idComoData) : new Date();
        return String(data.getDate()).padStart(2, "0") + "/" + String(data.getMonth() + 1).padStart(2, "0") + "/" + data.getFullYear();
    }
    function normalizarDataCadastro(valor) {
        const texto = String(valor || "").trim();
        let partes = texto.match(/^(\\d{2})\\/(\\d{2})\\/(\\d{4})$/);
        let dia, mes, ano;
        if (partes) { dia = Number(partes[1]); mes = Number(partes[2]); ano = Number(partes[3]); }
        else {
            partes = texto.match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
            if (!partes) return "";
            ano = Number(partes[1]); mes = Number(partes[2]); dia = Number(partes[3]);
        }
        const valida = new Date(Date.UTC(ano, mes - 1, dia));
        if (valida.getUTCFullYear() !== ano || valida.getUTCMonth() !== mes - 1 || valida.getUTCDate() !== dia) return "";
        return String(ano).padStart(4, "0") + "-" + String(mes).padStart(2, "0") + "-" + String(dia).padStart(2, "0");
    }
    if (campoDataCadastro) {
        campoDataCadastro.value = formatarDataCadastro(registro.dataCadastro, registro.id);
        campoDataCadastro.addEventListener("input", function () {
            const digitos = this.value.replace(/\\D/g, "").slice(0, 8);
            this.value = digitos.length > 4 ? digitos.slice(0, 2) + "/" + digitos.slice(2, 4) + "/" + digitos.slice(4) : digitos.length > 2 ? digitos.slice(0, 2) + "/" + digitos.slice(2) : digitos;
        });
    }
    if (textoIdCadastro) textoIdCadastro.textContent = String(registro.id ?? "");
'''
    block_pattern = re.compile(r'    const campoDataCadastro = document\.getElementById\("dataCadastro"\);.*?if \(textoIdCadastro\) textoIdCadastro\.textContent = String\(registro\.id \?\? ""\);\n', re.S)
    if block_pattern.search(edit_js):
        edit_js = block_pattern.sub(lambda _: init, edit_js, count=1)
    else:
        anchor = '    const btnSalvar =\n        document.getElementById("salvar");'
        if anchor not in edit_js:
            raise SystemExit("Não foi encontrada a declaração do botão Salvar no editar.js.")
        edit_js = edit_js.replace(anchor, anchor + "\n" + init, 1)

    handler_anchor = '                const novoLote = {\n'
    handler_prep = '''                const dataCadastroEditada = normalizarDataCadastro(campoDataCadastro ? campoDataCadastro.value : "");
                if (!dataCadastroEditada) {
                    alert("Informe uma data válida no formato DD/MM/AAAA.");
                    if (campoDataCadastro) campoDataCadastro.focus();
                    return;
                }
'''
    edit_js = edit_js.replace('dataCadastro: campoDataCadastro ? campoDataCadastro.value : (registro.dataCadastro || ""),', 'dataCadastro: dataCadastroEditada,')
    if 'const dataCadastroEditada = normalizarDataCadastro(' not in edit_js:
        if handler_anchor not in edit_js:
            raise SystemExit("Não foi encontrado o objeto novoLote no editar.js.")
        edit_js = edit_js.replace(handler_anchor, handler_prep + handler_anchor, 1)
    if 'dataCadastro: dataCadastroEditada,' not in edit_js:
        if handler_anchor not in edit_js:
            raise SystemExit("Não foi encontrado o objeto novoLote para persistir a data.")
        edit_js = edit_js.replace(handler_anchor, handler_anchor + '                    dataCadastro: dataCadastroEditada,\n', 1)
    edit_path.write_text(edit_js, encoding="utf-8")

    db_path = project / "database.js"
    db = db_path.read_text(encoding="utf-8")
    db_pattern = re.compile(r'(const atualizadoBase\s*=\s*\{\s*\.\.\.estoque\[indice\],\s*id:\s*estoque\[indice\]\.id,)')
    if 'String(novoLote.dataCadastro || estoque[indice].dataCadastro || "").trim()' not in db:
        db, inseridos = db_pattern.subn(r'\1\n        dataCadastro:\n            String(novoLote.dataCadastro || estoque[indice].dataCadastro || "").trim(),', db, count=1)
        if inseridos == 0:
            raise SystemExit("Não foi encontrada a montagem do lote atualizado no database.js.")
    db_path.write_text(db, encoding="utf-8")

    index_path = project / "index.html"
    index = index_path.read_text(encoding="utf-8")
    pattern = re.compile(r'\s*<p>\s*<button\s+type="button"\s+onclick="window\.location\.href=\'arquivos\.html\'">📁\s*PDFs, Excel e Planilhas</button>\s*</p>\s*', re.I)
    index, removidos = pattern.subn("\n", index, count=1)
    if removidos == 0 and 'PDFs, Excel e Planilhas</button>' in index:
        raise SystemExit("O atalho 'PDFs, Excel e Planilhas' não foi encontrado uma única vez no menu inicial.")
    index_path.write_text(index, encoding="utf-8")

    sw_path = project / "service-worker.js"
    if sw_path.exists():
        sw = sw_path.read_text(encoding="utf-8")
        sw = sw.replace('seedcontrol-v3.8-pwa-3924', 'seedcontrol-v3.8-pwa-3925')
        sw_path.write_text(sw, encoding="utf-8")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(work.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(work))

print(f"Fonte editada criada: {OUTPUT}")
print("Alterações: campo de data digitável DD/MM/AAAA com teclado numérico e validação; data persistida; atalho removido do menu inicial; cache da interface invalidado.")
