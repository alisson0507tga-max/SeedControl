// seedcontrol-entrada-comercial-ui-v3904
(function () {
    "use strict";

    const $ = id => document.getElementById(id);
    const corpo = $("ecCorpo");
    const pesquisa = $("ecPesquisa");
    const modal = $("ecModal");
    let idEdicao = "";

    function n(v) { const x = Number(String(v == null ? "" : v).replace(",", ".")); return Number.isFinite(x) ? x : 0; }
    function fmt(v, casas = 2) { return n(v).toLocaleString("pt-BR", { maximumFractionDigits: casas }); }
    function esc(v) { return String(v == null ? "" : v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;"); }
    function lista() { return typeof window.carregarEntradasComerciais3904 === "function" ? window.carregarEntradasComerciais3904() : []; }

    function registrosFiltrados() {
        const termo = String(pesquisa && pesquisa.value || "").trim().toLowerCase();
        return lista().filter(r => !termo || [r.dataEntrada,r.cultivar,r.lote,r.bags,r.kg,r.pms,r.germinacao,r.observacao].some(v => String(v ?? "").toLowerCase().includes(termo)));
    }

    function render() {
        const todos = lista();
        const regs = registrosFiltrados();
        $("ecTotalRegistros").textContent = todos.length;
        $("ecTotalBags").textContent = fmt(todos.reduce((s,r) => s + n(r.bags), 0), 2);
        $("ecTotalKg").textContent = fmt(todos.reduce((s,r) => s + n(r.kg), 0), 3);
        if (!regs.length) {
            corpo.innerHTML = '<tr><td colspan="9">Nenhuma entrada comercial registrada.</td></tr>';
            return;
        }
        corpo.innerHTML = regs.map(r => `<tr data-id="${esc(r.id)}"><td>${esc(r.dataEntrada)}</td><td>${esc(r.cultivar)}</td><td>${esc(r.lote)}</td><td>${fmt(r.bags,2)}</td><td>${fmt(r.kg,3)}</td><td>${fmt(r.pms,2)}</td><td>${esc(r.germinacao || "-")}</td><td>${esc(r.observacao || "")}</td><td><button class="ec3904-editar" data-editar="${esc(r.id)}">✏️</button></td></tr>`).join("");
    }

    function abrir(reg) {
        const r = reg || {};
        idEdicao = String(r.id || "");
        $("ecModalTitulo").textContent = idEdicao ? "Editar entrada" : "Nova entrada";
        $("ecData").value = r.dataEntrada || new Date().toLocaleDateString("pt-BR");
        $("ecCultivar").value = r.cultivar || "";
        $("ecLote").value = r.lote || "";
        $("ecKg").value = r.kg || "";
        $("ecPms").value = r.pms || "";
        $("ecBags").value = r.bags || "";
        $("ecGerminacao").value = r.germinacao || "";
        $("ecObservacao").value = r.observacao || "";
        $("ecExcluir").style.visibility = idEdicao ? "visible" : "hidden";
        modal.hidden = false;
    }

    function fechar() {
        modal.hidden = true;
        idEdicao = "";
    }

    function salvarForm() {
        const cultivar = $("ecCultivar").value.trim();
        const lote = $("ecLote").value.trim();
        if (!cultivar || !lote) {
            alert("Informe cultivar e lote.");
            return;
        }

        const atual = lista();
        const antigo = atual.find(r => String(r.id) === idEdicao);
        const registro = {
            ...(antigo || {}),
            id: idEdicao || ("EC-" + Date.now()),
            dataEntrada: $("ecData").value.trim(),
            cultivar,
            lote,
            bags: n($("ecBags").value),
            kg: n($("ecKg").value),
            pms: n($("ecPms").value),
            germinacao: $("ecGerminacao").value.trim(),
            observacao: $("ecObservacao").value.trim(),
            atualizadoEm: new Date().toISOString()
        };
        if (!registro.criadoEm) registro.criadoEm = registro.atualizadoEm;

        if (idEdicao) {
            const i = atual.findIndex(r => String(r.id) === idEdicao);
            if (i >= 0) atual[i] = registro;
        } else {
            atual.unshift(registro);
        }

        window.salvarEntradasComerciais3904(atual);
        fechar();
        render();
    }

    function excluir() {
        if (!idEdicao) return;
        if (!confirm("Excluir esta entrada comercial?")) return;
        window.salvarEntradasComerciais3904(lista().filter(r => String(r.id) !== idEdicao));
        fechar();
        render();
    }

    function estimar() {
        const kg = n($("ecKg").value);
        const pms = n($("ecPms").value);
        if (kg <= 0 || pms <= 0) {
            alert("Informe Kg recebidos e PMS para estimar os Bags.");
            return;
        }
        const bags = typeof window.estimarBagsComerciaisPorKg3904 === "function"
            ? window.estimarBagsComerciaisPorKg3904(kg, pms)
            : kg / (pms * 5);
        $("ecBags").value = bags.toFixed(2);
    }

    async function exportar() {
        const regs = registrosFiltrados();
        if (!regs.length) {
            alert("Não há entradas para exportar.");
            return;
        }
        if (typeof XLSX === "undefined") {
            alert("Biblioteca do Excel não carregou.");
            return;
        }

        const totalBags = regs.reduce((s,r) => s + n(r.bags), 0);
        const totalKg = regs.reduce((s,r) => s + n(r.kg), 0);
        const dados = [
            ["ENTRADA DE SEMENTES SOJA"],
            ["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)","GERMINAÇÃO (nota)","Observação"],
            ...regs.map(r => [r.dataEntrada || "",r.cultivar || "",r.lote || "",n(r.bags),n(r.kg),n(r.pms),r.germinacao || "",r.observacao || ""]),
            ["","","TOTAL",totalBags,totalKg,"","",""]
        ];

        const ws = XLSX.utils.aoa_to_sheet(dados);
        ws["!merges"] = [{ s:{r:0,c:0}, e:{r:0,c:7} }];
        ws["!cols"] = [{wch:14},{wch:25},{wch:22},{wch:10},{wch:13},{wch:11},{wch:18},{wch:31}];
        ws["!rows"] = [{hpt:28},{hpt:34}];

        function cell(r,c) {
            const a = XLSX.utils.encode_cell({r,c});
            if (!ws[a]) ws[a] = { t:"s", v:"" };
            return ws[a];
        }
        function borda() {
            const s = { style:"thin", color:{rgb:"222222"} };
            return { top:s,bottom:s,left:s,right:s };
        }

        for (let c=0;c<8;c++) cell(0,c).s = { fill:{patternType:"solid",fgColor:{rgb:"F36B21"}}, font:{bold:true,sz:16,color:{rgb:"000000"}}, alignment:{horizontal:"center",vertical:"center"}, border:borda() };
        for (let c=0;c<8;c++) cell(1,c).s = { fill:{patternType:"solid",fgColor:{rgb:"B7DFCC"}}, font:{bold:true,sz:10,color:{rgb:"000000"}}, alignment:{horizontal:"center",vertical:"center",wrapText:true}, border:borda() };

        regs.forEach((_,i) => {
            const r = i + 2;
            const cor = i % 2 === 0 ? "FFFFFF" : "FDE3D8";
            for (let c=0;c<8;c++) cell(r,c).s = { fill:{patternType:"solid",fgColor:{rgb:cor}}, font:{bold:true,sz:9,color:{rgb:"111111"}}, alignment:{horizontal:(c===1||c===2||c===7)?"left":"center",vertical:"center"}, border:borda() };
        });

        const linhaTotal = regs.length + 2;
        for (let c=0;c<8;c++) cell(linhaTotal,c).s = { fill:{patternType:"solid",fgColor:{rgb:"E7F4EA"}}, font:{bold:true,sz:10,color:{rgb:"111111"}}, alignment:{horizontal:"center",vertical:"center"}, border:borda() };

        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Entrada Comercial 2026");
        const nome = "SeedControl_Entrada_Comercial_2026.xlsx";

        const cap = window.Capacitor;
        const nativo = cap && typeof cap.isNativePlatform === "function" && cap.isNativePlatform();
        if (nativo && cap.Plugins && cap.Plugins.Filesystem && cap.Plugins.Share) {
            const arr = XLSX.write(wb, { bookType:"xlsx", type:"array" });
            const bytes = new Uint8Array(arr);
            let bin = "";
            for (let i=0;i<bytes.length;i+=32768) bin += String.fromCharCode.apply(null, bytes.subarray(i,i+32768));
            const b64 = btoa(bin);
            await cap.Plugins.Filesystem.writeFile({ path:"SeedControl/Planilhas/" + nome, data:b64, directory:"DOCUMENTS", recursive:true });
            const temp = await cap.Plugins.Filesystem.writeFile({ path:"SeedControlShare/" + nome, data:b64, directory:"CACHE", recursive:true });
            await cap.Plugins.Share.share({ title:nome, text:"Entrada Comercial 2026 - SeedControl", url:temp.uri, dialogTitle:"Compartilhar planilha" });
            alert("Planilha salva em Documentos/SeedControl/Planilhas.");
        } else {
            XLSX.writeFile(wb, nome);
        }
    }

    $("ecNovo").addEventListener("click", () => abrir(null));
    $("ecFechar").addEventListener("click", fechar);
    $("ecSalvar").addEventListener("click", salvarForm);
    $("ecExcluir").addEventListener("click", excluir);
    $("ecEstimar").addEventListener("click", estimar);
    $("ecExportar").addEventListener("click", () => exportar().catch(e => alert("Não foi possível exportar: " + (e && e.message ? e.message : "erro desconhecido"))));
    pesquisa.addEventListener("input", render);
    corpo.addEventListener("click", e => {
        const b = e.target.closest("[data-editar]");
        if (!b) return;
        const r = lista().find(x => String(x.id) === String(b.dataset.editar));
        if (r) abrir(r);
    });
    modal.addEventListener("click", e => { if (e.target === modal) fechar(); });
    window.addEventListener("seedcontrol:entrada-comercial-atualizada", render);
    render();
})();
