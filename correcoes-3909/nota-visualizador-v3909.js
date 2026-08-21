// seedcontrol-nota-visualizador-robusto-v3909
(function () {
  "use strict";

  let loteAtual = null;
  let fotoAtual = "";
  let timer = 0;

  function texto(v) { return String(v == null ? "" : v).trim(); }
  function norm(v) {
    return texto(v).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ");
  }

  function carregarEstoque() {
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

  function carregarEntradas() {
    try {
      const d = JSON.parse(localStorage.getItem("seedcontrol_entrada_comercial_2026") || "[]");
      return Array.isArray(d) ? d : [];
    } catch (_) { return []; }
  }

  function carregarMapaNotas() {
    try {
      const m = JSON.parse(localStorage.getItem("seedcontrol_entrada_comercial_notas_2026") || "{}");
      return m && typeof m === "object" && !Array.isArray(m) ? m : {};
    } catch (_) { return {}; }
  }

  function campo(bloco, rotulo) {
    const txt = String(bloco && (bloco.innerText || bloco.textContent) || "");
    const rx = new RegExp(rotulo + "\\s*:?\\s*([^\\n\\r]+)", "i");
    const m = txt.match(rx);
    return m ? texto(m[1]) : "";
  }

  function loteDoBloco(bloco) {
    return campo(bloco, "(?:📋\\s*)?Lote").replace(/^[:\-\s]+/, "");
  }

  function cultivarDoBloco(bloco) {
    const h2 = bloco && bloco.querySelector("h2");
    if (h2) {
      const t = texto(h2.textContent).replace(/^\s*[🌱📋]\s*/, "");
      if (t && !/^lote\b/i.test(t)) return t;
    }
    return "";
  }

  function encontrarLote(bloco) {
    const lote = loteDoBloco(bloco);
    if (!lote) return null;
    const estoque = carregarEstoque();
    let candidatos = estoque.filter(item => norm(item && item.lote) === norm(lote));
    const cultivar = cultivarDoBloco(bloco);
    if (cultivar) {
      const porCultivar = candidatos.filter(item => norm(item && item.cultivar) === norm(cultivar));
      if (porCultivar.length) candidatos = porCultivar;
    }
    if (candidatos.length > 1) {
      const fazenda = campo(bloco, "(?:🚜\\s*)?Fazenda");
      const peneira = campo(bloco, "(?:🌾\\s*)?Peneira");
      const talhao = campo(bloco, "(?:📍\\s*)?Talh(?:a|ã)o");
      const exato = candidatos.find(item =>
        (!fazenda || norm(item && item.fazenda) === norm(fazenda)) &&
        (!peneira || norm(item && item.peneira) === norm(peneira)) &&
        (!talhao || norm(item && item.talhao) === norm(talhao))
      );
      if (exato) return exato;
    }
    return candidatos[0] || null;
  }

  function fotoAlternativa(lote) {
    if (!lote) return "";
    const mapa = carregarMapaNotas();
    const entradas = carregarEntradas();
    const porId = entradas.find(r => texto(r && r.origemLoteId) && texto(r.origemLoteId) === texto(lote.id));
    if (porId && mapa[texto(porId.id)]) return texto(mapa[texto(porId.id)]);
    const porCampos = entradas.find(r => norm(r && r.lote) === norm(lote.lote) && (!r.cultivar || norm(r.cultivar) === norm(lote.cultivar)));
    if (porCampos && mapa[texto(porCampos.id)]) return texto(mapa[texto(porCampos.id)]);
    return "";
  }

  function fotoDoLote(lote) {
    return texto(lote && lote.notaEntradaFoto) || fotoAlternativa(lote);
  }

  function instalarEstilo() {
    if (document.getElementById("seedNota3909Style")) return;
    const s = document.createElement("style");
    s.id = "seedNota3909Style";
    s.textContent = `
      .seed-nota-btn-v3909{width:100%;min-height:50px;margin:10px 0 0;padding:10px 14px;border:1px solid rgba(74,222,128,.42);border-radius:13px;background:linear-gradient(100deg,#126a35,#178b43);color:#fff;font:inherit;font-weight:750;grid-column:1/-1}
      .seed-nota-modal-v3909{position:fixed;inset:0;z-index:2147483000;display:none;flex-direction:column;background:rgba(2,8,12,.97);padding:max(14px,env(safe-area-inset-top)) 12px max(14px,env(safe-area-inset-bottom));color:#fff}
      .seed-nota-modal-v3909.ativo{display:flex}.seed-nota-top-v3909{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:4px 4px 12px}.seed-nota-top-v3909 button{min-width:44px;min-height:44px;border-radius:12px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);color:#fff;font-size:22px}
      .seed-nota-area-v3909{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:auto;border:1px solid rgba(148,163,184,.18);border-radius:16px;background:#02090d}.seed-nota-img-v3909{display:block;max-width:100%;max-height:100%;object-fit:contain;transform-origin:center;transition:transform .18s ease}.seed-nota-img-v3909.zoom{transform:scale(1.65)}
      .seed-nota-acoes-v3909{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding-top:12px}.seed-nota-acoes-v3909 button{min-height:50px;border-radius:13px;border:1px solid rgba(74,222,128,.34);background:rgba(18,112,55,.78);color:#fff;font:inherit;font-weight:700}
    `;
    document.head.appendChild(s);
  }

  function criarModal() {
    if (document.getElementById("seedNotaModal3909")) return;
    const m = document.createElement("div");
    m.id = "seedNotaModal3909";
    m.className = "seed-nota-modal-v3909";
    m.innerHTML = `<div class="seed-nota-top-v3909"><strong id="seedNotaTitulo3909">Nota de entrada</strong><button id="seedNotaFechar3909" type="button">✕</button></div><div class="seed-nota-area-v3909"><img id="seedNotaImg3909" class="seed-nota-img-v3909" alt="Nota de entrada"></div><div class="seed-nota-acoes-v3909"><button id="seedNotaZoom3909" type="button">🔍 Ampliar</button><button id="seedNotaCompartilhar3909" type="button">↗ Compartilhar</button></div>`;
    document.body.appendChild(m);
    document.getElementById("seedNotaFechar3909").addEventListener("click", fechar);
    document.getElementById("seedNotaZoom3909").addEventListener("click", function () {
      const img = document.getElementById("seedNotaImg3909");
      const z = img.classList.toggle("zoom");
      this.textContent = z ? "🔎 Normal" : "🔍 Ampliar";
    });
    document.getElementById("seedNotaCompartilhar3909").addEventListener("click", compartilhar);
  }

  function abrir(lote, foto) {
    if (!foto) return;
    loteAtual = lote;
    fotoAtual = foto;
    criarModal();
    const img = document.getElementById("seedNotaImg3909");
    img.classList.remove("zoom");
    img.src = foto;
    document.getElementById("seedNotaTitulo3909").textContent = `Nota de entrada • Lote ${texto(lote && lote.lote)}`;
    document.getElementById("seedNotaZoom3909").textContent = "🔍 Ampliar";
    document.getElementById("seedNotaModal3909").classList.add("ativo");
    document.documentElement.style.overflow = "hidden";
  }

  function fechar() {
    const m = document.getElementById("seedNotaModal3909");
    if (m) m.classList.remove("ativo");
    document.documentElement.style.overflow = "";
  }

  async function compartilhar() {
    if (!fotoAtual) return;
    const nome = `SeedControl-nota-${texto(loteAtual && loteAtual.lote).replace(/[^a-z0-9_-]+/gi,"-") || "lote"}.jpg`;
    try {
      const base64 = String(fotoAtual).split(",")[1] || "";
      const cap = window.Capacitor && window.Capacitor.Plugins;
      if (cap && cap.Filesystem && cap.Share) {
        const salvo = await cap.Filesystem.writeFile({ path:nome, data:base64, directory:"CACHE" });
        await cap.Share.share({ title:"Nota de entrada", text:`Lote ${texto(loteAtual && loteAtual.lote)}`, url:salvo.uri, dialogTitle:"Compartilhar nota" });
        return;
      }
    } catch (_) {}
    alert("A nota está disponível para visualização, mas o compartilhamento não foi disponibilizado neste aparelho.");
  }

  function candidatos() {
    const seletores = [
      "#lista .card-registro", "#lista .estoque-registro",
      "main .card", ".container .card", "article"
    ];
    const set = new Set();
    document.querySelectorAll(seletores.join(",")).forEach(el => {
      const t = texto(el.innerText || el.textContent);
      if (/\bLote\b/i.test(t) && /\bBags\b/i.test(t)) set.add(el);
    });
    return Array.from(set);
  }

  function decorar() {
    instalarEstilo();
    criarModal();
    candidatos().forEach(bloco => {
      if (bloco.querySelector(".seed-nota-btn-v3839,.seed-nota-btn-v3909")) return;
      const lote = encontrarLote(bloco);
      const foto = fotoDoLote(lote);
      if (!lote || !foto) return;
      const b = document.createElement("button");
      b.type = "button";
      b.className = "seed-nota-btn-v3909";
      b.textContent = "📄 Ver nota";
      b.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); abrir(lote, foto); });
      const alvo = Array.from(bloco.querySelectorAll("button,a")).find(x => /Movimentar Estoque|Editar/i.test(texto(x.textContent)));
      if (alvo && alvo.parentNode === bloco) bloco.insertBefore(b, alvo);
      else bloco.appendChild(b);
    });
  }

  function agendar() { clearTimeout(timer); timer = setTimeout(decorar, 60); }

  function iniciar() {
    decorar();
    new MutationObserver(agendar).observe(document.body, { childList:true, subtree:true });
    document.addEventListener("visibilitychange", () => { if (!document.hidden) decorar(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once:true });
  else iniciar();
})();
