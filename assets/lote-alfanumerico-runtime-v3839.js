// seedcontrol-lote-alfanumerico-runtime-v3839
(function () {
    "use strict";

    let estado = null;

    function norm(v) {
        return String(v == null ? "" : v).trim().toLowerCase();
    }

    function ehAlfanumerico(v) {
        return /[^0-9]/.test(String(v || ""));
    }

    function prepararCampo() {
        const input = document.getElementById("lote");
        if (!input) return;
        try { input.type = "text"; } catch (_) {}
        input.setAttribute("inputmode", "text");
        input.setAttribute("autocapitalize", "characters");
        input.setAttribute("autocomplete", "off");
        input.setAttribute("spellcheck", "false");
        input.setAttribute("placeholder", "Ex.: 112, AB-123 ou 24/001");
    }

    function dadosIdentidade() {
        const valor = id => {
            const el = document.getElementById(id);
            return el ? String(el.value || "").trim() : "";
        };
        return {
            cultivar: valor("cultivar"),
            lote: valor("lote"),
            fazenda: valor("fazenda"),
            peneira: valor("peneira"),
            talhao: valor("talhao")
        };
    }

    function duplicadoAlfanumerico(dados, ignorarId) {
        if (!ehAlfanumerico(dados.lote)) return false;
        if (typeof window.carregarEstoque !== "function") return false;
        const base = window.carregarEstoque();
        if (!Array.isArray(base)) return false;
        return base.some(item => {
            if (!item) return false;
            if (ignorarId != null && String(item.id) === String(ignorarId)) return false;
            return norm(item.cultivar) === norm(dados.cultivar) &&
                   norm(item.lote) === norm(dados.lote) &&
                   norm(item.fazenda) === norm(dados.fazenda) &&
                   norm(item.peneira) === norm(dados.peneira) &&
                   norm(item.talhao) === norm(dados.talhao);
        });
    }

    function corrigirLista(lista) {
        if (!estado || !Array.isArray(lista)) return lista;
        lista.forEach(item => {
            if (!item) return;
            if (String(item.lote) === String(estado.surrogate) || Number(item.lote) === Number(estado.surrogate)) {
                item.lote = estado.original;
            }
        });
        return lista;
    }

    function corrigirHistorico(lista) {
        if (!estado || !Array.isArray(lista)) return lista;
        lista.forEach(item => {
            if (!item) return;
            if (String(item.lote) === String(estado.surrogate) || Number(item.lote) === Number(estado.surrogate)) {
                item.lote = estado.original;
            }
        });
        return lista;
    }

    function instalarWrappers() {
        if (typeof window.salvarEstoque === "function" && !window.salvarEstoque.__seedLote3839) {
            const original = window.salvarEstoque;
            const wrapper = function (lista) {
                return original.call(this, corrigirLista(lista));
            };
            wrapper.__seedLote3839 = true;
            window.salvarEstoque = wrapper;
        }

        if (typeof window.salvarHistorico === "function" && !window.salvarHistorico.__seedLote3839) {
            const original = window.salvarHistorico;
            const wrapper = function (lista) {
                return original.call(this, corrigirHistorico(lista));
            };
            wrapper.__seedLote3839 = true;
            window.salvarHistorico = wrapper;
        }
    }

    function iniciarSubstituicao(evento) {
        const alvo = evento.target && evento.target.closest ? evento.target.closest("#salvar") : null;
        if (!alvo) return;

        const input = document.getElementById("lote");
        if (!input) return;

        const original = String(input.value || "").trim();
        if (!original || !ehAlfanumerico(original)) return;

        const dados = dadosIdentidade();
        const params = new URLSearchParams(location.search);
        const ignorarId = params.get("id");

        if (duplicadoAlfanumerico(dados, ignorarId)) {
            evento.preventDefault();
            evento.stopImmediatePropagation();
            alert("Este lote já está cadastrado com a mesma cultivar, fazenda, peneira e talhão.");
            return;
        }

        instalarWrappers();

        const surrogate = String(Date.now()).slice(-9) + String(Math.floor(Math.random() * 900) + 100);
        estado = { original, surrogate };
        input.value = surrogate;

        setTimeout(() => {
            input.value = original;
            estado = null;
        }, 1000);
    }

    function iniciar() {
        prepararCampo();
        instalarWrappers();
        document.addEventListener("click", iniciarSubstituicao, true);
        document.addEventListener("submit", function (evento) {
            const form = evento.target;
            if (!form || !form.querySelector || !form.querySelector("#lote")) return;
            const fake = { target: document.getElementById("salvar"), preventDefault: () => evento.preventDefault(), stopImmediatePropagation: () => evento.stopImmediatePropagation() };
            iniciarSubstituicao(fake);
        }, true);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    } else {
        iniciar();
    }
})();
