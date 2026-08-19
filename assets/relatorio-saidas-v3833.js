// seedcontrol-relatorio-saidas-v3833
(function () {
    "use strict";

    const $ = id => document.getElementById(id);
    const historico = typeof carregarHistorico === "function" ? carregarHistorico() : [];
    const saidas = Array.isArray(historico) ? historico.filter(x => x && x.tipo === "saida") : [];
    let filtradas = [];

    function normalizar(v) {
        return String(v == null ? "" : v).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    }

    function esc(v) {
        return String(v == null ? "" : v).replace(/[&<>"']/g, c => ({
            "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
        }[c]));
    }

    function dataItem(item) {
        const s = String(item.data || "");
        const m = s.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})(?:,?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?/);
        if (!m) return null;
        return new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]), Number(m[4] || 0), Number(m[5] || 0), Number(m[6] || 0));
    }

    function inicioDia(d) { const x = new Date(d); x.setHours(0,0,0,0); return x; }
    function fimDia(d) { const x = new Date(d); x.setHours(23,59,59,999); return x; }

    function intervalo() {
        const agora = new Date();
        const p = $("periodo").value;
        if (p === "todos") return [null, null, "Todo o histórico"];
        if (p === "hoje") return [inicioDia(agora), fimDia(agora), "Hoje"];
        if (p === "7dias") {
            const ini = inicioDia(agora); ini.setDate(ini.getDate() - 6);
            return [ini, fimDia(agora), "Últimos 7 dias"];
        }
        if (p === "personalizado") {
            const a = $("dataInicio").value;
            const b = $("dataFim").value;
            const ini = a ? inicioDia(new Date(a + "T12:00:00")) : null;
            const fim = b ? fimDia(new Date(b + "T12:00:00")) : null;
            return [ini, fim, "Período personalizado"];
        }
        return [new Date(agora.getFullYear(), agora.getMonth(), 1), fimDia(agora), "Mês atual"];
    }

    function aplicar() {
        const [ini, fim, descricao] = intervalo();
        const cultivar = normalizar($("filtroCultivar").value);
        const lote = normalizar($("filtroLote").value);
        const destino = normalizar($("filtroDestino").value);

        filtradas = saidas.filter(item => {
            const d = dataItem(item);
            if (ini && (!d || d < ini)) return false;
            if (fim && (!d || d > fim)) return false;
            if (cultivar && !normalizar(item.cultivar).includes(cultivar)) return false;
            if (lote && normalizar(item.lote) !== lote) return false;
            if (destino && !normalizar(item.destino).includes(destino)) return false;
            return true;
        });

        $("totalSaidas").textContent = String(filtradas.length);
        $("totalBagsSaidas").textContent = String(filtradas.reduce((s, x) => s + (Number(x.quantidade) || 0), 0));
        $("periodoDescricao").textContent = descricao;

        const lista = $("listaSaidas");
        if (!filtradas.length) {
            lista.innerHTML = '<div class="rel-vazio">Nenhuma saída encontrada para os filtros selecionados.</div>';
            return;
        }

        lista.innerHTML = filtradas.map(item => `
            <article class="rel-saida-card">
                <h3>📦 ${esc(item.quantidade)} bags — Lote ${esc(item.lote)}</h3>
                <div class="rel-saida-grid">
                    <p><strong>📅 Data</strong>${esc(item.data)}</p>
                    <p><strong>🌱 Cultivar</strong>${esc(item.cultivar)}</p>
                    <p><strong>🌾 Peneira</strong>${esc(item.peneira || "-")}</p>
                    <p><strong>🚜 Fazenda origem</strong>${esc(item.fazendaOrigem || "-")}</p>
                    <p><strong>📍 Talhão</strong>${esc(item.talhao || "-")}</p>
                    <p class="rel-saida-destino"><strong>🚚 Destino</strong>${esc(item.destino || "Não informado")}</p>
                    <p class="rel-saida-destino"><strong>📝 Observação</strong>${esc(item.observacao || "-")}</p>
                </div>
            </article>
        `).join("");
    }

    function linhasExportacao() {
        return filtradas.map(item => [
            item.data || "", item.cultivar || "", item.peneira || "", item.lote || "",
            Number(item.quantidade) || 0, item.fazendaOrigem || "", item.talhao || "",
            item.destino || "", item.observacao || ""
        ]);
    }

    function gerarPdfArrayBuffer() {
        const jsPDF = window.jspdf && window.jspdf.jsPDF;
        if (!jsPDF) throw new Error("Biblioteca PDF indisponível.");
        const pdf = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });
        pdf.setFontSize(16); pdf.text("RELATÓRIO DE SAÍDAS - SEEDCONTROL", 14, 14);
        pdf.setFontSize(10); pdf.text(`Total: ${filtradas.length} saídas / ${filtradas.reduce((s,x)=>s+(Number(x.quantidade)||0),0)} bags`, 14, 21);
        if (typeof pdf.autoTable !== "function") throw new Error("Tabela PDF indisponível.");
        pdf.autoTable({
            startY: 26,
            head: [["Data","Cultivar","Peneira","Lote","Bags","Fazenda origem","Talhão","Destino","Observação"]],
            body: linhasExportacao(),
            styles: { fontSize: 7, cellPadding: 1.5 },
            headStyles: { fillColor: [20,125,54] }
        });
        return pdf.output("arraybuffer");
    }

    function bytesBase64(buffer) {
        const bytes = new Uint8Array(buffer); let bin = "";
        for (let i=0; i<bytes.length; i+=0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, Math.min(i+0x8000, bytes.length)));
        return btoa(bin);
    }

    async function salvarCompartilhar(nome, buffer, compartilhar) {
        const cap = window.Capacitor;
        const fs = cap && cap.Plugins && cap.Plugins.Filesystem;
        const share = cap && cap.Plugins && cap.Plugins.Share;
        if (!fs) return false;
        const base64 = bytesBase64(buffer);
        const salvo = await fs.writeFile({ path: "SeedControl/RelatoriosSaidas/" + nome, data: base64, directory: "DOCUMENTS", recursive: true });
        if (compartilhar && share) {
            const temp = await fs.writeFile({ path: "SeedControlShare/" + nome, data: base64, directory: "CACHE", recursive: true });
            await share.share({ title: nome, text: "Relatório de Saídas - SeedControl", url: temp.uri, dialogTitle: "Compartilhar relatório" });
        }
        return Boolean(salvo && salvo.uri);
    }

    async function pdf(compartilhar) {
        if (!filtradas.length) return alert("Não há saídas para exportar.");
        try {
            const buffer = gerarPdfArrayBuffer();
            const nome = `SeedControl_Relatorio_Saidas_${new Date().toISOString().slice(0,10)}.pdf`;
            const salvo = await salvarCompartilhar(nome, buffer, compartilhar);
            if (!salvo) {
                const jsPDF = window.jspdf && window.jspdf.jsPDF;
                const p = new jsPDF({ orientation:"landscape", unit:"mm", format:"a4" });
                p.text("Use o APK para salvar este relatório.", 14, 14);
                p.save(nome);
            }
        } catch (e) { alert("Não foi possível gerar o PDF. " + (e.message || e)); }
    }

    async function excel() {
        if (!filtradas.length) return alert("Não há saídas para exportar.");
        try {
            if (!window.XLSX) throw new Error("Biblioteca Excel indisponível.");
            const dados = [["RELATÓRIO DE SAÍDAS - SEEDCONTROL"], ["Data","Cultivar","Peneira","Lote","Bags","Fazenda origem","Talhão","Destino","Observação"], ...linhasExportacao()];
            const ws = XLSX.utils.aoa_to_sheet(dados);
            ws["!merges"] = [{ s:{r:0,c:0}, e:{r:0,c:8} }];
            ws["!cols"] = [{wch:21},{wch:24},{wch:10},{wch:9},{wch:9},{wch:20},{wch:12},{wch:24},{wch:30}];
            const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, "Saídas");
            const arr = XLSX.write(wb, { bookType:"xlsx", type:"array" });
            const nome = `SeedControl_Relatorio_Saidas_${new Date().toISOString().slice(0,10)}.xlsx`;
            const salvo = await salvarCompartilhar(nome, arr, false);
            if (!salvo) XLSX.writeFile(wb, nome);
        } catch (e) { alert("Não foi possível gerar o Excel. " + (e.message || e)); }
    }

    $("periodo").addEventListener("change", function () {
        $("datasPersonalizadas").hidden = this.value !== "personalizado";
    });
    $("aplicarFiltros").addEventListener("click", aplicar);
    $("exportarPDF").addEventListener("click", () => pdf(false));
    $("compartilharPDF").addEventListener("click", () => pdf(true));
    $("exportarExcel").addEventListener("click", excel);
    aplicar();
})();
