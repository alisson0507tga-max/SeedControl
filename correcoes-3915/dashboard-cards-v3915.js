// seedcontrol-dashboard-cards-v3915
(function(){
  "use strict";
  const mapa = {
    "estoque total":"estoque",
    "kg (media)":"kg",
    "kg (média)":"kg",
    "sacas (60 kg)":"sacas",
    "cultivares":"cultivares",
    "lotes":"lotes",
    "fazendas":"fazendas"
  };
  function norm(v){
    return String(v||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/\s+/g," ").trim();
  }
  function abrir(tipo){ location.href = `detalhes-dashboard.html?tipo=${encodeURIComponent(tipo)}`; }
  function iniciar(){
    document.querySelectorAll("#dashboard .metric-card").forEach(card=>{
      const titulo = card.querySelector("h2");
      const tipo = mapa[norm(titulo && titulo.textContent)];
      if (!tipo || card.dataset.seedDetalhe3915) return;
      card.dataset.seedDetalhe3915 = tipo;
      card.setAttribute("role","button");
      card.setAttribute("tabindex","0");
      card.setAttribute("aria-label",`${titulo.textContent}. Toque para ver detalhes`);
      card.addEventListener("click",()=>abrir(tipo));
      card.addEventListener("keydown",e=>{
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); abrir(tipo); }
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded",iniciar,{once:true});
  else iniciar();
})();
