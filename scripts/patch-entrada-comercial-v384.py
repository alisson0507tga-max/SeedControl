from pathlib import Path
import re

ROOT = Path("native/www")
PLANILHA_HTML = ROOT / "planilha.html"
CADASTRO_HTML = ROOT / "cadastro.html"
BACKUP_HTML = ROOT / "backup.html"
SW = ROOT / "service-worker.js"

for arquivo in (PLANILHA_HTML, CADASTRO_HTML):
    if not arquivo.exists():
        raise SystemExit(f"Arquivo obrigatório não encontrado: {arquivo}")

CORE = r'''// seedcontrol-entrada-comercial-core-v3903
(function () {
    "use strict";

    const CHAVE = "seedcontrol_entrada_comercial_2026";
    const CAMPO_BACKUP = "entradaComercial2026";

    function numero(valor) {
        const n = Number(String(valor == null ? "" : valor).replace(",", "."));
        return Number.isFinite(n) ? n : 0;
    }

    function texto(valor) {
        return String(valor == null ? "" : valor).trim();
    }

    function hojeBR() {
        return new Date().toLocaleDateString("pt-BR");
    }

    function normalizarRegistro(item) {
        const registro = item && typeof item === "object" ? item : {};
        const pms = numero(registro.pms);
        const bags = numero(registro.bags);
        const pesoBagKg = numero(registro.pesoBagKg) || (pms > 0 ? pms * 5 : 0);
        const kg = numero(registro.kg) || numero(registro.kgsMedia) || (bags * pesoBagKg);

        return {
            id: texto(registro.id) || ("EC-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8)),
            origemLoteId: texto(registro.origemLoteId),
            dataEntrada: texto(registro.dataEntrada) || hojeBR(),
            cultivar: texto(registro.cultivar),
            lote: texto(registro.lote),
            bags: bags,
            kg: kg,
            pms: pms,
            germinacao: texto(registro.germinacao),
            observacao: texto(registro.observacao),
            criadoEm: texto(registro.criadoEm) || new Date().toISOString(),
            atualizadoEm: texto(registro.atualizadoEm) || new Date().toISOString()
        };
    }

    function lerConfiguracoes() {
        try {
            if (typeof window.carregarConfiguracoes === "function") {
                const cfg = window.carregarConfiguracoes();
                return cfg && typeof cfg === "object" && !Array.isArray(cfg) ? cfg : {};
            }
            const bruto = localStorage.getItem("configuracoes");
            const cfg = bruto ? JSON.parse(bruto) : {};
            return cfg && typeof cfg === "object" && !Array.isArray(cfg) ? cfg : {};
        } catch (_) {
            return {};
        }
    }

    function gravarConfiguracoes(cfg) {
        try {
            if (typeof window.salvarConfiguracoes === "function") {
                window.salvarConfiguracoes(cfg, { silencioso: true });
            } else {
                localStorage.setItem("configuracoes", JSON.stringify(cfg));
            }
        } catch (_) {}
    }

    function carregar() {
        let lista = [];
        try {
            const bruto = localStorage.getItem(CHAVE);
            const parsed = bruto ? JSON.parse(bruto) : null;
            if (Array.isArray(parsed)) lista = parsed;
        } catch (_) {}

        if (!lista.length) {
            const cfg = lerConfiguracoes();
            if (Array.isArray(cfg[CAMPO_BACKUP])) {
                lista = cfg[CAMPO_BACKUP];
            }
        }

        return lista.map(normalizarRegistro);
    }

    function salvar(lista) {
        const normalizada = (Array.isArray(lista) ? lista : []).map(normalizarRegistro);
        localStorage.setItem(CHAVE, JSON.stringify(normalizada));

        // Espelho dentro das configurações para entrar no backup normal do SeedControl.
        const cfg = lerConfiguracoes();
        cfg[CAMPO_BACKUP] = normalizada;
        gravarConfiguracoes(cfg);

        try {
            window.dispatchEvent(new CustomEvent("seedcontrol:entrada-comercial-atualizada", {
                detail: { total: normalizada.length }
            }));
        } catch (_) {}

        return normalizada;
    }

    function calcularPesoBagPMS(pms) {
        const valor = numero(pms);
        return valor > 0 ? valor * 5 : 0;
    }

    function estimarBagsPorKg(kg, pms) {
        const pesoBag = calcularPesoBagPMS(pms);
        const pesoTotal = numero(kg);
        return pesoBag > 0 && pesoTotal > 0 ? pesoTotal / pesoBag : 0;
    }

    function registrarLoteComercial(lote) {
        if (!lote || typeof lote !== "object") return null;

        const metodo = typeof window.normalizarMetodoPeso === "function"
            ? window.normalizarMetodoPeso(lote.metodoPeso)
            : texto(lote.metodoPeso).toLowerCase();

        if (metodo !== "comercial" && metodo !== "pms") return null;

        const origemId = texto(lote.id);
        const lista = carregar();
        if (origemId && lista.some(item => item.origemLoteId === origemId)) {
            return lista.find(item => item.origemLoteId === origemId) || null;
        }

        const pms = numero(lote.pms);
        const bags = numero(lote.bags);
        const pesoBagKg = numero(lote.pesoBagKg) || calcularPesoBagPMS(pms);
        const registro = normalizarRegistro({
            origemLoteId: origemId,
            dataEntrada: hojeBR(),
            cultivar: lote.cultivar,
            lote: lote.lote,
            bags: bags,
            kg: numero(lote.kgsMedia) || (bags * pesoBagKg),
            pms: pms,
            germinacao: "",
            observacao: ""
        });

        lista.unshift(registro);
        salvar(lista);
        return registro;
    }

    function instalarIntegracaoCadastro() {
        const original = window.cadastrarLote;
        if (typeof original !== "function" || original.__seedEntradaComercialV3903) return;

        function cadastrarComEntradaComercial(novoLote, opcoes) {
            const resultado = original.apply(this, arguments);
            try {
                const checkbox = document.getElementById("registrarEntradaComercial3903");
                const permitido = !checkbox || checkbox.checked;
                if (permitido && resultado && resultado.ok && resultado.lote) {
                    registrarLoteComercial(resultado.lote);
                }
            } catch (erro) {
                console.error("Falha ao registrar Entrada Comercial:", erro);
            }
            return resultado;
        }

        cadastrarComEntradaComercial.__seedEntradaComercialV3903 = true;
        window.cadastrarLote = cadastrarComEntradaComercial;
    }

    function criarOpcaoCadastro() {
        const salvarBtn = document.getElementById("salvar");
        const metodo = document.getElementById("metodoPeso");
        if (!salvarBtn || !metodo || document.getElementById("entradaComercialOpcao3903")) return;

        const bloco = document.createElement("div");
        bloco.id = "entradaComercialOpcao3903";
        bloco.style.cssText = "margin:14px 0;padding:13px;border:1px solid rgba(74,222,128,.28);border-radius:13px;background:rgba(7,45,34,.55);display:none";
        bloco.innerHTML = '<label style="display:flex;gap:10px;align-items:flex-start;margin:0;cursor:pointer"><input id="registrarEntradaComercial3903" type="checkbox" checked style="margin-top:3px"><span><strong>📥 Registrar na Entrada Comercial 2026</strong><small style="display:block;margin-top:4px;color:#aebdc2;line-height:1.35">Guarda este recebimento na planilha comercial baseada no PMS.</small></span></label>';
        salvarBtn.parentNode.insertBefore(bloco, salvarBtn);

        function atualizar() {
            const valor = texto(metodo.value).toLowerCase();
            bloco.style.display = (valor === "comercial" || valor === "pms") ? "block" : "none";
        }
        metodo.addEventListener("change", atualizar);
        atualizar();
    }

    function sincronizarEspelhoBackup() {
        const lista = carregar();
        if (lista.length) salvar(lista);
    }

    window.carregarEntradasComerciais = carregar;
    window.salvarEntradasComerciais = salvar;
    window.registrarEntradaComercialDoLote = registrarLoteComercial;
    window.calcularPesoBagComercialPorPMS = calcularPesoBagPMS;
    window.estimarBagsComerciaisPorKg = estimarBagsPorKg;

    instalarIntegracaoCadastro();
    sincronizarEspelhoBackup();

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            instalarIntegracaoCadastro();
            criarOpcaoCadastro();
        });
    } else {
        criarOpcaoCadastro();
    }
})();
'''

HTML = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#071713">
<title>Entrada Comercial 2026 - SeedControl</title>
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="app-v384.css">
<link rel="stylesheet" href="entrada-comercial-v3903.css">
</head>
<body class="entrada-comercial-body">
<header class="topo entrada-comercial-topo">
<h1>📥 Entrada Comercial 2026</h1>
<p>Recebimento de sementes calculado pelo PMS</p>
</header>
<main class="container entrada-comercial-container">
<section class="card entrada-comercial-resumo">
<div><small>Registros</small><strong id="ecTotalRegistros">0</strong></div>
<div><small>Bags</small><strong id="ecTotalBags">0</strong></div>
<div><small>Kg</small><strong id="ecTotalKg">0</strong></div>
</section>
<section class="card entrada-comercial-acoes">
<input id="ecPesquisa" type="text" placeholder="Buscar cultivar, lote ou observação..." autocomplete="off">
<div class="ec-botoes">
<button id="ecNovo" type="button">➕ Nova entrada</button>
<button id="ecExportar" type="button">📗 Exportar Excel</button>
</div>
</section>
<section class="card card-planilha">
<p class="ec-aviso">↔️ Arraste para os lados para visualizar todas as colunas.</p>
<div class="ec-scroll">
<table class="ec-tabela">
<thead>
<tr class="ec-titulo"><th colspan="9">ENTRADA DE SEMENTES SOJA</th></tr>
<tr class="ec-cabecalho">
<th>DATA<br>ENTRADA</th><th>CULTIVAR</th><th>LOTE</th><th>BAGS</th><th>Kg</th><th>PMS(g)</th><th>GERMINAÇÃO<br>(nota)</th><th>OBSERVAÇÃO</th><th>AÇÃO</th>
</tr>
</thead>
<tbody id="ecCorpo"><tr><td colspan="9">Carregando...</td></tr></tbody>
</table>
</div>
</section>
<button class="ec-voltar" type="button" onclick="window.location.href='planilha.html'">← Voltar para Planilhas</button>
</main>
<div id="ecModal" class="ec-modal" hidden>
<div class="ec-modal-card">
<div class="ec-modal-topo"><h2 id="ecModalTitulo">Nova entrada</h2><button id="ecFechar" type="button">✕</button></div>
<div class="ec-form-grid">
<label>Data de entrada<input id="ecData" type="text" placeholder="dd/mm/aaaa"></label>
<label>Cultivar<input id="ecCultivar" type="text"></label>
<label>Lote<input id="ecLote" type="text" inputmode="text"></label>
<label>Kg recebidos<input id="ecKg" type="number" step="0.001" inputmode="decimal"></label>
<label>PMS (g)<input id="ecPms" type="number" step="0.01" inputmode="decimal"></label>
<label>Bags estimados<input id="ecBags" type="number" step="0.01" inputmode="decimal"></label>
<label>Germinação (nota)<input id="ecGerminacao" type="text" inputmode="decimal"></label>
<label class="ec-observacao">Observação<textarea id="ecObservacao" rows="3"></textarea></label>
</div>
<div class="ec-calculo"><button id="ecEstimar" type="button">🧮 Estimar Bags pelo PMS</button><small>Fórmula comercial: peso de 1 Bag = PMS × 5 kg.</small></div>
<div class="ec-modal-acoes"><button id="ecExcluir" type="button" class="perigo">🗑 Excluir</button><button id="ecSalvar" type="button">💾 Salvar</button></div>
</div>
</div>
<script src="database.js"></script>
<script src="entrada-comercial-core-v3903.js"></script>
<script src="vendor/xlsx-js-style.bundle.js"></script>
<script src="entrada-comercial-v3903.js"></script>
</body>
</html>
'''

CSS = r'''/* seedcontrol-entrada-comercial-v3903 */
.entrada-comercial-body{background:linear-gradient(180deg,#06111a,#071722 48%,#06141d);color:#f8fafc;min-height:100vh}.entrada-comercial-topo{background:linear-gradient(110deg,#071814,#063322 58%,#06251d)}.entrada-comercial-container{max-width:980px;margin:auto;padding:18px 14px 32px}.entrada-comercial-resumo{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.entrada-comercial-resumo div{padding:12px;border-radius:12px;background:#071d27;border:1px solid rgba(148,163,184,.16)}.entrada-comercial-resumo small{display:block;color:#9fb0b7}.entrada-comercial-resumo strong{display:block;margin-top:4px;font-size:24px;color:#4ade80}.entrada-comercial-acoes input{width:100%;min-height:50px;border-radius:12px;border:1px solid rgba(148,163,184,.28);background:#06141d;color:white;padding:0 14px}.ec-botoes{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:11px}.ec-botoes button,.ec-voltar,.ec-modal-acoes button,.ec-calculo button{min-height:48px;border-radius:12px;border:1px solid rgba(74,222,128,.35);background:#0d6435;color:#fff;font-weight:700}.ec-scroll{overflow:auto;border-radius:10px}.ec-tabela{border-collapse:collapse;min-width:980px;width:100%;background:white;color:#111}.ec-tabela th,.ec-tabela td{border:1px solid #222;padding:7px 8px;text-align:center;font-weight:700}.ec-titulo th{background:#f36b21;font-size:22px}.ec-cabecalho th{background:#b7dfcc;font-size:12px}.ec-tabela tbody tr:nth-child(even){background:#fde3d8}.ec-tabela tbody tr:nth-child(odd){background:#fff}.ec-tabela td:nth-child(2),.ec-tabela td:nth-child(3),.ec-tabela td:nth-child(8){text-align:left}.ec-editar{border:0;border-radius:8px;padding:7px 10px;background:#176f3d;color:#fff}.ec-aviso{color:#aab9c0;font-size:12px}.ec-voltar{width:100%;margin-top:14px;background:#0c3e2b}.ec-modal{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.76);padding:18px;overflow:auto}.ec-modal-card{max-width:680px;margin:4vh auto;background:#102632;border:1px solid rgba(74,222,128,.28);border-radius:18px;padding:17px;box-shadow:0 20px 60px #000}.ec-modal-topo{display:flex;align-items:center;justify-content:space-between}.ec-modal-topo h2{margin:0}.ec-modal-topo button{width:42px;height:42px;border-radius:50%;border:1px solid #475569;background:#172c38;color:#fff}.ec-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.ec-form-grid label{font-size:13px;font-weight:700}.ec-form-grid input,.ec-form-grid textarea{width:100%;margin-top:6px;border-radius:10px;border:1px solid #415563;background:#071923;color:#fff;padding:11px}.ec-observacao{grid-column:1/-1}.ec-calculo{margin-top:12px;padding:12px;border-radius:12px;background:#092419}.ec-calculo button{width:100%}.ec-calculo small{display:block;margin-top:7px;color:#a9bbb2}.ec-modal-acoes{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}.ec-modal-acoes .perigo{background:#8b2c2c;border-color:#b64a4a}.ec-modal-acoes button:last-child{background:#169447}@media(max-width:560px){.entrada-comercial-resumo{grid-template-columns:1fr 1fr}.entrada-comercial-resumo div:last-child{grid-column:1/-1}.ec-botoes,.ec-form-grid{grid-template-columns:1fr}.ec-observacao{grid-column:auto}}
'''

JS = r'''// seedcontrol-entrada-comercial-ui-v3903
(function () {
    "use strict";

    const $ = id => document.getElementById(id);
    const corpo = $("ecCorpo");
    const pesquisa = $("ecPesquisa");
    const modal = $("ecModal");
    let idEdicao = "";

    function n(v){const x=Number(v);return Number.isFinite(x)?x:0}
    function fmt(v, casas=2){return n(v).toLocaleString("pt-BR",{maximumFractionDigits:casas})}
    function esc(v){return String(v==null?"":v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;")}
    function lista(){return typeof carregarEntradasComerciais==="function"?carregarEntradasComerciais():[]}

    function registrosFiltrados(){
        const termo=String(pesquisa&&pesquisa.value||"").trim().toLowerCase();
        return lista().filter(r=>!termo||[r.dataEntrada,r.cultivar,r.lote,r.bags,r.kg,r.pms,r.germinacao,r.observacao].some(v=>String(v??"").toLowerCase().includes(termo)));
    }

    function render(){
        const todos=lista();
        const regs=registrosFiltrados();
        $("ecTotalRegistros").textContent=todos.length;
        $("ecTotalBags").textContent=fmt(todos.reduce((s,r)=>s+n(r.bags),0),2);
        $("ecTotalKg").textContent=fmt(todos.reduce((s,r)=>s+n(r.kg),0),2);
        if(!regs.length){corpo.innerHTML='<tr><td colspan="9">Nenhuma entrada comercial registrada.</td></tr>';return}
        corpo.innerHTML=regs.map(r=>`<tr data-id="${esc(r.id)}"><td>${esc(r.dataEntrada)}</td><td>${esc(r.cultivar)}</td><td>${esc(r.lote)}</td><td>${fmt(r.bags,2)}</td><td>${fmt(r.kg,3)}</td><td>${fmt(r.pms,2)}</td><td>${esc(r.germinacao||"-")}</td><td>${esc(r.observacao||"")}</td><td><button class="ec-editar" data-editar="${esc(r.id)}">✏️</button></td></tr>`).join("");
    }

    function abrir(reg){
        const r=reg||{};idEdicao=String(r.id||"");
        $("ecModalTitulo").textContent=idEdicao?"Editar entrada":"Nova entrada";
        $("ecData").value=r.dataEntrada||new Date().toLocaleDateString("pt-BR");
        $("ecCultivar").value=r.cultivar||"";$("ecLote").value=r.lote||"";$("ecKg").value=r.kg||"";$("ecPms").value=r.pms||"";$("ecBags").value=r.bags||"";$("ecGerminacao").value=r.germinacao||"";$("ecObservacao").value=r.observacao||"";
        $("ecExcluir").style.visibility=idEdicao?"visible":"hidden";modal.hidden=false;
    }
    function fechar(){modal.hidden=true;idEdicao=""}

    function salvarForm(){
        const cultivar=$("ecCultivar").value.trim(), lote=$("ecLote").value.trim();
        if(!cultivar||!lote){alert("Informe cultivar e lote.");return}
        const atual=lista();const antigo=atual.find(r=>String(r.id)===idEdicao);
        const registro={...(antigo||{}),id:idEdicao||( "EC-"+Date.now()),dataEntrada:$("ecData").value.trim(),cultivar,lote,bags:n($("ecBags").value),kg:n($("ecKg").value),pms:n($("ecPms").value),germinacao:$("ecGerminacao").value.trim(),observacao:$("ecObservacao").value.trim(),atualizadoEm:new Date().toISOString()};
        if(!registro.criadoEm)registro.criadoEm=registro.atualizadoEm;
        if(idEdicao){const i=atual.findIndex(r=>String(r.id)===idEdicao);if(i>=0)atual[i]=registro}else atual.unshift(registro);
        salvarEntradasComerciais(atual);fechar();render();
    }

    function excluir(){if(!idEdicao)return;if(!confirm("Excluir esta entrada comercial?"))return;salvarEntradasComerciais(lista().filter(r=>String(r.id)!==idEdicao));fechar();render()}

    function estimar(){
        const kg=n($("ecKg").value),pms=n($("ecPms").value);
        if(kg<=0||pms<=0){alert("Informe Kg recebidos e PMS para estimar os Bags.");return}
        const bags=typeof estimarBagsComerciaisPorKg==="function"?estimarBagsComerciaisPorKg(kg,pms):kg/(pms*5);
        $("ecBags").value=bags.toFixed(2);
    }

    async function exportar(){
        const regs=registrosFiltrados();if(!regs.length){alert("Não há entradas para exportar.");return}
        if(typeof XLSX==="undefined"){alert("Biblioteca do Excel não carregou.");return}
        const dados=[["ENTRADA DE SEMENTES SOJA"],["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)","GERMINAÇÃO (nota)","Observação"],...regs.map(r=>[r.dataEntrada||"",r.cultivar||"",r.lote||"",n(r.bags),n(r.kg),n(r.pms),r.germinacao||"",r.observacao||""])];
        const ws=XLSX.utils.aoa_to_sheet(dados);ws["!merges"]=[{s:{r:0,c:0},e:{r:0,c:7}}];ws["!cols"]=[{wch:14},{wch:25},{wch:22},{wch:10},{wch:13},{wch:11},{wch:18},{wch:31}];
        function cell(r,c){const a=XLSX.utils.encode_cell({r,c});if(!ws[a])ws[a]={t:"s",v:""};return ws[a]}
        function border(){const s={style:"thin",color:{rgb:"222222"}};return{top:s,bottom:s,left:s,right:s}}
        for(let c=0;c<8;c++)cell(0,c).s={fill:{patternType:"solid",fgColor:{rgb:"F36B21"}},font:{bold:true,sz:16,color:{rgb:"000000"}},alignment:{horizontal:"center",vertical:"center"},border:border()};
        for(let c=0;c<8;c++)cell(1,c).s={fill:{patternType:"solid",fgColor:{rgb:"B7DFCC"}},font:{bold:true,sz:10,color:{rgb:"000000"}},alignment:{horizontal:"center",vertical:"center",wrapText:true},border:border()};
        regs.forEach((_,i)=>{const r=i+2;const cor=i%2===0?"FFFFFF":"FDE3D8";for(let c=0;c<8;c++)cell(r,c).s={fill:{patternType:"solid",fgColor:{rgb:cor}},font:{bold:true,sz:9,color:{rgb:"111111"}},alignment:{horizontal:c===1||c===2||c===7?"left":"center",vertical:"center"},border:border()}});
        const wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,ws,"Entrada Comercial 2026");const nome="SeedControl_Entrada_Comercial_2026.xlsx";
        const cap=window.Capacitor;const nativo=cap&&typeof cap.isNativePlatform==="function"&&cap.isNativePlatform();
        if(nativo&&cap.Plugins&&cap.Plugins.Filesystem&&cap.Plugins.Share){const arr=XLSX.write(wb,{bookType:"xlsx",type:"array"});const bytes=new Uint8Array(arr);let bin="";for(let i=0;i<bytes.length;i+=32768)bin+=String.fromCharCode.apply(null,bytes.subarray(i,i+32768));const b64=btoa(bin);const salvo=await cap.Plugins.Filesystem.writeFile({path:"SeedControl/Planilhas/"+nome,data:b64,directory:"DOCUMENTS",recursive:true});const temp=await cap.Plugins.Filesystem.writeFile({path:"SeedControlShare/"+nome,data:b64,directory:"CACHE",recursive:true});await cap.Plugins.Share.share({title:nome,text:"Entrada Comercial 2026 - SeedControl",url:temp.uri,dialogTitle:"Compartilhar planilha"});alert("Planilha salva em Documentos/SeedControl/Planilhas.");}else XLSX.writeFile(wb,nome);
    }

    $("ecNovo").addEventListener("click",()=>abrir(null));$("ecFechar").addEventListener("click",fechar);$("ecSalvar").addEventListener("click",salvarForm);$("ecExcluir").addEventListener("click",excluir);$("ecEstimar").addEventListener("click",estimar);$("ecExportar").addEventListener("click",()=>exportar().catch(e=>alert("Não foi possível exportar: "+(e&&e.message?e.message:"erro desconhecido"))));
    pesquisa.addEventListener("input",render);corpo.addEventListener("click",e=>{const b=e.target.closest("[data-editar]");if(!b)return;const r=lista().find(x=>String(x.id)===String(b.dataset.editar));if(r)abrir(r)});modal.addEventListener("click",e=>{if(e.target===modal)fechar()});window.addEventListener("seedcontrol:entrada-comercial-atualizada",render);render();
})();
'''

(ROOT / "entrada-comercial-core-v3903.js").write_text(CORE, encoding="utf-8")
(ROOT / "entrada-comercial.html").write_text(HTML, encoding="utf-8")
(ROOT / "entrada-comercial-v3903.css").write_text(CSS, encoding="utf-8")
(ROOT / "entrada-comercial-v3903.js").write_text(JS, encoding="utf-8")


def injetar_core(path: Path):
    if not path.exists():
        return
    texto = path.read_text(encoding="utf-8")
    if "entrada-comercial-core-v3903.js" in texto:
        return
    padrao = re.compile(r'(<script[^>]+src=["\']database\.js(?:\?[^"\']*)?["\'][^>]*></script>)', re.I)
    texto_novo, qtd = padrao.subn(r'\1\n<script src="entrada-comercial-core-v3903.js?v=3903"></script>', texto, count=1)
    if qtd != 1:
        raise SystemExit(f"Não foi possível injetar core comercial em {path.name}")
    path.write_text(texto_novo, encoding="utf-8")

injetar_core(CADASTRO_HTML)
injetar_core(BACKUP_HTML)

planilha = PLANILHA_HTML.read_text(encoding="utf-8")
if "entrada-comercial.html?v=3903" not in planilha:
    ancora = '<div class="container">'
    bloco = '''<div class="container">\n\n<div class="card" style="border:1px solid rgba(74,222,128,.28);background:linear-gradient(145deg,rgba(9,48,37,.78),rgba(7,27,35,.92))">\n<h2>📥 Entrada Comercial de Sementes</h2>\n<p style="color:#aebdc2">Recebimentos de sementes de fora, com estimativa comercial baseada no PMS.</p>\n<button type="button" onclick="window.location.href='entrada-comercial.html?v=3903'">Abrir Entrada Comercial 2026</button>\n</div>'''
    if ancora not in planilha:
        raise SystemExit("Container da tela Planilha não encontrado.")
    planilha = planilha.replace(ancora, bloco, 1)
    PLANILHA_HTML.write_text(planilha, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-3903', sw, count=1)
    SW.write_text(sw, encoding="utf-8")

for nome in ("entrada-comercial-core-v3903.js", "entrada-comercial.html", "entrada-comercial-v3903.css", "entrada-comercial-v3903.js"):
    if not (ROOT / nome).exists():
        raise SystemExit(f"Falha: {nome} não foi criado.")

cad_final = CADASTRO_HTML.read_text(encoding="utf-8")
plan_final = PLANILHA_HTML.read_text(encoding="utf-8")
for trecho in ("registrarEntradaComercial3903", "estimarBagsComerciaisPorKg", "PMS × 5"):
    if trecho not in CORE and trecho not in JS:
        raise SystemExit(f"Validação comercial falhou: {trecho}")
if "entrada-comercial-core-v3903.js" not in cad_final:
    raise SystemExit("Core comercial não entrou no cadastro.html")
if "entrada-comercial.html?v=3903" not in plan_final:
    raise SystemExit("Atalho da Entrada Comercial não entrou em planilha.html")

print("Entrada Comercial 2026 preparada: integração com cadastro Comercial(PMS), edição manual, estimativa Bags por Kg/PMS, Excel fiel e espelho no backup.")
