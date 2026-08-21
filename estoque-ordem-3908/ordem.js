// seedcontrol-estoque-ordem-recente-v3908
(function () {
    "use strict";

    const CHAVE_ESTOQUE = "estoque";
    const LIMITE_INFERIOR_ID = Date.UTC(2020, 0, 1);
    const LIMITE_FUTURO = 366 * 24 * 60 * 60 * 1000;

    function texto(v) {
        return String(v == null ? "" : v).trim();
    }

    function normalizar(v) {
        return texto(v).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    }

    function chave(item) {
        if (!item || typeof item !== "object") return "";
        if (texto(item.id)) return "id:" + texto(item.id);
        return [item.cultivar, item.lote, item.fazenda, item.peneira, item.talhao]
            .map(normalizar)
            .join("|");
    }

    function lerEstoque() {
        try {
            const dados = JSON.parse(localStorage.getItem(CHAVE_ESTOQUE) || "[]");
            return Array.isArray(dados) ? dados : [];
        } catch (_) {
            return [];
        }
    }

    function isoPeloId(item) {
        const id = Number(item && item.id);
        const agora = Date.now();
        if (!Number.isFinite(id)) return "";
        if (id < LIMITE_INFERIOR_ID || id > agora + LIMITE_FUTURO) return "";
        const d = new Date(id);
        return Number.isFinite(d.getTime()) ? d.toISOString() : "";
    }

    function corrigirRegistrosSemData() {
        const lista = lerEstoque();
        let alterou = false;

        lista.forEach(function (item) {
            if (!item || typeof item !== "object") return;
            if (texto(item.dataCadastro)) return;
            const iso = isoPeloId(item);
            if (!iso) return;
            item.dataCadastro = iso;
            alterou = true;
        });

        if (alterou) {
            try {
                localStorage.setItem(CHAVE_ESTOQUE, JSON.stringify(lista));
            } catch (_) {}
        }
        return alterou;
    }

    function instalarCarimboNovos() {
        if (Storage.prototype.setItem.__seedOrdem3908) return;

        const original = Storage.prototype.setItem;

        function setItem3908(chaveStorage, valor) {
            if (this !== window.localStorage || String(chaveStorage) !== CHAVE_ESTOQUE) {
                return original.apply(this, arguments);
            }

            try {
                const antesRaw = window.localStorage.getItem(CHAVE_ESTOQUE);
                const antes = antesRaw ? JSON.parse(antesRaw) : [];
                const depois = JSON.parse(String(valor || "[]"));

                if (Array.isArray(depois)) {
                    const existentes = new Set((Array.isArray(antes) ? antes : []).map(chave));
                    const agoraISO = new Date().toISOString();

                    depois.forEach(function (item) {
                        if (!item || typeof item !== "object") return;
                        const ehNovo = !existentes.has(chave(item));
                        if (ehNovo && !texto(item.dataCadastro)) {
                            item.dataCadastro = agoraISO;
                        }
                    });

                    return original.call(this, chaveStorage, JSON.stringify(depois));
                }
            } catch (_) {}

            return original.apply(this, arguments);
        }

        setItem3908.__seedOrdem3908 = true;
        Storage.prototype.setItem = setItem3908;
    }

    function forcarOrdenacaoMaisRecentes() {
        const select = document.getElementById("ordenacao");
        if (!select || select.value !== "data_desc") return;

        try {
            select.dispatchEvent(new Event("change", { bubbles: true }));
        } catch (_) {}
    }

    instalarCarimboNovos();
    const corrigiu = corrigirRegistrosSemData();

    function iniciarTela() {
        if (corrigiu) {
            requestAnimationFrame(function () {
                requestAnimationFrame(forcarOrdenacaoMaisRecentes);
            });
        } else {
            forcarOrdenacaoMaisRecentes();
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarTela, { once: true });
    } else {
        iniciarTela();
    }

    window.addEventListener("storage", function (event) {
        if (event && event.key === CHAVE_ESTOQUE) {
            setTimeout(forcarOrdenacaoMaisRecentes, 30);
        }
    });
})();
