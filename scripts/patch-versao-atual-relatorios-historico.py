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
        lista.unshift({ nome, path: opcoes.path, directory: opcoes.directory || "DATA", uri: resultado && resultado.uri || "", externalUri: resultado && resultado.externalUri || "", criadoEm: new Date().toISOString(), tipo: /\.pdf$/i.test(nome) ? "PDF" : "Excel/Planilha" });
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
            const eraDocumentos = String(entrada.directory || "").toUpperCase() === "DOCUMENTS";
            if (eraDocumentos) {
                // DATA não exige MANAGE_EXTERNAL_STORAGE e funciona no Android moderno.
                entrada.path = "SeedControl/Arquivos/" + nome;
                entrada.directory = "DATA";
                entrada.recursive = true;
            }
            if (eraDocumentos) {
                const downloader = window.Capacitor?.Plugins?.SeedControlDownload;
                if (downloader && entrada.data && /\.(pdf|xlsx?|csv)$/i.test(nome)) {
                    try {
                        const salvo = await downloader.saveFile({ filename: nome, data: entrada.data });
                        const resultado = { uri: salvo?.uri || "", externalUri: salvo?.uri || "" };
                        if (resultado.uri) { registrar(entrada, resultado); return resultado; }
                    } catch (erro) { console.warn("Não foi possível salvar em Downloads/SeedControl; usando armazenamento interno", erro); }
                }
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

back_js = r'''// SeedControl v3.8.6 - botão Voltar retorna à tela inicial
(function () {
    "use strict";
    function inicio() { return /(^|\/)index\.html$/.test(location.pathname) || /\/$/.test(location.pathname); }
    function voltarParaInicio() {
        if (!inicio()) { location.href = "index.html"; return; }
        if (window.Capacitor?.Plugins?.App?.exitApp) window.Capacitor.Plugins.App.exitApp();
    }
    function instalar() {
        const app = window.Capacitor?.Plugins?.App;
        if (!app || window.__seedcontrolBackV386) return;
        window.__seedcontrolBackV386 = true;
        app.addListener("backButton", voltarParaInicio);
    }
    instalar();
    setTimeout(instalar, 0);
})();
'''
(project / "back-button-v386.js").write_text(back_js, encoding="utf-8")

keyboard_js = r'''// SeedControl - atributos para o teclado nativo do Android
(function () {
    "use strict";
    function preparar(campo) {
        if (!campo || campo.disabled || campo.readOnly) return;
        if (campo.tagName !== "INPUT" && campo.tagName !== "TEXTAREA") return;
        const tipo = String(campo.type || "text").toLowerCase();
        if (campo.tagName === "INPUT" && ["file", "checkbox", "radio", "button", "submit", "reset", "color", "range", "date", "datetime-local", "time"].includes(tipo)) return;
        if (campo.tagName === "INPUT" && tipo === "number") campo.type = "text";
        campo.setAttribute("autocomplete", "on");
        campo.setAttribute("aria-autocomplete", "both");
        campo.setAttribute("enterkeyhint", "next");
        if (!campo.getAttribute("name") && campo.id) campo.setAttribute("name", campo.id);
        campo.setAttribute("autocorrect", "on");
        campo.setAttribute("autocapitalize", "sentences");
        campo.setAttribute("spellcheck", "true");
    }
    function iniciar() {
        document.querySelectorAll("input, textarea").forEach(preparar);
        document.addEventListener("focusin", e => preparar(e.target), true);
        document.addEventListener("contextmenu", e => preparar(e.target), true);
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true }); else iniciar();
})();
'''
(project / "keyboard-universal-v387.js").write_text(keyboard_js, encoding="utf-8")

central_html = '''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Arquivos - SeedControl</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="app-v384.css"><script src="arquivo-storage-v384.js?v=3842"></script></head>
<body class="seed-v384-page"><header class="topo"><h1>📁 Arquivos</h1><p>PDFs, Excel e planilhas gerados no aplicativo</p></header><main class="container"><div class="card"><p>Os arquivos ficam guardados no aplicativo. Use <strong>Visualizar / Salvar no celular</strong> para abrir o PDF ou Excel e escolher o aplicativo ou a pasta de destino no Android.</p></div><div id="listaArquivos"></div><button type="button" onclick="window.location.href='historico.html'">← Voltar ao Histórico</button></main><script src="arquivos.js?v=3842"></script></body></html>
'''
(project / "arquivos.html").write_text(central_html, encoding="utf-8")

arquivos_js = r'''(function () {
    "use strict";
    const lista = document.getElementById("listaArquivos");
    function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
    function data(v) { try { return new Date(v).toLocaleString("pt-BR"); } catch (_) { return v || ""; } }
    async function abrir(item) {
        const fs = window.Capacitor?.Plugins?.Filesystem, share = window.Capacitor?.Plugins?.Share;
        if (!fs || !share) { alert("O componente de arquivos do Android não está disponível. Instale a nova versão do SeedControl."); return; }
        try { const r = item.externalUri ? { uri: item.externalUri } : await fs.getUri({ directory: item.directory || "DATA", path: item.path }); await share.share({ title: item.nome, text: "Arquivo salvo em Downloads/SeedControl.", url: r.uri, dialogTitle: "Abrir arquivo" }); }
        catch (e) { alert("Não foi possível abrir o arquivo. " + (e.message || e)); }
    }
    function render() {
        const itens = window.SeedControlArquivos?.listar?.() || [];
        if (!itens.length) { lista.innerHTML = '<div class="card"><h2>📂 Nenhum arquivo gerado ainda</h2><p>Gere um PDF ou Excel em Relatório de Saídas ou Relatórios.</p></div>'; return; }
        lista.innerHTML = itens.map((item, i) => '<div class="card"><h2>' + (item.tipo === "PDF" ? "📕" : "📗") + ' ' + esc(item.tipo) + '</h2><p><strong>Arquivo:</strong> ' + esc(item.nome) + '</p><p><strong>Gerado em:</strong> ' + esc(data(item.criadoEm)) + '</p><button type="button" data-abrir="' + i + '">👁️ Visualizar / Salvar no celular</button> <button type="button" data-remover="' + i + '">🗑️ Remover da lista</button></div>').join("");
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
function excluirRegistroHistorico(i) { const h=carregarHistorico(), item=h[Number(i)]; if(!item) return; if(!confirm("Excluir esta movimentação do histórico? O saldo do lote será revertido.")) return; const r=removerRegistroHistorico(i); if(!r.ok){alert(r.mensagem);return;} renderizarHistorico(); }
function renderizarHistorico() {
    if (!lista) return; const h=carregarHistorico();
    if (!h.length) { lista.innerHTML='<div class="card"><h2>📋 Nenhuma movimentação encontrada</h2><p>Faça uma entrada ou saída para começar o histórico.</p></div>'; return; }
    lista.innerHTML=h.map((item,i)=>{const t=String(item.tipo||"").toLowerCase(), mov=t==="entrada"||t==="saida"; return '<div class="card"><div id="hist-resumo-'+i+'"><h2>'+ico(t)+' '+escHist(tipoNome(t))+'</h2><p><strong>📅 Data:</strong> '+escHist(item.data||"-")+'</p><p><strong>🌱 Cultivar:</strong> '+escHist(item.cultivar||"-")+'</p><p><strong>📋 Lote:</strong> '+escHist(item.lote||"-")+'</p><p><strong>📦 Quantidade:</strong> '+escHist(item.quantidade??0)+' Bags</p>'+(item.destino?'<p><strong>🚚 Destino:</strong> '+escHist(item.destino)+'</p>':'')+'<p><strong>📝 Observação:</strong> '+escHist(item.observacao||"Sem observação")+'</p><button type="button" onclick="alternarEdicaoHistorico('+i+',true)">✏️ Editar card</button> <button type="button" onclick="excluirRegistroHistorico('+i+')">🗑️ Excluir movimentação</button></div><form id="hist-edit-'+i+'" hidden onsubmit="event.preventDefault();salvarEdicaoHistorico('+i+')"><h3>Editar '+escHist(tipoNome(t))+'</h3><label>Data<input name="data" type="text" value="'+escHist(item.data||"")+'"></label>'+(mov?'<label>Quantidade de Bags<input name="quantidade" type="text" inputmode="text" value="'+escHist(item.quantidade??"")+'"></label>':'')+(item.destino!==undefined?'<label>Destino<input name="destino" type="text" value="'+escHist(item.destino||"")+'"></label>':'')+'<label>Observação<textarea name="observacao">'+escHist(item.observacao||"")+'</textarea></label><button type="submit">💾 Salvar</button> <button type="button" onclick="alternarEdicaoHistorico('+i+',false)">Cancelar</button></form></div>';}).join("");
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
    const anterior = historico[pos], tipo = String(anterior.tipo || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""), movimento = tipo === "entrada" || tipo === "saida";
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

// ======================================
// EXCLUIR REGISTRO DO HISTÓRICO
// ======================================
function removerRegistroHistorico(indice, opcoes = {}) {
    const historico = carregarHistorico(); const pos = Number(indice);
    if (!Number.isInteger(pos) || pos < 0 || pos >= historico.length) return {ok:false,mensagem:"Registro do histórico não encontrado."};
    const item = historico[pos], tipo = String(item.tipo || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""), qtd = Number(item.quantidade) || 0;
    let estoqueAlterado = false;
    if (tipo === "entrada" || tipo === "saida") {
        const estoque = carregarEstoque(); let lote = estoque.find(x => item.loteId != null && Number(x.id) === Number(item.loteId));
        if (!lote) lote = estoque.find(x => String(x.cultivar||"").trim() === String(item.cultivar||"").trim() && String(x.lote||"").trim() === String(item.lote||"").trim());
        if (lote) {
            const saldo = (Number(lote.bags) || 0) + (tipo === "entrada" ? -qtd : qtd);
            if (saldo >= 0) { lote.bags = saldo; salvarEstoque(estoque,{silencioso:true}); estoqueAlterado = true; }
        }
    }
    historico.splice(pos, 1); salvarHistorico(historico,{silencioso:true});
    if (!opcoes.silencioso) notificarMudanca(estoqueAlterado ? "estoque" : "historico");
    return {ok:true,mensagem:"Movimentação excluída com sucesso."};
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
    if "back-button-v386.js" not in t:
        t = t.replace("</head>", '<script src="back-button-v386.js?v=3861"></script>\n</head>', 1)
    if "keyboard-universal-v387.js" not in t:
        t = t.replace("</head>", '<script src="keyboard-universal-v387.js?v=3871"></script>\n</head>', 1)
    html.write_text(t, encoding="utf-8")

# Add obvious entry points to the current home and history screens.
for name, label in [("index.html", "📁 PDFs, Excel e Planilhas"), ("historico.html", "📁 Ver PDFs, Excel e Planilhas")]:
    p = project / name; t = p.read_text(encoding="utf-8")
    if "arquivos.html" not in t:
        t = t.replace("</main>", '<p><button type="button" onclick="window.location.href=\'arquivos.html\'">'+label+'</button></p>\n</main>', 1) if "</main>" in t else t.replace("</body>", '<p><button type="button" onclick="window.location.href=\'arquivos.html\'">'+label+'</button></p>\n</body>', 1)
        p.write_text(t, encoding="utf-8")

# A mesma lista aparece no histórico, sem obrigar o usuário a trocar de tela.
historico = project / "historico.html"
hist_text = historico.read_text(encoding="utf-8")
if 'id="listaArquivos"' not in hist_text:
    hist_text = hist_text.replace('<div id="lista"></div>', '<div id="lista"></div><section class="card"><h2>📁 PDFs, Excel e Planilhas</h2><div id="listaArquivos"></div></section>', 1)
if 'src="arquivos.js?v=3842"' not in hist_text:
    hist_text = hist_text.replace('</body>', '<script src="arquivos.js?v=3842"></script>\n</body>', 1)
historico.write_text(hist_text, encoding="utf-8")

# Usar sempre o teclado nativo normal do Android. Os scripts antigos de IME
# substituíam a entrada do WebView e impediam a área de transferência do Gboard.
import re
keyboard_scripts = re.compile(r'<script[^>]+(?:seed-teclado-final|ime-nativo-real|teclado-sugestoes|keyboard-universal|movimentacao-colar)[^>]*></script>\s*', re.I)
keyboard_styles = re.compile(r'<link[^>]+(?:seed-teclado-final|ime-nativo-real|teclado-sugestoes)[^>]*>\s*', re.I)
for html in sorted(project.glob("*.html")):
    t = html.read_text(encoding="utf-8")
    t = keyboard_scripts.sub("", t)
    t = keyboard_styles.sub("", t)
    t = re.sub(r'\s+inputmode="(?:numeric|decimal)"', ' inputmode="text"', t, flags=re.I)
    t = re.sub(r'\btype="number"', 'type="text"', t, flags=re.I)
    t = re.sub(r'\s+autocomplete="off"', ' autocomplete="on"', t, flags=re.I)
    t = re.sub(r'\s+spellcheck="false"', ' spellcheck="true"', t, flags=re.I)
    html.write_text(t, encoding="utf-8")

native_input_js = r'''// SeedControl - teclado nativo Android em todos os campos de texto
(function () {
    "use strict";
    const tiposSemTecladoTexto = new Set(["file", "checkbox", "radio", "button", "submit", "reset", "color", "range", "date", "datetime-local", "time", "month", "week"]);
    function preparar(campo) {
        if (!campo || campo.disabled || campo.readOnly || campo.dataset.seedNativeKeyboard4005 === "1") return;
        const eInput = campo.tagName === "INPUT";
        const eTexto = eInput || campo.tagName === "TEXTAREA" || campo.isContentEditable;
        if (!eTexto) return;
        const tipo = String(campo.type || "text").toLowerCase();
        if (eInput && tiposSemTecladoTexto.has(tipo)) return;
        if (eInput && ["number", "tel", "search"].includes(tipo)) {
            try { campo.type = "text"; } catch (_) {}
        }
        campo.dataset.seedNativeKeyboard4005 = "1";
        campo.setAttribute("autocomplete", "on");
        campo.setAttribute("aria-autocomplete", "both");
        campo.setAttribute("enterkeyhint", "next");
        if (!campo.getAttribute("name") && campo.id) campo.setAttribute("name", campo.id);
        campo.setAttribute("autocorrect", "on");
        campo.setAttribute("autocapitalize", "sentences");
        campo.setAttribute("spellcheck", "true");
        if (campo.isContentEditable) campo.setAttribute("role", "textbox");
    }
    function varrer() {
        document.querySelectorAll("input, textarea, [contenteditable=true]").forEach(preparar);
    }
    function iniciar() {
        varrer();
        document.addEventListener("focusin", e => preparar(e.target), true);
        new MutationObserver(varrer).observe(document.body, {childList:true, subtree:true});
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, {once:true}); else iniciar();
})();
'''
(project / "teclado-nativo-seedcontrol.js").write_text(native_input_js, encoding="utf-8")
for html in sorted(project.glob("*.html")):
    t = html.read_text(encoding="utf-8")
    if "teclado-nativo-seedcontrol.js" not in t:
        t = t.replace("</head>", '<script src="teclado-nativo-seedcontrol.js?v=4005"></script>\n</head>', 1)
    else:
        t = re.sub(r'teclado-nativo-seedcontrol\.js\?v=\d+', 'teclado-nativo-seedcontrol.js?v=4005', t)
    html.write_text(t, encoding="utf-8")

if OUTPUT.exists(): OUTPUT.unlink()
with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(project.rglob("*")):
        if path.is_file(): archive.write(path, Path(project.name) / path.relative_to(project))
print(f"Fonte atualizada: {OUTPUT}")
print("Correções: armazenamento em DATA, cards editáveis, central de arquivos PDF/Excel/planilhas.")
