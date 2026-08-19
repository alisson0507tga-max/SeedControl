from pathlib import Path
import re

ROOT = Path('native/www')
MOV_HTML = ROOT / 'movimentacao.html'
MOV_JS = ROOT / 'movimentacao.js'
HIST_HTML = ROOT / 'historico.html'
HIST_JS = ROOT / 'historico.js'
REL_HTML = ROOT / 'relatorio-saidas.html'
REL_JS = ROOT / 'relatorio-saidas.js'
REL_CSS = ROOT / 'relatorio-saidas.css'
SW = ROOT / 'service-worker.js'

for arquivo in (MOV_HTML, MOV_JS, HIST_HTML, HIST_JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo não encontrado: {arquivo}')

# ---------------------------------------------------------
# MOVIMENTAÇÃO: campo Destino e snapshot completo da saída
# ---------------------------------------------------------
mov_html = MOV_HTML.read_text(encoding='utf-8')

if 'id="grupoDestino"' not in mov_html:
    ancora = '''<label><b>Observação</b></label>'''
    bloco = '''<div id="grupoDestino" style="display:none;">

<label><b>Destino da saída</b></label>

<input
id="destino"
type="text"
placeholder="Ex.: Fazenda Graciosa"
autocomplete="on"
autocorrect="on"
spellcheck="true"
autocapitalize="words">

<small style="display:block;margin-top:-4px;margin-bottom:12px;opacity:.75;">
Informe para onde as bags foram enviadas. Ex.: Fazenda Graciosa, Talhão 4.
</small>

</div>

<label><b>Observação</b></label>'''
    if ancora not in mov_html:
        raise SystemExit('Âncora Observação não encontrada em movimentacao.html')
    mov_html = mov_html.replace(ancora, bloco, 1)

MOV_HTML.write_text(mov_html, encoding='utf-8')

mov_js = MOV_JS.read_text(encoding='utf-8')

if 'seedcontrol-destino-saida-v3831' not in mov_js:
    mov_js = '// seedcontrol-destino-saida-v3831\n' + mov_js

# Elementos destino
if 'const destino = document.getElementById("destino");' not in mov_js:
    ancora = 'const obs = document.getElementById("obs");'
    novo = '''const obs = document.getElementById("obs");
const destino = document.getElementById("destino");
const grupoDestino = document.getElementById("grupoDestino");'''
    if ancora not in mov_js:
        raise SystemExit('Âncora obs não encontrada em movimentacao.js')
    mov_js = mov_js.replace(ancora, novo, 1)

# Mostrar destino só na saída
if 'function atualizarCampoDestino' not in mov_js:
    ancora = '// Salvar movimentação'
    bloco = '''function atualizarCampoDestino() {

    if (!grupoDestino) return;

    const ehSaida = tipo.value === "saida";
    grupoDestino.style.display = ehSaida ? "block" : "none";

}

tipo.addEventListener("change", atualizarCampoDestino);
atualizarCampoDestino();

// Salvar movimentação'''
    if ancora not in mov_js:
        raise SystemExit('Âncora Salvar movimentação não encontrada')
    mov_js = mov_js.replace(ancora, bloco, 1)

# Acrescentar snapshot ao objeto do histórico
if 'fazendaOrigem:' not in mov_js:
    ancora = '''        quantidade: qtd,

        observacao: obs.value.trim()'''
    novo = '''        quantidade: qtd,

        peneira: registro.peneira || "",

        fazendaOrigem: registro.fazenda || "",

        talhao: registro.talhao || "",

        destino: tipo.value === "saida" && destino
            ? destino.value.trim()
            : "",

        observacao: obs.value.trim()'''
    if ancora not in mov_js:
        raise SystemExit('Objeto de histórico não encontrado em movimentacao.js')
    mov_js = mov_js.replace(ancora, novo, 1)

MOV_JS.write_text(mov_js, encoding='utf-8')

# ---------------------------------------------------------
# HISTÓRICO: botão + mostrar Destino em saídas
# ---------------------------------------------------------
hist_html = HIST_HTML.read_text(encoding='utf-8')

if 'relatorio-saidas.html' not in hist_html:
    ancora = '<div id="lista"></div>'
    bloco = '''<button
id="btnRelatorioSaidas"
type="button"
onclick="window.location.href='relatorio-saidas.html'"
style="margin-bottom:16px;background:#16a34a;">
📄 Relatório de Saídas
</button>

<div id="lista"></div>'''
    if ancora not in hist_html:
        raise SystemExit('lista não encontrada em historico.html')
    hist_html = hist_html.replace(ancora, bloco, 1)

HIST_HTML.write_text(hist_html, encoding='utf-8')

hist_js = HIST_JS.read_text(encoding='utf-8')

if 'seedcontrol-historico-destino-v3831' not in hist_js:
    hist_js = '// seedcontrol-historico-destino-v3831\n' + hist_js

if '${item.destino' not in hist_js:
    ancora = '''            <p><strong>📦 Quantidade:</strong> ${item.quantidade} Bags</p>

            <p><strong>📝 Observação:</strong> ${item.observacao || "Sem observação"}</p>'''
    novo = '''            <p><strong>📦 Quantidade:</strong> ${item.quantidade} Bags</p>

            ${item.tipo === "saida" ? `
                <p><strong>🚚 Destino:</strong> ${item.destino || "Não informado"}</p>
            ` : ""}

            <p><strong>📝 Observação:</strong> ${item.observacao || "Sem observação"}</p>'''
    if ancora not in hist_js:
        raise SystemExit('Bloco Quantidade/Observação não encontrado em historico.js')
    hist_js = hist_js.replace(ancora, novo, 1)

HIST_JS.write_text(hist_js, encoding='utf-8')

# ---------------------------------------------------------
# RELATÓRIO DE SAÍDAS
# ---------------------------------------------------------
rel_html = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#071713">
<title>Relatório de Saídas - SeedControl</title>
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="app-v384.css">
<link rel="stylesheet" href="relatorio-saidas.css?v=3831">
</head>
<body class="rel-saidas-body">
<header class="rel-saidas-topo">
    <h1>📄 Relatório de Saídas</h1>
    <p>Movimentações de saída do estoque</p>
</header>

<main class="container rel-saidas-container">
    <section class="rel-painel">
        <h2>🔎 Filtros</h2>

        <label for="periodo">Período</label>
        <select id="periodo">
            <option value="hoje">Hoje</option>
            <option value="7dias">Últimos 7 dias</option>
            <option value="mes" selected>Mês atual</option>
            <option value="todos">Todo o histórico</option>
            <option value="personalizado">Período personalizado</option>
        </select>

        <div id="datasPersonalizadas" class="rel-grid-2" hidden>
            <div>
                <label for="dataInicio">De</label>
                <input id="dataInicio" type="date">
            </div>
            <div>
                <label for="dataFim">Até</label>
                <input id="dataFim" type="date">
            </div>
        </div>

        <div class="rel-grid-2">
            <div>
                <label for="filtroCultivar">Cultivar</label>
                <input id="filtroCultivar" type="text" placeholder="Ex.: Guepardo">
            </div>
            <div>
                <label for="filtroLote">Lote</label>
                <input id="filtroLote" type="text" placeholder="Ex.: 10">
            </div>
        </div>

        <label for="filtroDestino">Destino</label>
        <input id="filtroDestino" type="text" placeholder="Ex.: Fazenda Graciosa">

        <button id="aplicarFiltros" type="button">🔎 Aplicar filtros</button>
    </section>

    <section class="rel-resumo">
        <article>
            <small>Saídas encontradas</small>
            <strong id="totalSaidas">0</strong>
        </article>
        <article>
            <small>Total de Bags</small>
            <strong id="totalBagsSaidas">0</strong>
        </article>
    </section>

    <section class="rel-acoes">
        <button id="exportarPDF" type="button">📕 PDF</button>
        <button id="exportarExcel" type="button">📗 Excel</button>
        <button id="compartilharPDF" type="button">📤 Compartilhar</button>
    </section>

    <section>
        <div class="rel-lista-titulo">
            <h2>Saídas</h2>
            <span id="periodoDescricao"></span>
        </div>
        <div id="listaSaidas"></div>
    </section>

    <button type="button" class="rel-voltar" onclick="window.location.href='historico.html'">← Voltar ao Histórico</button>
</main>

<script src="database.js"></script>
<script src="vendor/jspdf.umd.min.js"></script>
<script src="vendor/jspdf.plugin.autotable.min.js"></script>
<script src="vendor/xlsx-js-style.bundle.js"></script>
<script src="relatorio-saidas.js?v=3831"></script>
</body>
</html>
'''
REL_HTML.write_text(rel_html, encoding='utf-8')

rel_css = r'''/* SeedControl v3.8.4 - Relatório de Saídas */
.rel-saidas-body{min-height:100vh;background:linear-gradient(180deg,#06111a,#071722 55%,#06141d);color:#f8fafc}
.rel-saidas-topo{padding:24px 18px 22px;text-align:center;background:linear-gradient(110deg,#071814,#063322 58%,#06251d);border-bottom:1px solid rgba(74,222,128,.25)}
.rel-saidas-topo h1{margin:0;font-size:30px}.rel-saidas-topo p{margin:7px 0 0;color:#b8c5ca}
.rel-saidas-container{max-width:760px;margin:0 auto;padding:18px 16px calc(28px + env(safe-area-inset-bottom))}
.rel-painel,.rel-resumo{padding:16px;margin-bottom:14px;border:1px solid rgba(148,163,184,.20);border-radius:18px;background:linear-gradient(145deg,rgba(20,38,49,.97),rgba(10,28,39,.97));box-shadow:0 8px 22px rgba(0,0,0,.22)}
.rel-painel h2{margin:0 0 14px}.rel-painel label{display:block;margin:11px 0 6px;color:#dce6e9;font-weight:700;font-size:13px}
.rel-painel input,.rel-painel select{width:100%;min-height:48px;padding:0 12px;border-radius:12px;border:1px solid rgba(148,163,184,.28);background:#071821;color:#fff;font-size:15px}
.rel-painel button{width:100%;margin-top:15px;background:#16a34a}.rel-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.rel-resumo{display:grid;grid-template-columns:1fr 1fr;gap:10px}.rel-resumo article{padding:14px;border-radius:14px;background:rgba(5,25,34,.62);border:1px solid rgba(148,163,184,.15)}
.rel-resumo small{display:block;color:#9fb0b8;margin-bottom:5px}.rel-resumo strong{color:#4ade80;font-size:26px}
.rel-acoes{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:0 0 18px}.rel-acoes button{min-height:48px;padding:8px;font-size:13px}.rel-acoes button:nth-child(1){background:#b91c1c}.rel-acoes button:nth-child(2){background:#15803d}.rel-acoes button:nth-child(3){background:#2563eb}
.rel-lista-titulo{margin:17px 2px 10px}.rel-lista-titulo h2{margin:0}.rel-lista-titulo span{display:block;margin-top:4px;color:#93a5ae;font-size:12px}
.rel-saida-card{margin-bottom:12px;padding:15px;border-radius:17px;border:1px solid rgba(148,163,184,.18);background:linear-gradient(145deg,rgba(20,38,49,.98),rgba(10,28,39,.98))}
.rel-saida-card h3{margin:0 0 10px;font-size:19px;color:#fff}.rel-saida-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px 10px}.rel-saida-grid p{margin:0;padding:8px;border-radius:9px;background:rgba(6,21,30,.48);font-size:13px;color:#d8e1e5}.rel-saida-grid strong{display:block;color:#91a2aa;font-size:11px;margin-bottom:2px}.rel-saida-destino{grid-column:1/-1}.rel-vazio{padding:22px;text-align:center;border:1px dashed rgba(148,163,184,.25);border-radius:15px;color:#aebcc2}.rel-voltar{width:100%;margin-top:18px;background:#0b3b2b}
@media(max-width:430px){.rel-grid-2,.rel-saida-grid{grid-template-columns:1fr}.rel-saida-destino{grid-column:auto}.rel-acoes{grid-template-columns:1fr 1fr}.rel-acoes button:last-child{grid-column:1/-1}}
'''
REL_CSS.write_text(rel_css, encoding='utf-8')

rel_js = r'''// seedcontrol-relatorio-saidas-v3831
(function(){
"use strict";

const historico = typeof carregarHistorico === "function" ? carregarHistorico() : [];
const saidas = historico.filter(item => item && item.tipo === "saida");
let filtradas = [];

const $ = id => document.getElementById(id);
const periodo = $("periodo");
const datasPersonalizadas = $("datasPersonalizadas");
const dataInicio = $("dataInicio");
const dataFim = $("dataFim");
const filtroCultivar = $("filtroCultivar");
const filtroLote = $("filtroLote");
const filtroDestino = $("filtroDestino");
const lista = $("listaSaidas");
const totalSaidas = $("totalSaidas");
const totalBags = $("totalBagsSaidas");
const periodoDescricao = $("periodoDescricao");

function normalizar(v){return String(v==null?"":v).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();}
function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}

function parseDataBR(texto){
    const s=String(texto||"").trim();
    const m=s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:,?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?/);
    if(!m) return null;
    const d=new Date(Number(m[3]),Number(m[2])-1,Number(m[1]),Number(m[4]||0),Number(m[5]||0),Number(m[6]||0));
    return isNaN(d.getTime())?null:d;
}
function inicioDia(d){return new Date(d.getFullYear(),d.getMonth(),d.getDate());}
function fimDia(d){return new Date(d.getFullYear(),d.getMonth(),d.getDate(),23,59,59,999);}

function intervaloAtual(){
    const agora=new Date();
    const p=periodo.value;
    if(p==="todos") return {ini:null,fim:null,texto:"Todo o histórico"};
    if(p==="hoje") return {ini:inicioDia(agora),fim:fimDia(agora),texto:"Hoje"};
    if(p==="7dias") {const ini=inicioDia(agora);ini.setDate(ini.getDate()-6);return {ini,fim:fimDia(agora),texto:"Últimos 7 dias"};}
    if(p==="mes") return {ini:new Date(agora.getFullYear(),agora.getMonth(),1),fim:new Date(agora.getFullYear(),agora.getMonth()+1,0,23,59,59,999),texto:"Mês atual"};
    const ini=dataInicio.value?new Date(dataInicio.value+"T00:00:00"):null;
    const fim=dataFim.value?new Date(dataFim.value+"T23:59:59"):null;
    return {ini,fim,texto:"Período personalizado"};
}

function aplicar(){
    const inter=intervaloAtual();
    const cult=normalizar(filtroCultivar.value);
    const lote=normalizar(filtroLote.value);
    const dest=normalizar(filtroDestino.value);
    filtradas=saidas.filter(item=>{
        const d=parseDataBR(item.data);
        if(inter.ini && (!d || d<inter.ini)) return false;
        if(inter.fim && (!d || d>inter.fim)) return false;
        if(cult && !normalizar(item.cultivar).includes(cult)) return false;
        if(lote && normalizar(item.lote)!==lote) return false;
        if(dest && !normalizar(item.destino).includes(dest)) return false;
        return true;
    });
    render(inter.texto);
}

function render(desc){
    totalSaidas.textContent=String(filtradas.length);
    const soma=filtradas.reduce((acc,x)=>acc+(Number(x.quantidade)||0),0);
    totalBags.textContent=soma.toLocaleString("pt-BR",{maximumFractionDigits:2});
    periodoDescricao.textContent=desc;
    if(!filtradas.length){lista.innerHTML='<div class="rel-vazio">Nenhuma saída encontrada para os filtros selecionados.</div>';return;}
    lista.innerHTML=filtradas.map(item=>`
      <article class="rel-saida-card">
        <h3>➖ ${esc(item.cultivar||"Sem cultivar")} — Lote ${esc(item.lote||"-")}</h3>
        <div class="rel-saida-grid">
          <p><strong>📅 Data</strong>${esc(item.data||"-")}</p>
          <p><strong>📦 Quantidade</strong>${esc(item.quantidade||0)} Bags</p>
          <p><strong>🌾 Peneira</strong>${esc(item.peneira||"-")}</p>
          <p><strong>🚜 Origem</strong>${esc(item.fazendaOrigem||"-")}</p>
          <p><strong>📍 Talhão</strong>${esc(item.talhao||"-")}</p>
          <p class="rel-saida-destino"><strong>🚚 Destino</strong>${esc(item.destino||"Não informado")}</p>
          <p class="rel-saida-destino"><strong>📝 Observação</strong>${esc(item.observacao||"Sem observação")}</p>
        </div>
      </article>`).join("");
}

function nomeBase(){const d=new Date();return `SeedControl_Relatorio_Saidas_${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;}
function rows(){return filtradas.map(x=>[x.data||"",x.cultivar||"",x.peneira||"",x.lote||"",Number(x.quantidade)||0,x.fazendaOrigem||"",x.talhao||"",x.destino||"Não informado",x.observacao||""]);}
function bytesBase64(dados){const u=dados instanceof Uint8Array?dados:new Uint8Array(dados);let s="";for(let i=0;i<u.length;i+=0x8000)s+=String.fromCharCode.apply(null,u.subarray(i,Math.min(i+0x8000,u.length)));return btoa(s);}
function native(){return !!(window.Capacitor&&typeof window.Capacitor.isNativePlatform==="function"&&window.Capacitor.isNativePlatform());}
async function salvar(nome,dados,compartilhar){
    if(!native()) return null;
    const fs=window.Capacitor&&window.Capacitor.Plugins&&window.Capacitor.Plugins.Filesystem;
    const sh=window.Capacitor&&window.Capacitor.Plugins&&window.Capacitor.Plugins.Share;
    if(!fs) throw new Error("Filesystem indisponível");
    const b64=bytesBase64(dados);
    const salvo=await fs.writeFile({path:"SeedControl/RelatoriosSaidas/"+nome,data:b64,directory:"DOCUMENTS",recursive:true});
    if(compartilhar){if(!sh) throw new Error("Compartilhamento indisponível");const temp=await fs.writeFile({path:"SeedControlShare/"+nome,data:b64,directory:"CACHE",recursive:true});await sh.share({title:nome,text:"Relatório de saídas do SeedControl",url:temp.uri,dialogTitle:"Compartilhar relatório"});}
    return salvo;
}

async function gerarPDF(compartilhar){
    if(!filtradas.length){alert("Não há saídas para gerar o relatório.");return;}
    const jsPDF=window.jspdf&&window.jspdf.jsPDF;if(!jsPDF) throw new Error("jsPDF não carregou");
    const pdf=new jsPDF({orientation:"landscape",unit:"mm",format:"a4"});
    pdf.setFontSize(16);pdf.text("RELATÓRIO DE SAÍDAS - SEEDCONTROL",148,13,{align:"center"});
    pdf.setFontSize(9);pdf.text(`Período: ${periodoDescricao.textContent} | Saídas: ${filtradas.length} | Total: ${totalBags.textContent} bags`,14,20);
    pdf.autoTable({startY:25,head:[["Data","Cultivar","Pen.","Lote","Bags","Origem","Talhão","Destino","Observação"]],body:rows(),styles:{fontSize:7,cellPadding:1.5},headStyles:{fillColor:[22,163,74]},columnStyles:{0:{cellWidth:30},1:{cellWidth:42},8:{cellWidth:45}}});
    const nome=nomeBase()+".pdf";
    if(native()){const dados=pdf.output("arraybuffer");await salvar(nome,dados,compartilhar);if(!compartilhar) alert("PDF salvo em Documentos/SeedControl/RelatoriosSaidas.");}
    else pdf.save(nome);
}

async function gerarExcel(){
    if(!filtradas.length){alert("Não há saídas para gerar o relatório.");return;}
    if(!window.XLSX) throw new Error("Biblioteca Excel não carregou");
    const dados=[["RELATÓRIO DE SAÍDAS - SEEDCONTROL"],["DATA","CULTIVAR","PENEIRA","LOTE","BAGS","ORIGEM","TALHÃO","DESTINO","OBSERVAÇÃO"],...rows(),["","","","TOTAL",filtradas.reduce((a,x)=>a+(Number(x.quantidade)||0),0),"","","",""]];
    const ws=XLSX.utils.aoa_to_sheet(dados);ws["!merges"]=[{s:{r:0,c:0},e:{r:0,c:8}}];ws["!cols"]=[{wch:22},{wch:25},{wch:10},{wch:10},{wch:10},{wch:20},{wch:10},{wch:24},{wch:35}];
    for(let c=0;c<9;c++){const a=XLSX.utils.encode_cell({r:0,c});if(!ws[a])ws[a]={t:"s",v:""};ws[a].s={fill:{patternType:"solid",fgColor:{rgb:"4DD0E1"}},font:{bold:true},alignment:{horizontal:"center"}};const h=XLSX.utils.encode_cell({r:1,c});ws[h].s={fill:{patternType:"solid",fgColor:{rgb:"E0F7FA"}},font:{bold:true},alignment:{horizontal:"center"}};}
    const wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,ws,"Saídas");const nome=nomeBase()+".xlsx";
    if(native()){const arr=XLSX.write(wb,{bookType:"xlsx",type:"array"});await salvar(nome,arr,false);alert("Excel salvo em Documentos/SeedControl/RelatoriosSaidas.");}else XLSX.writeFile(wb,nome);
}

periodo.addEventListener("change",()=>{datasPersonalizadas.hidden=periodo.value!=="personalizado";aplicar();});
$("aplicarFiltros").addEventListener("click",aplicar);
$("exportarPDF").addEventListener("click",()=>gerarPDF(false).catch(e=>alert("Erro ao gerar PDF: "+e.message)));
$("compartilharPDF").addEventListener("click",()=>gerarPDF(true).catch(e=>alert("Erro ao compartilhar: "+e.message)));
$("exportarExcel").addEventListener("click",()=>gerarExcel().catch(e=>alert("Erro ao gerar Excel: "+e.message)));
[filtroCultivar,filtroLote,filtroDestino,dataInicio,dataFim].forEach(el=>el&&el.addEventListener("change",aplicar));
aplicar();
})();
'''
REL_JS.write_text(rel_js, encoding='utf-8')

# ---------------------------------------------------------
# Cache: abandonar conteúdo antigo e incluir relatório
# ---------------------------------------------------------
if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-31', sw, count=1)
    # Tenta incluir os novos arquivos no APP_SHELL se existir lista literal.
    if 'relatorio-saidas.html' not in sw:
        m = re.search(r'(const\s+APP_SHELL\s*=\s*\[)(.*?)(\];)', sw, flags=re.S)
        if m:
            miolo = m.group(2).rstrip()
            virg = ',' if miolo and not miolo.rstrip().endswith(',') else ''
            extra = f'{virg}\n  "./relatorio-saidas.html",\n  "./relatorio-saidas.js",\n  "./relatorio-saidas.css"\n'
            sw = sw[:m.start(2)] + miolo + extra + sw[m.end(2):]
    SW.write_text(sw, encoding='utf-8')

# ---------------------------------------------------------
# Validações
# ---------------------------------------------------------
for arquivo, marcas in {
    MOV_HTML: ['id="grupoDestino"','id="destino"','Destino da saída'],
    MOV_JS: ['seedcontrol-destino-saida-v3831','fazendaOrigem:','destino: tipo.value === "saida"'],
    HIST_HTML: ['relatorio-saidas.html','Relatório de Saídas'],
    HIST_JS: ['seedcontrol-historico-destino-v3831','🚚 Destino'],
    REL_HTML: ['relatorio-saidas.js?v=3831','Compartilhar','Total de Bags'],
    REL_JS: ['seedcontrol-relatorio-saidas-v3831','tipo === "saida"','RelatoriosSaidas','autoTable','XLSX.write'],
    REL_CSS: ['rel-saida-card','rel-acoes']
}.items():
    txt = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in txt:
            raise SystemExit(f'Validação falhou em {arquivo.name}: {marca}')

print('Relatório de Saídas pronto: destino na movimentação, snapshot no histórico, filtros, PDF, Excel e compartilhamento.')
