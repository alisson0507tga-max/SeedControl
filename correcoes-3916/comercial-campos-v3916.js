// seedcontrol-comercial-campos-v3916
(function () {
  "use strict";

  const CLASSE = "seed-comercial-oculto-v3916";
  let timer = 0;

  function texto(v) {
    return String(v == null ? "" : v).trim();
  }

  function norm(v) {
    return texto(v)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, " ");
  }

  function metodo() {
    return document.getElementById("metodoPeso") ||
      document.querySelector('[name="metodoPeso"]') ||
      document.querySelector('select[id*="metodo" i],select[name*="metodo" i]');
  }

  function ehComercial() {
    const el = metodo();
    if (!el) return false;
    const opcao = el.selectedOptions && el.selectedOptions[0] ? el.selectedOptions[0].textContent : "";
    const t = norm(`${el.value || ""} ${opcao || ""}`);
    return t.includes("comercial") || t.includes("5 milhoes") || t === "pms" || t.includes(" pms");
  }

  function guardarRequired(el) {
    if (!el || !(el instanceof HTMLElement)) return;
    if (!el.dataset.seed3916Required) {
      el.dataset.seed3916Required = el.required ? "1" : "0";
    }
  }

  function aplicarRequired(el, oculto) {
    if (!el || !(el instanceof HTMLElement) || !("required" in el)) return;
    guardarRequired(el);
    if (oculto) el.required = false;
    else el.required = el.dataset.seed3916Required === "1";
  }

  function adicionarAlvo(set, el) {
    if (!el || !(el instanceof HTMLElement)) return;
    set.add(el);
    if (el.matches("input,select,textarea")) return;
    el.querySelectorAll("input,select,textarea").forEach(c => set.add(c));
  }

  function alvosPorId(set) {
    ["fazenda", "talhao", "talhão", "secagem", "situacaoSecagem", "situacao-secagem", "statusSecagem"].forEach(id => {
      const campo = document.getElementById(id);
      if (!campo) return;
      adicionarAlvo(set, campo);
      const label = campo.labels && campo.labels[0] ? campo.labels[0] : document.querySelector(`label[for="${CSS.escape(id)}"]`);
      if (label) adicionarAlvo(set, label);
    });
  }

  function rotuloAlvo(label) {
    const t = norm(label && label.textContent);
    return t === "fazenda" || t === "talhao" || t.includes("situacao da secagem") || t === "secagem";
  }

  function alvosPorRotulo(set) {
    document.querySelectorAll("label").forEach(label => {
      if (!rotuloAlvo(label)) return;
      adicionarAlvo(set, label);

      const forId = label.getAttribute("for");
      if (forId) adicionarAlvo(set, document.getElementById(forId));

      const dentro = label.querySelector("input,select,textarea");
      if (dentro) adicionarAlvo(set, dentro);

      let prox = label.nextElementSibling;
      if (prox) {
        if (prox.matches("input,select,textarea")) adicionarAlvo(set, prox);
        else {
          const controles = prox.querySelectorAll("input,select,textarea");
          if (controles.length === 1 && !prox.querySelector("label")) adicionarAlvo(set, prox);
        }
      }
    });
  }

  function coletarAlvos() {
    const set = new Set();
    alvosPorId(set);
    alvosPorRotulo(set);
    return Array.from(set);
  }

  function atualizar() {
    const comercial = ehComercial();
    const alvos = coletarAlvos();

    alvos.forEach(el => {
      el.classList.toggle(CLASSE, comercial);
      if (el.matches("input,select,textarea")) {
        aplicarRequired(el, comercial);
        el.setAttribute("aria-hidden", comercial ? "true" : "false");
      }
    });

    document.body.classList.toggle("seed-modo-comercial-v3916", comercial);
  }

  function instalarEstilo() {
    if (document.getElementById("seedComercialCamposStyle3916")) return;
    const s = document.createElement("style");
    s.id = "seedComercialCamposStyle3916";
    s.textContent = `.${CLASSE}{display:none!important}`;
    document.head.appendChild(s);
  }

  function agendar() {
    clearTimeout(timer);
    timer = setTimeout(atualizar, 30);
  }

  function iniciar() {
    instalarEstilo();
    document.addEventListener("change", function (e) {
      const m = metodo();
      if (m && e.target === m) atualizar();
    });
    new MutationObserver(agendar).observe(document.body, { childList: true, subtree: true });
    atualizar();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
