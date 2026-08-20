// seedcontrol-planilha-mobile-v3907
(function () {
    "use strict";

    let observer = null;
    let timer = 0;

    function instalarEstilo() {
        if (document.getElementById("seedPlanilhaMobile3907Style")) return;
        const style = document.createElement("style");
        style.id = "seedPlanilhaMobile3907Style";
        style.textContent = `
            .seed-planilha-scroll-v3907 {
                width: 100%;
                max-width: 100%;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                -webkit-overflow-scrolling: touch;
                overscroll-behavior-x: contain;
                touch-action: pan-x pan-y;
                padding-bottom: 7px;
            }
            .seed-planilha-scroll-v3907 table {
                width: 1120px !important;
                min-width: 1120px !important;
                max-width: none !important;
                table-layout: fixed !important;
                transform: none !important;
                zoom: 1 !important;
            }
            .seed-planilha-scroll-v3907 th,
            .seed-planilha-scroll-v3907 td {
                box-sizing: border-box !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: clip !important;
                opacity: 1 !important;
                color: #111 !important;
                font-size: 12px !important;
                line-height: 1.25 !important;
                padding: 5px 6px !important;
                vertical-align: middle !important;
            }
            .seed-planilha-scroll-v3907 th { font-weight: 800 !important; }
            .seed-planilha-dica-v3907 {
                margin: 8px 0 10px;
                color: #aebdc2;
                font-size: 12px;
                line-height: 1.35;
            }
        `;
        document.head.appendChild(style);
    }

    function ehPlanilhaPrincipal(tabela) {
        const txt = String(tabela && tabela.innerText || "").toUpperCase();
        return txt.includes("CULTIVAR") &&
               txt.includes("PENEIRA") &&
               txt.includes("LOTE") &&
               (txt.includes("BAGS") || txt.includes("QUANTIDADE"));
    }

    function prepararTabela() {
        const tabelas = Array.from(document.querySelectorAll("table"));
        tabelas.forEach(tabela => {
            if (!ehPlanilhaPrincipal(tabela)) return;
            if (tabela.parentElement && tabela.parentElement.classList.contains("seed-planilha-scroll-v3907")) return;

            const wrap = document.createElement("div");
            wrap.className = "seed-planilha-scroll-v3907";
            tabela.parentNode.insertBefore(wrap, tabela);
            wrap.appendChild(tabela);

            if (!wrap.previousElementSibling || !wrap.previousElementSibling.classList.contains("seed-planilha-dica-v3907")) {
                const dica = document.createElement("p");
                dica.className = "seed-planilha-dica-v3907";
                dica.textContent = "↔️ Arraste para os lados para visualizar todas as colunas.";
                wrap.parentNode.insertBefore(dica, wrap);
            }
        });
    }

    function reposicionarEntradaComercial() {
        const card = document.getElementById("seedcontrol-entrada-comercial-atalho-v3904");
        if (!card) return;

        const secoes = Array.from(document.querySelectorAll("main section, .container > section, section.card"));
        const exportacao = secoes.find(secao =>
            secao !== card &&
            String(secao.textContent || "").toLowerCase().includes("exportar planilha")
        );

        if (exportacao && card.nextElementSibling !== exportacao) {
            exportacao.parentNode.insertBefore(card, exportacao);
            return;
        }

        const botoes = Array.from(document.querySelectorAll("button"));
        const voltar = botoes.find(btn => String(btn.textContent || "").toLowerCase().includes("voltar ao início"));
        if (voltar && voltar.parentNode && card.compareDocumentPosition(voltar) & Node.DOCUMENT_POSITION_PRECEDING) {
            voltar.parentNode.insertBefore(card, voltar);
        }
    }

    function aplicar() {
        instalarEstilo();
        reposicionarEntradaComercial();
        prepararTabela();
    }

    function agendar() {
        clearTimeout(timer);
        timer = setTimeout(aplicar, 35);
    }

    function iniciar() {
        aplicar();
        if (!observer) {
            observer = new MutationObserver(agendar);
            observer.observe(document.documentElement, { childList:true, subtree:true });
        }
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once:true });
    else iniciar();
})();
