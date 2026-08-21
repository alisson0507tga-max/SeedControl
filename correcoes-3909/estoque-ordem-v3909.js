// seedcontrol-estoque-ordem-real-v3909
(function () {
  "use strict";

  const CHAVE = "estoque";
  let aplicando = false;
  let timer = 0;

  function texto(v) { return String(v == null ? "" : v).trim(); }
  function norm(v) {
    return texto(v).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, " ");
  }

  function carregar() {
    try {
      const d = JSON.parse(localStorage.getItem(CHAVE) || "[]");
      return Array.isArray(d) ? d : [];
    } catch (_) { return []; }
  }

  function dataMs(item) {
    const campos = [item && item.dataCadastro, item && item.criadoEm, item && item.dataCriacao, item && item.createdAt, item && item.atualizadoEm];
    for (const valor of campos) {
      if (!valor) continue;
      const ms = Date.parse(String(valor));
      if (Number.isFinite(ms)) return ms;
    }
    const id = Number(item && item.id);
    const min = Date.UTC(2020, 0, 1);
    const max = Date.now() + 31 * 86400000;
    if (Number.isFinite(id) && id >= min && id <= max) return id;
    return 0;
  }

  function carimbarNovos() {
    if (Storage.prototype.setItem.__seedOrdemReal3909) return;
    const original = Storage.prototype.setItem;
    function setItem3909(chave, valor) {
      if (this !== window.localStorage || String(chave) !== CHAVE) return original.apply(this, arguments);
      try {
        const antes = carregar();
        const depois = JSON.parse(String(valor || "[]"));
        if (Array.isArray(depois)) {
          const ids = new Set(antes.map(x => texto(x && x.id)).filter(Boolean));
          const chaves = new Set(antes.map(x => [norm(x && x.cultivar), norm(x && x.lote), norm(x && x.fazenda), norm(x && x.peneira), norm(x && x.talhao)].join("|")));
          const agora = new Date().toISOString();
          depois.forEach(item => {
            if (!item || typeof item !== "object" || item.dataCadastro) return;
            const id = texto(item.id);
            const k = [norm(item.cultivar), norm(item.lote), norm(item.fazenda), norm(item.peneira), norm(item.talhao)].join("|");
            if ((id && !ids.has(id)) || (!id && !chaves.has(k))) item.dataCadastro = agora;
          });
          return original.call(this, chave, JSON.stringify(depois));
        }
      } catch (_) {}
      return original.apply(this, arguments);
    }
    setItem3909.__seedOrdemReal3909 = true;
    Storage.prototype.setItem = setItem3909;
  }

  function campo(card, rotulo) {
    const txt = String(card && (card.innerText || card.textContent) || "");
    const rx = new RegExp(rotulo + "\\s*:?\\s*([^\\n\\r]+)", "i");
    const m = txt.match(rx);
    return m ? texto(m[1]) : "";
  }

  function cultivarCard(card) {
    const h = card && card.querySelector("h2");
    return h ? texto(h.textContent).replace(/^\s*🌱\s*/, "") : "";
  }

  function acharItem(card, estoque) {
    const lote = campo(card, "(?:📋\\s*)?Lote");
    if (!lote) return null;
    const cultivar = cultivarCard(card);
    let candidatos = estoque.map((item, indice) => ({ item, indice })).filter(x => norm(x.item && x.item.lote) === norm(lote));
    if (cultivar) {
      const porCultivar = candidatos.filter(x => norm(x.item && x.item.cultivar) === norm(cultivar));
      if (porCultivar.length) candidatos = porCultivar;
    }
    if (candidatos.length > 1) {
      const fazenda = campo(card, "(?:🚜\\s*)?Fazenda");
      const peneira = campo(card, "(?:🌾\\s*)?Peneira");
      const talhao = campo(card, "(?:📍\\s*)?Talh(?:a|ã)o");
      const exato = candidatos.find(x =>
        (!fazenda || norm(x.item && x.item.fazenda) === norm(fazenda)) &&
        (!peneira || norm(x.item && x.item.peneira) === norm(peneira)) &&
        (!talhao || norm(x.item && x.item.talhao) === norm(talhao))
      );
      if (exato) return exato;
    }
    return candidatos[0] || null;
  }

  function ordenarAgora() {
    if (aplicando) return;
    const select = document.getElementById("ordenacao");
    const lista = document.getElementById("lista");
    if (!select || !lista || select.value !== "data_desc") return;

    aplicando = true;
    try {
      const estoque = carregar();
      const cards = Array.from(lista.querySelectorAll(":scope > .card-registro, :scope > .estoque-registro"));
      if (cards.length < 2) return;
      const info = cards.map((card, pos) => {
        const achado = acharItem(card, estoque);
        const indice = achado ? achado.indice : -1;
        const ms = achado ? dataMs(achado.item) : 0;
        return { card, pos, indice, ms };
      });
      info.sort((a, b) => (b.ms - a.ms) || (b.indice - a.indice) || (a.pos - b.pos));
      info.forEach(x => lista.appendChild(x.card));
    } finally {
      aplicando = false;
    }
  }

  function agendar() {
    clearTimeout(timer);
    timer = setTimeout(ordenarAgora, 35);
  }

  function iniciar() {
    carimbarNovos();
    const select = document.getElementById("ordenacao");
    const lista = document.getElementById("lista");
    if (select) select.addEventListener("change", () => { setTimeout(ordenarAgora, 0); setTimeout(ordenarAgora, 80); });
    if (lista) new MutationObserver(() => { if (!aplicando) agendar(); }).observe(lista, { childList: true });
    setTimeout(ordenarAgora, 80);
    setTimeout(ordenarAgora, 300);
  }

  carimbarNovos();
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
