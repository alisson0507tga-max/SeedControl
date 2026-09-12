from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZIP = ROOT / "SeedControl_v3.8_revisado_apk (2).zip"
WORK = ROOT / "build_historico_editavel"
OUTPUT_ZIP = ROOT / "SeedControl_v3.8_historico_saida_editavel.zip"

if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir()

with zipfile.ZipFile(SOURCE_ZIP) as archive:
    archive.extractall(WORK)

project_dirs = list(WORK.glob("*/"))
if len(project_dirs) != 1:
    raise SystemExit(f"Projeto inesperado no ZIP: {project_dirs}")
project = project_dirs[0]

keyboard_policy = r'''/* SeedControl: teclado nativo alfanumerico em todos os campos editaveis. */
(function aplicarTecladoNativoAlfanumerico() {
    function ajustarCampos(root) {
        (root || document).querySelectorAll("input, textarea").forEach(function (campo) {
            if (campo.tagName === "INPUT" && campo.type === "file") return;
            if (campo.tagName === "INPUT" && ["button", "submit", "reset", "checkbox", "radio", "range", "color"].includes(campo.type)) return;
            if (campo.tagName === "INPUT") campo.type = "text";
            campo.setAttribute("inputmode", "text");
            campo.removeAttribute("pattern");
        });
    }
    ajustarCampos(document);
    document.addEventListener("DOMContentLoaded", function () { ajustarCampos(document); });
    new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1) ajustarCampos(node);
            });
        });
    }).observe(document.documentElement, { childList: true, subtree: true });
})();
'''

for html_path in sorted(project.glob("*.html")):
    text = html_path.read_text(encoding="utf-8")
    if "aplicarTecladoNativoAlfanumerico" not in text:
        marker = "</body>"
        if marker not in text:
            raise SystemExit(f"Marcador </body> nao encontrado em {html_path.name}")
        text = text.replace(marker, f"<script>{keyboard_policy}</script>\n\n{marker}", 1)
        html_path.write_text(text, encoding="utf-8")

# Store the originating lot id in new movement records and expose a safe updater.
database = project / "database.js"
db_text = database.read_text(encoding="utf-8")
movement_marker = '''        lote:\n            lote.lote,\n\n        quantidade:\n            qtd,'''
movement_replacement = '''        lote:\n            lote.lote,\n\n        loteId:\n            lote.id,\n\n        quantidade:\n            qtd,'''
if movement_marker not in db_text:
    raise SystemExit("Nao foi encontrado o registro de movimentacao em database.js")
db_text = db_text.replace(movement_marker, movement_replacement, 1)

history_helper = r'''

// ======================================
// EDITAR REGISTRO DO HISTÓRICO
// ======================================

function atualizarRegistroHistorico(indice, atualizacoes = {}, opcoes = {}) {
    const historico = carregarHistorico();
    const posicao = Number(indice);
    if (!Number.isInteger(posicao) || posicao < 0 || posicao >= historico.length) {
        return { ok: false, mensagem: "Registro do histórico não encontrado." };
    }

    const anterior = historico[posicao];
    const tipo = String(anterior.tipo || "").toLowerCase();
    const ehMovimentacao = tipo === "entrada" || tipo === "saida";
    const quantidadeAnterior = Number(anterior.quantidade) || 0;
    const valorRecebido = atualizacoes.quantidade;
    const quantidadeNova = valorRecebido === undefined
        ? quantidadeAnterior
        : Number(String(valorRecebido).replace(",", "."));

    if (ehMovimentacao && (!Number.isFinite(quantidadeNova) || quantidadeNova <= 0)) {
        return { ok: false, mensagem: "Informe uma quantidade válida maior que zero." };
    }

    const estoque = carregarEstoque();
    let lote = null;
    if (ehMovimentacao) {
        lote = estoque.find(item => anterior.loteId != null && Number(item.id) === Number(anterior.loteId));
        if (!lote) {
            lote = estoque.find(item => String(item.cultivar || "").trim() === String(anterior.cultivar || "").trim() && String(item.lote || "").trim() === String(anterior.lote || "").trim());
        }
        if (!lote) return { ok: false, mensagem: "O lote dessa movimentação não está mais disponível." };

        const diferenca = quantidadeNova - quantidadeAnterior;
        const variacaoEstoque = tipo === "entrada" ? diferenca : -diferenca;
        const novoSaldo = (Number(lote.bags) || 0) + variacaoEstoque;
        if (novoSaldo < 0) return { ok: false, mensagem: "A alteração deixaria o estoque negativo." };
        lote.bags = novoSaldo;
        salvarEstoque(estoque, { silencioso: true });
    }

    historico[posicao] = {
        ...anterior,
        quantidade: ehMovimentacao ? quantidadeNova : (valorRecebido === undefined ? anterior.quantidade : valorRecebido),
        observacao: atualizacoes.observacao === undefined ? anterior.observacao : String(atualizacoes.observacao).trim(),
        data: atualizacoes.data === undefined ? anterior.data : String(atualizacoes.data).trim()
    };
    salvarHistorico(historico, { silencioso: true });
    if (!opcoes.silencioso) notificarMudanca(ehMovimentacao ? "estoque" : "historico");
    return { ok: true, mensagem: "Registro atualizado com sucesso!", registro: historico[posicao] };
}
'''
config_marker = "// ======================================\n// CONFIGURAÇÕES"
if "function atualizarRegistroHistorico" not in db_text:
    if config_marker not in db_text:
        raise SystemExit("Marcador de configuracoes nao encontrado em database.js")
    db_text = db_text.replace(config_marker, history_helper + "\n\n" + config_marker, 1)
database.write_text(db_text, encoding="utf-8")

historico_js = r'''// ===============================
// SeedControl - Histórico editável
// ===============================

let ouvintesHistoricoRegistrados = false;
const lista = document.getElementById("lista");

function escaparHistorico(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, function (caractere) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[caractere];
    });
}

function nomeTipoHistorico(tipo) {
    return ({ entrada: "Entrada", saida: "Saída", edicao: "Edição", exclusao: "Exclusão", cadastro: "Cadastro" })[tipo] || tipo || "Registro";
}

function iconeTipoHistorico(tipo) {
    return ({ entrada: "➕", saida: "➖", edicao: "✏️", exclusao: "🗑️", cadastro: "🌱" })[tipo] || "📋";
}

function alternarEdicaoHistorico(indice, editar) {
    const form = document.getElementById("historico-edicao-" + indice);
    const resumo = document.getElementById("historico-resumo-" + indice);
    if (form) form.hidden = !editar;
    if (resumo) resumo.hidden = editar;
}

function salvarEdicaoHistorico(indice) {
    const form = document.getElementById("historico-edicao-" + indice);
    if (!form) return;
    const resultado = atualizarRegistroHistorico(indice, {
        quantidade: form.elements.quantidade ? form.elements.quantidade.value : undefined,
        observacao: form.elements.observacao ? form.elements.observacao.value : undefined,
        data: form.elements.data ? form.elements.data.value : undefined
    });
    if (!resultado.ok) { alert(resultado.mensagem); return; }
    renderizarHistorico();
}

function renderizarHistorico() {
    if (!lista) return;
    const historico = carregarHistorico();
    if (historico.length === 0) {
        lista.innerHTML = '<div class="card"><h2>📋 Nenhuma movimentação encontrada</h2><p>Faça uma entrada, saída, edição ou exclusão para começar o histórico.</p></div>';
        return;
    }
    lista.innerHTML = historico.map(function (item, indice) {
        const tipo = String(item.tipo || "").toLowerCase();
        const permiteQuantidade = tipo === "entrada" || tipo === "saida";
        return '<div class="card historico-item">' +
            '<div id="historico-resumo-' + indice + '">' +
            '<h2>' + iconeTipoHistorico(tipo) + ' ' + escaparHistorico(nomeTipoHistorico(tipo)) + '</h2>' +
            '<p><strong>📅 Data:</strong> ' + escaparHistorico(item.data || "-") + '</p>' +
            '<p><strong>🌱 Cultivar:</strong> ' + escaparHistorico(item.cultivar || "-") + '</p>' +
            '<p><strong>📋 Lote:</strong> ' + escaparHistorico(item.lote || "-") + '</p>' +
            '<p><strong>📦 Quantidade:</strong> ' + escaparHistorico(item.quantidade ?? 0) + ' Bags</p>' +
            '<p><strong>📝 Observação:</strong> ' + escaparHistorico(item.observacao || "Sem observação") + '</p>' +
            '<button type="button" onclick="alternarEdicaoHistorico(' + indice + ', true)">✏️ Editar registro</button>' +
            '</div>' +
            '<form id="historico-edicao-' + indice + '" hidden onsubmit="event.preventDefault(); salvarEdicaoHistorico(' + indice + ')">' +
            '<h3>Editar ' + escaparHistorico(nomeTipoHistorico(tipo)) + '</h3>' +
            '<label>Data<input name="data" type="text" value="' + escaparHistorico(item.data || "") + '"></label>' +
            (permiteQuantidade ? '<label>Quantidade de Bags<input name="quantidade" type="text" inputmode="text" value="' + escaparHistorico(item.quantidade ?? "") + '"></label>' : '') +
            '<label>Observação<textarea name="observacao">' + escaparHistorico(item.observacao || "") + '</textarea></label>' +
            '<button type="submit">💾 Salvar edição</button> <button type="button" onclick="alternarEdicaoHistorico(' + indice + ', false)">Cancelar</button>' +
            '</form>' +
            '</div>';
    }).join("");
}

function registrarOuvintesHistorico() {
    if (ouvintesHistoricoRegistrados) return;
    ouvintesHistoricoRegistrados = true;
    window.addEventListener("seedcontrol:atualizado", renderizarHistorico);
    window.addEventListener("storage", renderizarHistorico);
    window.addEventListener("focus", renderizarHistorico);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) renderizarHistorico(); });
}

function iniciarHistorico() { renderizarHistorico(); registrarOuvintesHistorico(); }
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciarHistorico);
else iniciarHistorico();
'''
(project / "historico.js").write_text(historico_js, encoding="utf-8")

if OUTPUT_ZIP.exists():
    OUTPUT_ZIP.unlink()
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(WORK.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(WORK))

print(f"Telas atualizadas: {len(list(project.glob('*.html')))}")
print(f"ZIP gerado: {OUTPUT_ZIP}")
print("Histórico: edição de data, observação e quantidade; estoque reconciliado para entradas e saídas.")
print("Teclado: inputmode=text/type=text em todos os campos editáveis, inclusive campos dinâmicos.")
