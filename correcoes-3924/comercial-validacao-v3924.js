// seedcontrol-comercial-validacao-v3924
(function () {
  "use strict";

  const MARCADOR = "__SEEDCONTROL_NAO_APLICA_COMERCIAL_3924__";
  const IDS = ["fazenda", "talhao", "talhão", "secagem", "situacaoSecagem", "situacao-secagem", "statusSecagem"];
  let temporarios = [];

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

  function ehRotuloNaoAplicavel(label) {
    const t = norm(label && label.textContent);
    return t === "fazenda" || t === "talhao" || t.includes("situacao da secagem") || t === "secagem";
  }

  function coletarCampos() {
    const set = new Set();

    IDS.forEach(id => {
      const el = document.getElementById(id);
      if (el && el.matches("input,select,textarea")) set.add(el);
    });

    document.querySelectorAll("label").forEach(label => {
      if (!ehRotuloNaoAplicavel(label)) return;
      const forId = label.getAttribute("for");
      if (forId) {
        const el = document.getElementById(forId);
        if (el && el.matches("input,select,textarea")) set.add(el);
      }
      label.querySelectorAll("input,select,textarea").forEach(el => set.add(el));
      const prox = label.nextElementSibling;
      if (prox) {
        if (prox.matches("input,select,textarea")) set.add(prox);
        else prox.querySelectorAll("input,select,textarea").forEach(el => set.add(el));
      }
    });

    return Array.from(set);
  }

  function restaurarCamposTemporarios() {
    temporarios.forEach(item => {
      try {
        item.el.value = item.valor;
        if (item.opcao && item.opcao.dataset.seed3924 === "1") item.opcao.remove();
      } catch (_) {}
    });
    temporarios = [];
  }

  function prepararCamposTemporarios() {
    if (!ehComercial()) return;
    restaurarCamposTemporarios();

    temporarios = coletarCampos().filter(el => !texto(el.value)).map(el => {
      const estado = { el, valor: el.value, opcao: null };

      if (el.tagName === "SELECT") {
        let opcao = Array.from(el.options || []).find(o => o.value === MARCADOR);
        if (!opcao) {
          opcao = document.createElement("option");
          opcao.value = MARCADOR;
          opcao.textContent = "Não se aplica (Comercial)";
          opcao.hidden = true;
          opcao.dataset.seed3924 = "1";
          el.appendChild(opcao);
        }
        estado.opcao = opcao;
        el.value = MARCADOR;
      } else {
        el.value = MARCADOR;
      }

      return estado;
    });
  }

  function limparMarcadoresDoEstoque(valor) {
    if (typeof valor !== "string" || !valor.includes(MARCADOR)) return valor;
    try {
      const lista = JSON.parse(valor);
      if (!Array.isArray(lista)) return valor;
      lista.forEach(item => {
        if (!item || typeof item !== "object") return;
        ["fazenda", "talhao", "talhão", "secagem", "situacaoSecagem", "statusSecagem"].forEach(chave => {
          if (item[chave] === MARCADOR) item[chave] = "";
        });
      });
      return JSON.stringify(lista);
    } catch (_) {
      return valor;
    }
  }

  function protegerPersistencia() {
    const atual = Storage.prototype.setItem;
    if (atual && atual.__seedComercial3924) return;

    function setItem3924(chave, valor) {
      if (this === window.localStorage && String(chave) === "estoque") {
        valor = limparMarcadoresDoEstoque(valor);
      }
      return atual.call(this, chave, valor);
    }

    setItem3924.__seedComercial3924 = true;
    setItem3924.__seedComercial3924Original = atual;
    Storage.prototype.setItem = setItem3924;
  }

  function prepararAntesDeSalvar(evento) {
    const alvo = evento.target instanceof Element ? evento.target.closest("#salvar") : null;
    if (!alvo || !ehComercial()) return;
    prepararCamposTemporarios();
    setTimeout(restaurarCamposTemporarios, 0);
  }

  function iniciar() {
    protegerPersistencia();
    document.addEventListener("click", prepararAntesDeSalvar, true);
    window.addEventListener("pagehide", restaurarCamposTemporarios);
    window.seedControlEhComercial3924 = ehComercial;
    window.SEEDCONTROL_COMERCIAL_VALIDACAO_3924 = true;
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
