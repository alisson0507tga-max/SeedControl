// seedcontrol-dashboard-comerciais-v3918
(function(){
  "use strict";

  function texto(v){ return String(v == null ? "" : v).trim(); }
  function norm(v){
    return texto(v).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/\s+/g," ");
  }
  function numero(v){
    if (v === null || v === undefined || v === "") return 0;
    if (typeof v === "string") v = v.replace(/\./g,"").replace(",",".");
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }
  function bags(item){ return numero(item && (item.bags != null ? item.bags : item.quantidade)); }
  function carregarEstoque(){
    try {
      if (typeof window.carregarEstoque === "function") {
        const d = window.carregarEstoque();
        if (Array.isArray(d)) return d;
      }
    } catch (_) {}
    try {
      const d = JSON.parse(localStorage.getItem("estoque") || "[]");
      return Array.isArray(d) ? d : [];
    } catch (_) { return []; }
  }
  function carregarEntradas(){
    try {
      const d = JSON.parse(localStorage.getItem("seedcontrol_entrada_comercial_2026") || "[]");
      return Array.isArray(d) ? d : [];
    } catch (_) { return []; }
  }
  function chaveLote(item){ return `${norm(item && item.cultivar)}|${norm(item && item.lote)}`; }
  function criarIndiceEntradas(){
    const ids = new Set();
    const lotes = new Set();
    carregarEntradas().forEach(r => {
      const id = texto(r && r.origemLoteId);
      if (id) ids.add(id);
      const k = chaveLote(r);
      if (k !== "|") lotes.add(k);
    });
    return { ids, lotes };
  }
  function ehComercial(item, indice){
    if (!item) return false;
    const modo = norm([
      item.metodoPeso,
      item.metodo,
      item.tipoPeso,
      item.modoCalculo,
      item.tipoCalculo,
      item.origemTipo,
      item.categoria
    ].filter(Boolean).join(" "));
    if (modo.includes("comercial") || modo === "pms" || modo.includes(" pms")) return true;
    const id = texto(item.id);
    if (id && indice.ids.has(id)) return true;
    return indice.lotes.has(chaveLote(item));
  }
  function fmt(v,max=0){
    return new Intl.NumberFormat("pt-BR",{maximumFractionDigits:max}).format(numero(v));
  }

  function calcular(){
    const indice = criarIndiceEntradas();
    const lista = carregarEstoque().filter(item => ehComercial(item, indice));
    return {
      lotes: lista.length,
      bags: lista.reduce((s,item)=>s+bags(item),0)
    };
  }

  function instalarEstilo(){
    if (document.getElementById("seedComercialCardStyle3918")) return;
    const s = document.createElement("style");
    s.id = "seedComercialCardStyle3918";
    s.textContent = `
      .seed-comercial-card-v3918 .metric-copy h1{line-height:1.04!important}
      .seed-comercial-card-v3918 .seed-comercial-lotes-v3918{display:block;margin-top:6px;color:#b8c5ca;font-size:13px;font-weight:650;line-height:1.1}
    `;
    document.head.appendChild(s);
  }

  function atualizarValor(card){
    if (!card) return;
    const valor = card.querySelector("#estoqueKgTotal");
    if (!valor) return;
    const r = calcular();
    const esperado = `${fmt(r.bags,2)} Bags`;
    if (valor.dataset.seedValor3918 !== esperado || !valor.querySelector(".seed-comercial-lotes-v3918")) {
      valor.dataset.seedValor3918 = esperado;
      valor.innerHTML = `${esperado}<span class="seed-comercial-lotes-v3918">${r.lotes} lote${r.lotes===1?"":"s"}</span>`;
    }
  }

  function transformar(){
    instalarEstilo();
    const valorAtual = document.getElementById("estoqueKgTotal");
    const antigo = valorAtual && valorAtual.closest(".metric-card");
    if (!antigo) return;

    let card = antigo;
    if (!card.classList.contains("seed-comercial-card-v3918")) {
      // Clona para remover o clique antigo de Kg instalado pela 3915.
      const novo = card.cloneNode(true);
      card.replaceWith(novo);
      card = novo;
      card.classList.add("seed-comercial-card-v3918");
      const icon = card.querySelector(".metric-icon");
      const titulo = card.querySelector("h2");
      if (icon) icon.textContent = "🚚";
      if (titulo) titulo.textContent = "Sementes Comerciais";
      card.dataset.seedDetalhe3915 = "comerciais";
      card.setAttribute("role","button");
      card.setAttribute("tabindex","0");
      card.setAttribute("aria-label","Sementes Comerciais. Toque para ver detalhes");
      const abrir = () => { location.href = "detalhes-dashboard.html?tipo=comerciais"; };
      card.addEventListener("click", abrir);
      card.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); abrir(); }
      });
    }

    atualizarValor(card);

    const valor = card.querySelector("#estoqueKgTotal");
    if (valor && !valor.dataset.seedObserver3918) {
      valor.dataset.seedObserver3918 = "1";
      let ocupado = false;
      new MutationObserver(function(){
        if (ocupado) return;
        ocupado = true;
        requestAnimationFrame(function(){ atualizarValor(card); ocupado = false; });
      }).observe(valor,{childList:true,subtree:true,characterData:true});
    }
  }

  function iniciar(){
    transformar();
    window.addEventListener("focus",transformar);
    window.addEventListener("storage",transformar);
    document.addEventListener("visibilitychange",()=>{ if (!document.hidden) transformar(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded",iniciar,{once:true});
  else iniciar();
})();
