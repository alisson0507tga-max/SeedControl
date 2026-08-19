// seedcontrol-historico-saidas-v3833
(function () {
    "use strict";

    function esc(v) {
        return String(v == null ? "" : v).replace(/[&<>"']/g, c => ({
            "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
        }[c]));
    }

    function iniciar() {
        const lista = document.getElementById("lista");
        if (!lista) return;

        if (!document.getElementById("btnRelatorioSaidas")) {
            const botao = document.createElement("button");
            botao.id = "btnRelatorioSaidas";
            botao.type = "button";
            botao.textContent = "📄 Relatório de Saídas";
            botao.style.cssText = "width:100%;margin:0 0 16px;background:#16a34a;";
            botao.addEventListener("click", () => window.location.href = "relatorio-saidas.html");
            lista.insertAdjacentElement("beforebegin", botao);
        }

        if (typeof carregarHistorico !== "function") return;
        const historico = carregarHistorico();
        if (!Array.isArray(historico)) return;

        const cards = Array.from(lista.querySelectorAll(".card"));
        historico.forEach((item, indice) => {
            if (!item || item.tipo !== "saida" || !item.destino) return;
            const card = cards[indice];
            if (!card || card.querySelector(".seed-destino-historico")) return;

            const p = document.createElement("p");
            p.className = "seed-destino-historico";
            p.innerHTML = `<strong>🚚 Destino:</strong> ${esc(item.destino)}`;

            const paragrafos = card.querySelectorAll("p");
            const obs = Array.from(paragrafos).find(el => /Observa/i.test(el.textContent || ""));
            if (obs) obs.insertAdjacentElement("beforebegin", p);
            else card.appendChild(p);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => setTimeout(iniciar, 0), { once: true });
    } else {
        setTimeout(iniciar, 0);
    }
})();
