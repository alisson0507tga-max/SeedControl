// seedcontrol-relatorio-dia-v3912
(function () {
  "use strict";

  const $ = id => document.getElementById(id);

  function dataHojeLocal() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const dia = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${dia}`;
  }

  function formatarBR(v) {
    const m = String(v || "").match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return m ? `${m[3]}/${m[2]}/${m[1]}` : String(v || "");
  }

  function esconderCampo(id) {
    const el = $(id);
    if (!el) return;
    const label = document.querySelector(`label[for="${id}"]`);
    if (label) label.style.display = "none";
    if (el.parentElement && el.parentElement.parentElement && el.parentElement.parentElement.classList.contains("rel-grid-2")) {
      el.parentElement.style.display = "none";
    } else {
      el.style.display = "none";
    }
  }

  function esconderAntigos() {
    esconderCampo("periodo");
    esconderCampo("filtroCultivar");
    esconderCampo("filtroLote");
    esconderCampo("filtroDestino");
    const datas = $("datasPersonalizadas");
    if (datas) datas.style.display = "none";
    document.querySelectorAll(".rel-grid-2").forEach(grid => {
      const visiveis = Array.from(grid.children).some(c => getComputedStyle(c).display !== "none");
      if (!visiveis) grid.style.display = "none";
    });
  }

  function estilo() {
    if ($("seed-rel-dia-style-3912")) return;
    const s = document.createElement("style");
    s.id = "seed-rel-dia-style-3912";
    s.textContent = `
      .seed-rel-dia-3912{margin:8px 0 15px;}
      .seed-rel-dia-3912 label{display:block;margin-bottom:8px;font-weight:700;color:#e6edf0;}
      .seed-rel-dia-linha-3912{display:grid;grid-template-columns:1fr auto;gap:9px;align-items:end;}
      .seed-rel-dia-linha-3912 input{width:100%;min-height:54px;margin:0!important;}
      .seed-rel-hoje-3912{width:auto!important;min-height:54px!important;padding:0 16px!important;margin:0!important;border-radius:12px!important;white-space:nowrap;}
      #seedAplicarDia3912{width:100%;margin-top:12px!important;}
      .seed-rel-dia-ajuda-3912{display:block;margin-top:7px;opacity:.72;line-height:1.35;}
    `;
    document.head.appendChild(s);
  }

  function sincronizarEAplicar() {
    const data = $("seedDataSaida3912");
    const periodo = $("periodo");
    const ini = $("dataInicio");
    const fim = $("dataFim");
    const cultivar = $("filtroCultivar");
    const lote = $("filtroLote");
    const destino = $("filtroDestino");
    const aplicar = $("aplicarFiltros");
    if (!data || !periodo || !ini || !fim || !aplicar) return;

    if (!data.value) data.value = dataHojeLocal();
    periodo.value = "personalizado";
    ini.value = data.value;
    fim.value = data.value;
    if (cultivar) cultivar.value = "";
    if (lote) lote.value = "";
    if (destino) destino.value = "";
    periodo.dispatchEvent(new Event("change", { bubbles: true }));
    aplicar.click();

    const desc = $("periodoDescricao");
    if (desc) desc.textContent = `Dia ${formatarBR(data.value)}`;
  }

  function montarFiltro() {
    const painel = document.querySelector(".rel-painel");
    const aplicarAntigo = $("aplicarFiltros");
    if (!painel || !aplicarAntigo || $("seedDataSaida3912")) return false;

    estilo();
    esconderAntigos();
    aplicarAntigo.style.display = "none";

    const bloco = document.createElement("div");
    bloco.className = "seed-rel-dia-3912";
    bloco.innerHTML = `
      <label for="seedDataSaida3912">Data da saída</label>
      <div class="seed-rel-dia-linha-3912">
        <input id="seedDataSaida3912" type="date">
        <button id="seedHoje3912" class="seed-rel-hoje-3912" type="button">Hoje</button>
      </div>
      <small class="seed-rel-dia-ajuda-3912">Escolha o dia para ver todas as saídas registradas nessa data.</small>
      <button id="seedAplicarDia3912" type="button">🔎 Ver saídas do dia</button>
    `;

    const h2 = painel.querySelector("h2");
    if (h2) h2.insertAdjacentElement("afterend", bloco);
    else painel.insertAdjacentElement("afterbegin", bloco);

    $("seedDataSaida3912").value = dataHojeLocal();
    $("seedHoje3912").addEventListener("click", () => {
      $("seedDataSaida3912").value = dataHojeLocal();
      sincronizarEAplicar();
    });
    $("seedAplicarDia3912").addEventListener("click", sincronizarEAplicar);
    $("seedDataSaida3912").addEventListener("change", sincronizarEAplicar);
    sincronizarEAplicar();
    return true;
  }

  function iniciar() {
    if (montarFiltro()) return;
    let tentativas = 0;
    const timer = setInterval(() => {
      if (montarFiltro() || ++tentativas > 40) clearInterval(timer);
    }, 100);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
