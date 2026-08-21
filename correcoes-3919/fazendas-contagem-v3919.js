// seedcontrol-fazendas-contagem-v3919
(function(){
  "use strict";

  function texto(v){ return String(v == null ? "" : v).trim(); }
  function norm(v){
    return texto(v).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/\s+/g," ").trim();
  }
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
  function indiceComercial(){
    const ids = new Set();
    const lotes = new Set();
    carregarEntradas().forEach(r=>{
      const id = texto(r && r.origemLoteId);
      if (id) ids.add(id);
      const k = chaveLote(r);
      if (k !== "|") lotes.add(k);
    });
    return {ids,lotes};
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
  function fazendaValida(v){
    const n = norm(v);
    return !!n && n !== "0" && n !== "-" && n !== "sem fazenda informada";
  }
  function contar(){
    const indice = indiceComercial();
    const nomes = new Set();
    carregarEstoque().forEach(item=>{
      if (ehComercial(item, indice)) return;
      if (!fazendaValida(item && item.fazenda)) return;
      nomes.add(norm(item.fazenda));
    });
    return nomes.size;
  }

  let ocupado = false;
  function atualizar(){
    const el = document.getElementById("fazendas");
    if (!el) return;
    const valor = String(contar());
    if (texto(el.textContent) !== valor) el.textContent = valor;
  }
  function agendar(){
    if (ocupado) return;
    ocupado = true;
    requestAnimationFrame(function(){
      atualizar();
      ocupado = false;
    });
  }
  function iniciar(){
    atualizar();
    const el = document.getElementById("fazendas");
    if (el) new MutationObserver(agendar).observe(el,{childList:true,subtree:true,characterData:true});
    window.addEventListener("focus",agendar);
    window.addEventListener("storage",agendar);
    document.addEventListener("visibilitychange",()=>{ if (!document.hidden) agendar(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded",iniciar,{once:true});
  else iniciar();
})();
