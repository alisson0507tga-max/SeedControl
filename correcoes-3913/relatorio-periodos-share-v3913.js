// seedcontrol-relatorio-periodos-share-v3913
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  let busy = false;

  function pad(v) { return String(v).padStart(2, "0"); }
  function hojeISO() {
    const d = new Date();
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }
  function mesISO() {
    const d = new Date();
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}`;
  }
  function anoAtual() { return String(new Date().getFullYear()); }

  function dataItem(item) {
    const s = String(item && item.data || "");
    const m = s.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})(?:,?\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?/);
    if (!m) return null;
    return new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]), Number(m[4] || 0), Number(m[5] || 0), Number(m[6] || 0));
  }

  function fimDia(d) {
    const x = new Date(d);
    x.setHours(23, 59, 59, 999);
    return x;
  }

  function intervaloAtual() {
    const modo = $("seedPeriodo3913")?.value || "dia";
    if (modo === "mes") {
      const valor = $("seedMes3913")?.value || mesISO();
      const m = valor.match(/^(\d{4})-(\d{2})$/);
      const y = m ? Number(m[1]) : new Date().getFullYear();
      const mo = m ? Number(m[2]) - 1 : new Date().getMonth();
      const ini = new Date(y, mo, 1, 0, 0, 0, 0);
      const fim = new Date(y, mo + 1, 0, 23, 59, 59, 999);
      return { modo, ini, fim, desc: `Mês ${pad(mo + 1)}/${y}`, nome: `${y}-${pad(mo + 1)}` };
    }
    if (modo === "ano") {
      let y = Number($("seedAno3913")?.value || anoAtual());
      if (!Number.isFinite(y) || y < 2000 || y > 2100) y = new Date().getFullYear();
      return {
        modo,
        ini: new Date(y, 0, 1, 0, 0, 0, 0),
        fim: new Date(y, 11, 31, 23, 59, 59, 999),
        desc: `Ano ${y}`,
        nome: String(y)
      };
    }
    const valor = $("seedDia3913")?.value || hojeISO();
    const m = valor.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    const y = m ? Number(m[1]) : new Date().getFullYear();
    const mo = m ? Number(m[2]) - 1 : new Date().getMonth();
    const da = m ? Number(m[3]) : new Date().getDate();
    const ini = new Date(y, mo, da, 0, 0, 0, 0);
    return { modo: "dia", ini, fim: fimDia(ini), desc: `Dia ${pad(da)}/${pad(mo + 1)}/${y}`, nome: `${y}-${pad(mo + 1)}-${pad(da)}` };
  }

  function saidasFiltradas() {
    const hist = typeof carregarHistorico === "function" ? carregarHistorico() : [];
    const { ini, fim } = intervaloAtual();
    return (Array.isArray(hist) ? hist : []).filter((item) => {
      if (!item || item.tipo !== "saida") return false;
      const d = dataItem(item);
      return !!d && d >= ini && d <= fim;
    });
  }

  function formatarDataInput(d) {
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }

  function sincronizarRelatorio() {
    const info = intervaloAtual();
    const periodo = $("periodo");
    const ini = $("dataInicio");
    const fim = $("dataFim");
    const cultivar = $("filtroCultivar");
    const lote = $("filtroLote");
    const destino = $("filtroDestino");
    const aplicar = $("aplicarFiltros");
    if (periodo && ini && fim && aplicar) {
      periodo.value = "personalizado";
      ini.value = formatarDataInput(info.ini);
      fim.value = formatarDataInput(info.fim);
      if (cultivar) cultivar.value = "";
      if (lote) lote.value = "";
      if (destino) destino.value = "";
      periodo.dispatchEvent(new Event("change", { bubbles: true }));
      aplicar.click();
    }
    const desc = $("periodoDescricao");
    if (desc) desc.textContent = info.desc;
    const bot = $("seedAplicar3913");
    if (bot) bot.textContent = info.modo === "dia" ? "🔎 Ver saídas do dia" : info.modo === "mes" ? "🔎 Ver saídas do mês" : "🔎 Ver saídas do ano";
  }

  function aplicarVisibilidade() {
    const modo = $("seedPeriodo3913")?.value || "dia";
    const dia = $("seedCampoDia3913");
    const mes = $("seedCampoMes3913");
    const ano = $("seedCampoAno3913");
    if (dia) dia.hidden = modo !== "dia";
    if (mes) mes.hidden = modo !== "mes";
    if (ano) ano.hidden = modo !== "ano";
  }

  function estilo() {
    if ($("seed-rel-3913-style")) return;
    const s = document.createElement("style");
    s.id = "seed-rel-3913-style";
    s.textContent = `
      .seed-rel-periodos-3913{margin:8px 0 16px;}
      .seed-rel-periodos-3913 label{display:block;margin:0 0 8px;font-weight:700;color:#e6edf0;}
      .seed-rel-periodos-3913 select,.seed-rel-periodos-3913 input{width:100%;min-height:54px;margin:0!important;}
      .seed-rel-campo-3913{margin-top:13px;}
      .seed-rel-ajuda-3913{display:block;margin-top:8px;opacity:.72;line-height:1.35;}
      #seedAplicar3913{width:100%;margin-top:14px!important;}
      .seed-share-grid-3913{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;}
      .seed-share-grid-3913 button{width:100%;margin:0!important;min-height:54px;}
      @media(max-width:430px){.seed-share-grid-3913{grid-template-columns:1fr 1fr;}}
    `;
    document.head.appendChild(s);
  }

  function montarFiltros() {
    const painel = document.querySelector(".rel-painel");
    if (!painel || $("seedPeriodo3913")) return false;
    estilo();

    const antigo3912 = document.querySelector(".seed-rel-dia-3912");
    if (antigo3912) antigo3912.style.display = "none";

    ["periodo", "dataInicio", "dataFim", "filtroCultivar", "filtroLote", "filtroDestino", "aplicarFiltros"].forEach((id) => {
      const el = $(id);
      if (el) el.style.display = "none";
      const label = document.querySelector(`label[for="${id}"]`);
      if (label) label.style.display = "none";
    });
    const datas = $("datasPersonalizadas");
    if (datas) datas.style.display = "none";

    const bloco = document.createElement("div");
    bloco.className = "seed-rel-periodos-3913";
    bloco.innerHTML = `
      <label for="seedPeriodo3913">Filtrar por</label>
      <select id="seedPeriodo3913">
        <option value="dia">Dia</option>
        <option value="mes">Mês</option>
        <option value="ano">Ano</option>
      </select>
      <div id="seedCampoDia3913" class="seed-rel-campo-3913">
        <label for="seedDia3913">Data da saída</label>
        <input id="seedDia3913" type="date">
      </div>
      <div id="seedCampoMes3913" class="seed-rel-campo-3913" hidden>
        <label for="seedMes3913">Mês</label>
        <input id="seedMes3913" type="month">
      </div>
      <div id="seedCampoAno3913" class="seed-rel-campo-3913" hidden>
        <label for="seedAno3913">Ano</label>
        <input id="seedAno3913" type="number" min="2000" max="2100" inputmode="numeric">
      </div>
      <small class="seed-rel-ajuda-3913">Escolha dia, mês ou ano para ver todas as saídas desse período.</small>
      <button id="seedAplicar3913" type="button">🔎 Ver saídas do dia</button>
    `;
    const h2 = painel.querySelector("h2");
    if (h2) h2.insertAdjacentElement("afterend", bloco);
    else painel.prepend(bloco);

    $("seedDia3913").value = hojeISO();
    $("seedMes3913").value = mesISO();
    $("seedAno3913").value = anoAtual();

    $("seedPeriodo3913").addEventListener("change", () => {
      aplicarVisibilidade();
      sincronizarRelatorio();
    });
    $("seedDia3913").addEventListener("change", sincronizarRelatorio);
    $("seedMes3913").addEventListener("change", sincronizarRelatorio);
    $("seedAno3913").addEventListener("change", sincronizarRelatorio);
    $("seedAplicar3913").addEventListener("click", sincronizarRelatorio);

    aplicarVisibilidade();
    sincronizarRelatorio();
    return true;
  }

  function esc(v) {
    return String(v == null ? "" : v);
  }

  function linhas(saidas) {
    return saidas.map((item) => [
      item.data || "", item.cultivar || "", item.peneira || "", item.lote || "",
      Number(item.quantidade) || 0, item.fazendaOrigem || "", item.talhao || "",
      item.destino || "", item.observacao || ""
    ]);
  }

  function gerarPDF(saidas) {
    const jsPDF = window.jspdf && window.jspdf.jsPDF;
    if (!jsPDF) throw new Error("Biblioteca PDF indisponível.");
    const pdf = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });
    const info = intervaloAtual();
    pdf.setFontSize(16);
    pdf.text("RELATÓRIO DE SAÍDAS - SEEDCONTROL", 14, 14);
    pdf.setFontSize(10);
    pdf.text(`${info.desc} | ${saidas.length} saídas | ${saidas.reduce((s, x) => s + (Number(x.quantidade) || 0), 0)} bags`, 14, 21);
    if (typeof pdf.autoTable !== "function") throw new Error("Tabela PDF indisponível.");
    pdf.autoTable({
      startY: 26,
      head: [["Data", "Cultivar", "Peneira", "Lote", "Bags", "Fazenda origem", "Talhão", "Destino", "Observação"]],
      body: linhas(saidas),
      styles: { fontSize: 7, cellPadding: 1.5 },
      headStyles: { fillColor: [20, 125, 54] }
    });
    return pdf.output("arraybuffer");
  }

  function gerarExcel(saidas) {
    if (!window.XLSX) throw new Error("Biblioteca Excel indisponível.");
    const info = intervaloAtual();
    const dados = [
      ["RELATÓRIO DE SAÍDAS - SEEDCONTROL"],
      [info.desc, "", "", "", `Total: ${saidas.length} saídas`, `Bags: ${saidas.reduce((s, x) => s + (Number(x.quantidade) || 0), 0)}`],
      ["Data", "Cultivar", "Peneira", "Lote", "Bags", "Fazenda origem", "Talhão", "Destino", "Observação"],
      ...linhas(saidas)
    ];
    const ws = XLSX.utils.aoa_to_sheet(dados);
    ws["!merges"] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 8 } }];
    ws["!cols"] = [{wch:21},{wch:24},{wch:12},{wch:18},{wch:9},{wch:20},{wch:12},{wch:24},{wch:32}];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Saídas");
    return XLSX.write(wb, { bookType: "xlsx", type: "array" });
  }

  function bytesBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let bin = "";
    for (let i = 0; i < bytes.length; i += 0x8000) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, Math.min(i + 0x8000, bytes.length)));
    }
    return btoa(bin);
  }

  function cancelado(erro) {
    const m = String((erro && (erro.message || erro.errorMessage)) || erro || "").toLowerCase();
    return m.includes("cancel") || m.includes("canceled") || m.includes("cancelled");
  }

  async function salvarArquivo(nome, buffer) {
    const fs = window.Capacitor?.Plugins?.Filesystem;
    if (!fs) throw new Error("Armazenamento do APK indisponível.");
    const salvo = await fs.writeFile({
      path: `SeedControl/RelatoriosSaidas/${nome}`,
      data: bytesBase64(buffer),
      directory: "DOCUMENTS",
      recursive: true
    });
    return salvo && salvo.uri;
  }

  async function compartilharArquivo(nome, buffer, formato) {
    const fs = window.Capacitor?.Plugins?.Filesystem;
    const share = window.Capacitor?.Plugins?.Share;
    if (!fs || !share) throw new Error("Compartilhamento do APK indisponível.");
    const temp = await fs.writeFile({
      path: `SeedControlShare/${nome}`,
      data: bytesBase64(buffer),
      directory: "CACHE",
      recursive: true
    });
    try {
      await share.share({
        title: `Relatório de Saídas - ${formato}`,
        text: `Relatório de Saídas - ${intervaloAtual().desc}`,
        files: [temp.uri],
        dialogTitle: `Compartilhar ${formato}`
      });
    } catch (erro) {
      if (cancelado(erro)) return false;
      throw erro;
    }
    return true;
  }

  async function executar(tipo, compartilhar) {
    if (busy) return;
    const saidas = saidasFiltradas();
    if (!saidas.length) {
      alert("Não há saídas nesse período para exportar.");
      return;
    }
    busy = true;
    try {
      const info = intervaloAtual();
      const pdf = tipo === "pdf";
      const buffer = pdf ? gerarPDF(saidas) : gerarExcel(saidas);
      const ext = pdf ? "pdf" : "xlsx";
      const nome = `SeedControl_Relatorio_Saidas_${info.nome}.${ext}`;
      if (compartilhar) {
        await compartilharArquivo(nome, buffer, pdf ? "PDF" : "Excel");
      } else {
        await salvarArquivo(nome, buffer);
        alert(`${pdf ? "PDF" : "Excel"} salvo em Documentos/SeedControl/RelatoriosSaidas.`);
      }
    } catch (erro) {
      if (!cancelado(erro)) alert(`Não foi possível ${compartilhar ? "compartilhar" : "salvar"} o relatório. ${esc(erro && erro.message || erro)}`);
    } finally {
      busy = false;
    }
  }

  function capturarBotao(id, acao) {
    const el = $(id);
    if (!el || el.dataset.seed3913) return;
    el.dataset.seed3913 = "1";
    el.addEventListener("click", (ev) => {
      ev.preventDefault();
      ev.stopImmediatePropagation();
      acao();
    }, true);
  }

  function montarAcoes() {
    const acoes = document.querySelector(".rel-acoes");
    if (!acoes || $("seedCompartilharPDF3913")) return false;
    capturarBotao("exportarPDF", () => executar("pdf", false));
    capturarBotao("exportarExcel", () => executar("excel", false));
    const antigo = $("compartilharPDF");
    if (antigo) antigo.style.display = "none";

    const grid = document.createElement("div");
    grid.className = "seed-share-grid-3913";
    grid.innerHTML = `
      <button id="seedCompartilharPDF3913" type="button">📤 Compartilhar PDF</button>
      <button id="seedCompartilharExcel3913" type="button">📤 Compartilhar Excel</button>
    `;
    acoes.appendChild(grid);
    $("seedCompartilharPDF3913").addEventListener("click", () => executar("pdf", true));
    $("seedCompartilharExcel3913").addEventListener("click", () => executar("excel", true));
    return true;
  }

  function iniciar() {
    montarFiltros();
    montarAcoes();
    let n = 0;
    const timer = setInterval(() => {
      montarFiltros();
      montarAcoes();
      if (++n > 40 || ($("seedPeriodo3913") && $("seedCompartilharExcel3913"))) clearInterval(timer);
    }, 100);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
