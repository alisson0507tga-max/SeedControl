from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "SeedControl_v3.8.4_uso_imediato_source.zip"
WORK = ROOT / "build_v3.8.4_relatorios_historico"
OUTPUT = ROOT / "SeedControl_v3.8.4_relatorios_historico_editavel_source.zip"

if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir()
with zipfile.ZipFile(SOURCE) as archive:
    archive.extractall(WORK)
project = next(WORK.glob("*/"))

storage_js = r'''// SeedControl v3.8.4 - armazenamento interno sem permissao externa
(function () {
    "use strict";
    const META_KEY = "seedcontrol:arquivos-relatorios:v384";
    function metas() { try { const v = JSON.parse(localStorage.getItem(META_KEY) || "[]"); return Array.isArray(v) ? v : []; } catch (_) { return []; } }
    function guardarMetas(lista) { localStorage.setItem(META_KEY, JSON.stringify(lista.slice(0, 100))); }
    function registrar(opcoes, resultado) {
        const path = String(opcoes.path || "");
        const nome = path.split("/").pop();
        if (!nome || !/\.(pdf|xlsx?|csv)$/i.test(nome)) return;
        const lista = metas().filter(x => x.path !== opcoes.path);
        lista.unshift({ nome, path: opcoes.path, directory: opcoes.directory || "DATA", uri: resultado && resultado.uri || "", criadoEm: new Date().toISOString(), tipo: /\.pdf$/i.test(nome) ? "PDF" : "Excel/Planilha" });
        guardarMetas(lista);
    }
    window.SeedControlArquivos = {
        listar: metas,
        remover: function (path) { guardarMetas(metas().filter(x => x.path !== path)); },
        registrar
    };
    function instalar() {
        const fs = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Filesystem;
        if (!fs || fs.__seedcontrolStorageV384) return;
        const original = fs.writeFile.bind(fs);
        fs.writeFile = async function (opcoes) {
            const entrada = { ...(opcoes || {}) };
            const nome = String(entrada.path || "").split("/").pop();
            if (String(entrada.directory || "").toUpperCase() === "DOCUMENTS") {
                // DATA não exige MANAGE_EXTERNAL_STORAGE e funciona no Android moderno.
                entrada.path = "SeedControl/Arquivos/" + nome;
                entrada.directory = "DATA";
                entrada.recursive = true;
            }
            const resultado = await original(entrada);
            registrar(entrada, resultado);
            return resultado;
        };
        fs.__seedcontrolStorageV384 = true;
    }
    instalar();
    setTimeout(instalar, 0);
})();
'''
(project / "arquivo-storage-v384.js").write_text(storage_js, encoding="utf-8")

central_html = '''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arquivos - SeedControl</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="app-v384.css"><script src="arquivo-storage-v384.js?v=3841"></script></head>
<body class="seed-v384-page"><header class="topo"><h1>📁 Arquivos</h1><p>PDFs, Excel e planilhas gerados no aplicativo</p></header><main class="container"><div class="card"><p>Os arquivos ficam guardados dentro do aplicativo, sem depender da permissão de armazenamento externo. Use <strong>Visualizar/Compartilhar</strong> para abrir o PDF ou Excel em um aplicativo compatível.</p></div><div id="listaArquivos"></div><button type="button" onclick="window.location.href='historico.html'">← Voltar ao Histórico</button></main><script src="arquivos.js?v=3841"></script></body></html>
'''
(project / "arquivos.html").write_text(central_html, encoding="utf-8")

arquivos_js = r'''(function () {
    "use strict";
    const lista = document.getElementById("listaArquivos");
    function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
    function data(v) { try { return new Date(v).toLocaleString("pt-BR"); } catch (_) { return v || ""; } }
    async function abrir(item) {
        const fs = window.Capacitor?.Plugins?.Filesystem, share = window.Capacitor?.Plugins?.Share;
        if (!fs || !share) { alert("Visualização nativa indisponível neste dispositivo."); return; }
        try { const r = await fs.getUri({ directory: item.directory || "DATA", path: item.path }); await share.share({ title: item.nome, text: "Arquivo gerado pelo SeedControl", url: r.uri, dialogTitle: "Abrir ou compartilhar arquivo" }); }
        catch (e) { alert("Não foi possível abrir o arquivo. " + (e.message || e)); }
    }
    function render() {
        const itens = window.SeedControlArquivos?.listar?.() || [];
        if (!itens.length) { lista.innerHTML = '<div class="card"><h2>📂 Nenhum arquivo gerado ainda</h2><p>Gere um PDF ou Excel em Relatório de Saídas ou Relatórios.</p></div>'; return; }
        lista.innerHTML = itens.map((item, i) => '<div class="card"><h2>' + (item.tipo === "PDF" ? "📕" : "📗") + ' ' + esc(item.tipo) + '</h2><p><strong>Arquivo:</strong> ' + esc(item.nome) + '</p><p><strong>Gerado em:</strong> ' + esc(data(item.criadoEm)) + '</p><button type="button" data-abrir="' + i + '">👁️ Visualizar / Compartilhar</button> <button type="button" data-remover="' + i + '">🗑️ Remover da lista</button></div>').join("");
        lista.querySelectorAll("[data-abrir]").forEach(b => b.onclick = () => abrir(itens[Number(b.dataset.abrir)]));
        lista.querySelectorAll("[data-remover]").forEach(b => b.onclick = () => { window.SeedControlArquivos.remover(itens[Number(b.dataset.remover)].path); render(); });
    }
    render();
})();
'''
(project / "arquivos.js").write_text(arquivos_js, encoding="utf-8")

# Replace the historical screen with editable cards while preserving destination data.
historico_js = r'''// SeedControl v3.8.4 - Histórico editável
let ouvintesHistoricoRegistrados = false;
const lista = document.getElementById("lista");
function escHist(v) { return String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function tipoNome(t) { return ({entrada:"Entrada",saida:"Saída",edicao:"Edição",exclusao:"Exclusão",cadastro:"Cadastro"}[t] || t || "Registro"); }
function ico(t) { return ({entrada:"➕",saida:"➖",edicao:"✏️",exclusao:"🗑️",cadastro:"🌱"}[t] || "📋"); }
function alternarEdicaoHistorico(i, editar) { const f=document.getElementById("hist-edit-"+i), r=document.getElementById("hist-resumo-"+i); if(f)f.hidden=!editar; if(r)r.hidden=editar; }
function salvarEdicaoHistorico(i) { const f=document.getElementById("hist-edit-"+i); const r=atualizarRegistroHistorico(i,{quantidade:f.elements.quantidade?.value,observacao:f.elements.observacao?.value,data:f.elements.data?.value,destino:f.elements.destino?.value}); if(!r.ok){alert(r.mensagem);return;} renderizarHistorico(); }
function renderizarHistorico() {
    if (!lista) return; const h=carregarHistorico();
    if (!h.length) { lista.innerHTML='<div class="card"><h2>📋 Nenhuma movimentação encontrada</h2><p>Faça uma entrada ou saída para começar o histórico.</p></div>'; return; }
    lista.innerHTML=h.map((item,i)=>{const t=String(item.tipo||"").toLowerCase(), mov=t==="entrada"||t==="saida"; return '<div class="card"><div id="hist-resumo-'+i+'"><h2>'+ico(t)+' '+escHist(tipoNome(t))+'</h2><p><strong>📅 Data:</strong> '+escHist(item.data||"-")+'</p><p><strong>🌱 Cultivar:</strong> '+escHist(item.cultivar||"-")+'</p><p><strong>📋 Lote:</strong> '+escHist(item.lote||"-")+'</p><p><strong>📦 Quantidade:</strong> '+escHist(item.quantidade??0)+' Bags</p>'+(item.destino?'<p><strong>🚚 Destino:</strong> '+escHist(item.destino)+'</p>':'')+'<p><strong>📝 Observação:</strong> '+escHist(item.observacao||"Sem observação")+'</p><button type="button" onclick="alternarEdicaoHistorico('+i+',true)">✏️ Editar card</button></div><form id="hist-edit-'+i+'" hidden onsubmit="event.preventDefault();salvarEdicaoHistorico('+i+')"><h3>Editar '+escHist(tipoNome(t))+'</h3><label>Data<input name="data" type="text" value="'+escHist(item.data||"")+'"></label>'+(mov?'<label>Quantidade de Bags<input name="quantidade" type="text" inputmode="text" value="'+escHist(item.quantidade??"")+'"></label>':'')+(item.destino!==undefined?'<label>Destino<input name="destino" type="text" value="'+escHist(item.destino||"")+'"></label>':'')+'<label>Observação<textarea name="observacao">'+escHist(item.observacao||"")+'</textarea></label><button type="submit">💾 Salvar</button> <button type="button" onclick="alternarEdicaoHistorico('+i+',false)">Cancelar</button></form></div>';}).join("");
}
function registrarOuvintesHistorico(){if(ouvintesHistoricoRegistrados)return;ouvintesHistoricoRegistrados=true;window.addEventListener("seedcontrol:atualizado",renderizarHistorico);window.addEventListener("storage",renderizarHistorico);window.addEventListener("focus",renderizarHistorico);}
function iniciarHistorico(){renderizarHistorico();registrarOuvintesHistorico();}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",iniciarHistorico);else iniciarHistorico();
'''
(project / "historico.js").write_text(historico_js, encoding="utf-8")

# Add database updater before configuration section.
db = project / "database.js"
text = db.read_text(encoding="utf-8")
helper = r'''
// ======================================
// EDITAR REGISTRO DO HISTÓRICO
// ======================================
function atualizarRegistroHistorico(indice, atualizacoes = {}, opcoes = {}) {
    const historico = carregarHistorico(); const pos = Number(indice);
    if (!Number.isInteger(pos) || pos < 0 || pos >= historico.length) return {ok:false,mensagem:"Registro do histórico não encontrado."};
    const anterior = historico[pos], tipo = String(anterior.tipo || "").toLowerCase(), movimento = tipo === "entrada" || tipo === "saida";
    const antiga = Number(anterior.quantidade) || 0, recebida = atualizacoes.quantidade, nova = recebida === undefined ? antiga : Number(String(recebida).replace(",","."));
    if (movimento && (!Number.isFinite(nova) || nova <= 0)) return {ok:false,mensagem:"Informe uma quantidade válida maior que zero."};
    if (movimento) {
        const estoque = carregarEstoque(); let lote = estoque.find(x => anterior.loteId != null && Number(x.id) === Number(anterior.loteId));
        if (!lote) lote = estoque.find(x => String(x.cultivar||"").trim() === String(anterior.cultivar||"").trim() && String(x.lote||"").trim() === String(anterior.lote||"").trim());
        if (!lote) return {ok:false,mensagem:"O lote desta movimentação não está disponível."};
        const diferenca = nova - antiga, variacao = tipo === "entrada" ? diferenca : -diferenca, saldo = (Number(lote.bags)||0) + variacao;
        if (saldo < 0) return {ok:false,mensagem:"A alteração deixaria o estoque negativo."};
        lote.bags = saldo; salvarEstoque(estoque,{silencioso:true});
    }
    historico[pos] = {...anterior, quantidade: movimento ? nova : (recebida === undefined ? anterior.quantidade : recebida), observacao: atualizacoes.observacao === undefined ? anterior.observacao : String(atualizacoes.observacao).trim(), data: atualizacoes.data === undefined ? anterior.data : String(atualizacoes.data).trim(), destino: atualizacoes.destino === undefined ? anterior.destino : String(atualizacoes.destino).trim()};
    salvarHistorico(historico,{silencioso:true}); if (!opcoes.silencioso) notificarMudanca(movimento ? "estoque" : "historico");
    return {ok:true,mensagem:"Registro atualizado com sucesso!",registro:historico[pos]};
}
'''
if "function atualizarRegistroHistorico" not in text:
    marker = "// ======================================\n// CONFIGURAÇÕES"
    if marker not in text: raise SystemExit("Marcador de configurações não encontrado")
    text = text.replace(marker, helper + "\n" + marker, 1)
# Keep the lot identity on future movement cards to make reconciliation exact.
marker = '''        lote:\n            lote.lote,\n        quantidade:\n            qtd,'''
replacement = '''        lote:\n            lote.lote,\n        loteId:\n            lote.id,\n        quantidade:\n            qtd,'''
if marker in text and "loteId:\n            lote.id" not in text:
    text = text.replace(marker, replacement, 1)
db.write_text(text, encoding="utf-8")

# Make the current storage interceptor available before report scripts on every HTML page.
for html in sorted(project.glob("*.html")):
    t = html.read_text(encoding="utf-8")
    if "arquivo-storage-v384.js" not in t:
        t = t.replace("</head>", '<script src="arquivo-storage-v384.js?v=3841"></script>\n</head>', 1)
    html.write_text(t, encoding="utf-8")

# Add obvious entry points to the current home and history screens.
for name, label in [("index.html", "📁 PDFs, Excel e Planilhas"), ("historico.html", "📁 Ver PDFs, Excel e Planilhas")]:
    p = project / name; t = p.read_text(encoding="utf-8")
    if "arquivos.html" not in t:
        t = t.replace("</main>", '<p><button type="button" onclick="window.location.href=\'arquivos.html\'">'+label+'</button></p>\n</main>', 1) if "</main>" in t else t.replace("</body>", '<p><button type="button" onclick="window.location.href=\'arquivos.html\'">'+label+'</button></p>\n</body>', 1)
        p.write_text(t, encoding="utf-8")

if OUTPUT.exists(): OUTPUT.unlink()
with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(project.rglob("*")):
        if path.is_file(): archive.write(path, Path(project.name) / path.relative_to(project))
print(f"Fonte atualizada: {OUTPUT}")
print("Correções: armazenamento em DATA, cards editáveis, central de arquivos PDF/Excel/planilhas.")
