// seedcontrol-movimentacao-destino-v3833
(function () {
    "use strict";

    function criarCampoDestino() {
        const tipo = document.getElementById("tipo");
        const obs = document.getElementById("obs");
        if (!tipo || !obs) return null;

        let grupo = document.getElementById("grupoDestino");
        if (!grupo) {
            grupo = document.createElement("div");
            grupo.id = "grupoDestino";
            grupo.innerHTML = `
                <label for="destino"><b>Destino da saída</b></label>
                <input
                    id="destino"
                    type="text"
                    placeholder="Ex.: Fazenda Graciosa"
                    autocomplete="on"
                    autocorrect="on"
                    spellcheck="true"
                    autocapitalize="words"
                >
                <small style="display:block;margin:6px 0 12px;opacity:.72;line-height:1.35;">
                    Informe para onde as bags foram enviadas.
                </small>
            `;
            obs.insertAdjacentElement("beforebegin", grupo);
        }

        function atualizar() {
            grupo.style.display = tipo.value === "saida" ? "block" : "none";
        }

        tipo.addEventListener("change", atualizar);
        atualizar();
        return grupo;
    }

    function registroAtual() {
        try {
            const params = new URLSearchParams(window.location.search);
            const id = Number(params.get("id"));
            const estoque = typeof carregarEstoque === "function" ? carregarEstoque() : [];
            return estoque.find(item => Number(item.id) === id) || null;
        } catch (_) {
            return null;
        }
    }

    function iniciar() {
        const tipo = document.getElementById("tipo");
        const quantidade = document.getElementById("quantidade");
        const salvar = document.getElementById("salvar");
        const grupo = criarCampoDestino();
        const destino = document.getElementById("destino");

        if (!tipo || !quantidade || !salvar || !grupo || !destino) return;

        salvar.addEventListener("click", function (event) {
            if (tipo.value !== "saida") return;
            if (destino.value.trim()) return;

            event.preventDefault();
            event.stopImmediatePropagation();
            alert("Informe o destino da saída.");
            destino.focus();
        }, true);

        salvar.addEventListener("click", function () {
            if (tipo.value !== "saida") return;

            const qtd = Number(quantidade.value);
            if (!Number.isFinite(qtd) || qtd <= 0) return;

            const dest = destino.value.trim();
            if (!dest) return;

            const registro = registroAtual();
            if (!registro || typeof carregarHistorico !== "function" || typeof salvarHistorico !== "function") return;

            try {
                const historico = carregarHistorico();
                if (!Array.isArray(historico) || !historico.length) return;

                const item = historico[0];
                if (!item || item.tipo !== "saida") return;
                if (String(item.lote) !== String(registro.lote)) return;
                if (Number(item.quantidade) !== qtd) return;

                item.destino = dest;
                item.peneira = registro.peneira || "";
                item.fazendaOrigem = registro.fazenda || "";
                item.talhao = registro.talhao || "";
                item.cultivar = registro.cultivar || item.cultivar || "";
                item.lote = registro.lote;
                item.seedSnapshotSaida = true;

                salvarHistorico(historico);
            } catch (erro) {
                console.error("Não foi possível completar o histórico da saída:", erro);
            }
        }, false);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    } else {
        iniciar();
    }
})();
