// seedcontrol-historico-limpeza-v3836
(function () {
    "use strict";

    const CHAVE_LIXEIRA = "seedcontrol_historico_lixeira_v3836";

    function lerLixeira() {
        try {
            const bruto = localStorage.getItem(CHAVE_LIXEIRA);
            if (!bruto) return null;
            const obj = JSON.parse(bruto);
            if (!obj || !Array.isArray(obj.historico)) return null;
            return obj;
        } catch (_) {
            return null;
        }
    }

    function salvarLixeira(historico) {
        localStorage.setItem(CHAVE_LIXEIRA, JSON.stringify({
            data: new Date().toLocaleString("pt-BR"),
            historico: historico
        }));
    }

    function criarEstilo() {
        if (document.getElementById("seedHistoricoLimpezaStyle")) return;
        const style = document.createElement("style");
        style.id = "seedHistoricoLimpezaStyle";
        style.textContent = `
            #seedHistoricoLimpeza {
                margin: 0 0 16px;
                padding: 13px;
                border-radius: 15px;
                border: 1px solid rgba(248,113,113,.28);
                background: rgba(69,10,10,.20);
            }
            #seedHistoricoLimpeza .seed-hist-limpar {
                width: 100%;
                margin: 0;
                background: #991b1b !important;
            }
            #seedHistoricoLimpeza .seed-hist-restaurar {
                width: 100%;
                margin: 9px 0 0;
                background: #0f766e !important;
            }
            #seedHistoricoLimpeza small {
                display: block;
                margin-top: 8px;
                color: #b8c5ca;
                line-height: 1.35;
                text-align: center;
            }
        `;
        document.head.appendChild(style);
    }

    function iniciar() {
        if (document.getElementById("seedHistoricoLimpeza")) return;

        const lista = document.getElementById("lista");
        if (!lista || typeof carregarHistorico !== "function" || typeof salvarHistorico !== "function") return;

        criarEstilo();

        const painel = document.createElement("div");
        painel.id = "seedHistoricoLimpeza";

        const btnLimpar = document.createElement("button");
        btnLimpar.type = "button";
        btnLimpar.className = "seed-hist-limpar";
        btnLimpar.textContent = "🧹 Limpar histórico";

        const aviso = document.createElement("small");
        aviso.textContent = "Apaga somente as movimentações do Histórico. Estoque, lotes e configurações não são alterados.";

        painel.appendChild(btnLimpar);
        painel.appendChild(aviso);

        const atual = carregarHistorico();
        const lixeira = lerLixeira();

        if (Array.isArray(atual) && atual.length === 0 && lixeira && lixeira.historico.length > 0) {
            const btnRestaurar = document.createElement("button");
            btnRestaurar.type = "button";
            btnRestaurar.className = "seed-hist-restaurar";
            btnRestaurar.textContent = "↩️ Desfazer última limpeza";
            btnRestaurar.addEventListener("click", function () {
                if (!confirm("Restaurar o histórico que foi apagado na última limpeza?")) return;
                salvarHistorico(lixeira.historico);
                localStorage.removeItem(CHAVE_LIXEIRA);
                alert("Histórico restaurado. O estoque não foi alterado.");
                window.location.reload();
            });
            painel.appendChild(btnRestaurar);
        }

        btnLimpar.addEventListener("click", function () {
            const historico = carregarHistorico();

            if (!Array.isArray(historico) || historico.length === 0) {
                alert("O Histórico já está vazio.");
                return;
            }

            const primeira = confirm(
                "Limpar somente o Histórico?\n\n" +
                "Serão apagadas " + historico.length + " movimentações.\n" +
                "O ESTOQUE E OS LOTES NÃO SERÃO APAGADOS."
            );
            if (!primeira) return;

            const segunda = confirm(
                "Confirma a limpeza do Histórico?\n\n" +
                "Uma cópia temporária será guardada para permitir Desfazer."
            );
            if (!segunda) return;

            salvarLixeira(historico);
            salvarHistorico([]);
            alert("Histórico limpo. Estoque e lotes foram mantidos.");
            window.location.reload();
        });

        lista.insertAdjacentElement("beforebegin", painel);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            setTimeout(iniciar, 20);
        }, { once: true });
    } else {
        setTimeout(iniciar, 20);
    }
})();
