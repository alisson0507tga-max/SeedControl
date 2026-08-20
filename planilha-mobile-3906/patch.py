from pathlib import Path

HTML = Path("native/www/planilha.html")

if not HTML.exists():
    raise SystemExit("planilha.html nao encontrado")

html = HTML.read_text(encoding="utf-8")

# 1) Reposiciona a Entrada Comercial para antes da area Exportar Planilha.
marcador = 'id="seedcontrol-entrada-comercial-atalho-v3904"'
pos = html.find(marcador)
if pos >= 0:
    inicio = html.rfind("<section", 0, pos)
    fim = html.find("</section>", pos)
    if inicio >= 0 and fim >= 0:
        fim += len("</section>")
        bloco = html[inicio:fim]
        html_sem = html[:inicio] + html[fim:]

        alvo_texto = html_sem.find("Exportar Planilha")
        alvo = html_sem.rfind("<section", 0, alvo_texto) if alvo_texto >= 0 else -1

        if alvo < 0:
            voltar = html_sem.find("Voltar ao Início")
            alvo = html_sem.rfind("<button", 0, voltar) if voltar >= 0 else -1

        if alvo < 0:
            alvo = html_sem.find("</main>")

        if alvo >= 0:
            html = html_sem[:alvo] + bloco + "\n\n" + html_sem[alvo:]
        else:
            html = html_sem + "\n" + bloco

# 2) Injeta tratamento mobile da pre-visualizacao da planilha.
if "seedcontrol-planilha-mobile-v3906" not in html:
    extra = r'''
<style id="seedcontrol-planilha-mobile-v3906">
/* Mantem a planilha legivel no celular: nao espreme 12 colunas. */
.seed-planilha-scroll-v3906 {
    width: 100%;
    max-width: 100%;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior-x: contain;
    touch-action: pan-x pan-y;
    padding-bottom: 6px;
}

.seed-planilha-scroll-v3906 table {
    width: 1120px !important;
    min-width: 1120px !important;
    max-width: none !important;
    table-layout: fixed !important;
    transform: none !important;
    zoom: 1 !important;
}

.seed-planilha-scroll-v3906 th,
.seed-planilha-scroll-v3906 td {
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

.seed-planilha-scroll-v3906 th {
    font-weight: 800 !important;
}

.seed-planilha-scroll-v3906::after {
    content: "Deslize para os lados para ver todas as colunas →";
    display: block;
    position: sticky;
    left: 0;
    width: max-content;
    max-width: calc(100vw - 70px);
    margin: 8px 4px 0;
    padding: 6px 9px;
    border-radius: 9px;
    background: rgba(6, 31, 39, .86);
    color: #a9bac0;
    font-size: 11px;
}
</style>
<script>
// seedcontrol-planilha-mobile-v3906
(function () {
    "use strict";

    function ehPlanilhaPrincipal(tabela) {
        var txt = String(tabela && tabela.innerText || "").toUpperCase();
        return txt.includes("CULTIVAR") &&
               txt.includes("PENEIRA") &&
               txt.includes("LOTE") &&
               (txt.includes("BAGS") || txt.includes("QUANTIDADE"));
    }

    function preparar() {
        var tabelas = Array.from(document.querySelectorAll("table"));
        tabelas.forEach(function (tabela) {
            if (!ehPlanilhaPrincipal(tabela)) return;
            if (tabela.parentElement && tabela.parentElement.classList.contains("seed-planilha-scroll-v3906")) return;

            var wrap = document.createElement("div");
            wrap.className = "seed-planilha-scroll-v3906";
            tabela.parentNode.insertBefore(wrap, tabela);
            wrap.appendChild(tabela);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", preparar, { once: true });
    } else {
        preparar();
    }

    var timer = 0;
    new MutationObserver(function () {
        clearTimeout(timer);
        timer = setTimeout(preparar, 30);
    }).observe(document.documentElement, { childList: true, subtree: true });
})();
</script>
'''
    if "</body>" in html:
        html = html.replace("</body>", extra + "\n</body>", 1)
    else:
        html += "\n" + extra

HTML.write_text(html, encoding="utf-8")

final = HTML.read_text(encoding="utf-8")
if "seedcontrol-planilha-mobile-v3906" not in final:
    raise SystemExit("Patch mobile 3906 nao entrou")
if "seed-planilha-scroll-v3906" not in final:
    raise SystemExit("Rolagem horizontal 3906 nao entrou")
if marcador in final:
    pos_card = final.find(marcador)
    pos_export = final.find("Exportar Planilha")
    pos_voltar = final.find("Voltar ao Início")
    if pos_export >= 0 and pos_card > pos_export:
        raise SystemExit("Entrada Comercial ainda ficou depois da area de exportacao")
    if pos_voltar >= 0 and pos_card > pos_voltar:
        raise SystemExit("Entrada Comercial ainda ficou depois do botao Voltar")

print("Planilha mobile 3906: colunas legiveis com rolagem horizontal e Entrada Comercial reposicionada.")
