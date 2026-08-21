// seedcontrol-lote-texto-guard-v3911
(function () {
  "use strict";

  let pendente = null;

  const texto = (v) => String(v == null ? "" : v).trim();
  const norm = (v) => texto(v).toLocaleLowerCase("pt-BR");

  function ler(id) {
    const el = document.getElementById(id);
    return el ? texto(el.value) : "";
  }

  function capturar() {
    const lote = ler("lote");
    if (!lote) return;
    pendente = {
      lote,
      cultivar: ler("cultivar"),
      fazenda: ler("fazenda"),
      peneira: ler("peneira"),
      talhao: ler("talhao"),
      bags: ler("bags"),
      id: new URLSearchParams(location.search).get("id") || ""
    };
  }

  function escolherRegistro(lista) {
    if (!pendente || !Array.isArray(lista) || !lista.length) return null;

    if (pendente.id) {
      const porId = lista.find((item) => item && texto(item.id) === texto(pendente.id));
      if (porId) return porId;
    }

    const candidatos = lista.filter((item) => {
      if (!item) return false;
      if (pendente.cultivar && norm(item.cultivar) !== norm(pendente.cultivar)) return false;
      if (pendente.fazenda && norm(item.fazenda) !== norm(pendente.fazenda)) return false;
      if (pendente.peneira && norm(item.peneira) !== norm(pendente.peneira)) return false;
      if (pendente.talhao && norm(item.talhao) !== norm(pendente.talhao)) return false;
      if (pendente.bags && texto(item.bags) !== texto(pendente.bags)) return false;
      return true;
    });

    if (!candidatos.length) return lista[lista.length - 1] || null;
    candidatos.sort((a, b) => Number(b && b.id || 0) - Number(a && a.id || 0));
    return candidatos[0];
  }

  function protegerLista(lista) {
    if (!pendente || !Array.isArray(lista)) return lista;
    const alvo = escolherRegistro(lista);
    if (alvo) alvo.lote = pendente.lote;
    return lista;
  }

  function instalarSalvarEstoque() {
    if (typeof window.salvarEstoque !== "function") return false;
    if (window.salvarEstoque.__seedLoteTexto3911) return true;
    const original = window.salvarEstoque;
    const wrapper = function (lista) {
      return original.call(this, protegerLista(lista));
    };
    wrapper.__seedLoteTexto3911 = true;
    window.salvarEstoque = wrapper;
    return true;
  }

  function prepararCampo() {
    const input = document.getElementById("lote");
    if (!input) return;
    try { input.type = "text"; } catch (_) {}
    input.setAttribute("inputmode", "text");
    input.setAttribute("autocapitalize", "characters");
    input.setAttribute("spellcheck", "false");
  }

  function instalarCaptura() {
    document.addEventListener("pointerdown", (ev) => {
      if (ev.target && ev.target.closest && ev.target.closest("#salvar")) capturar();
    }, true);
    document.addEventListener("click", (ev) => {
      if (ev.target && ev.target.closest && ev.target.closest("#salvar")) capturar();
    }, true);
    document.addEventListener("submit", (ev) => {
      if (ev.target && ev.target.querySelector && ev.target.querySelector("#lote")) capturar();
    }, true);
  }

  function iniciar() {
    prepararCampo();
    instalarCaptura();
    instalarSalvarEstoque();
    let tentativas = 0;
    const timer = setInterval(() => {
      prepararCampo();
      if (instalarSalvarEstoque() || ++tentativas > 40) clearInterval(timer);
    }, 100);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  } else {
    iniciar();
  }
})();
