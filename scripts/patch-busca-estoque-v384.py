from pathlib import Path

ROOT = Path('native/www')
JS = ROOT / 'estoque.js'
CSS = ROOT / 'estoque-v384.css'
HTML = ROOT / 'estoque.html'

for arquivo in (JS, CSS, HTML):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo não encontrado: {arquivo}')

marca_js = '// seedcontrol-busca-estoque-v3828'
js = JS.read_text(encoding='utf-8')

bloco_js = r'''

// seedcontrol-busca-estoque-v3828
(function () {
    "use strict";

    const normalizar = (valor) => String(valor == null ? "" : valor)
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();

    function obterLoteDoCard(card) {
        const texto = String(card && card.textContent || "");
        const match = texto.match(/\blote\s*:\s*([^\s|]+)/i);
        return match ? normalizar(match[1]) : "";
    }

    function criarStatus(campo) {
        let status = document.getElementById("resultadoPesquisaEstoque");
        if (status) return status;

        status = document.createElement("div");
        status.id = "resultadoPesquisaEstoque";
        status.className = "estoque-resultado-pesquisa";
        status.setAttribute("aria-live", "polite");
        status.hidden = true;

        const painel = campo.closest(".estoque-pesquisa") || campo.parentElement;
        if (painel) painel.appendChild(status);
        return status;
    }

    function aplicarBusca() {
        const campo = document.getElementById("pesquisa");
        const lista = document.getElementById("lista");
        if (!campo || !lista) return;

        const status = criarStatus(campo);
        const termoOriginal = String(campo.value || "").trim();
        const termo = normalizar(termoOriginal);
        const cards = Array.from(lista.querySelectorAll(".card-registro, .estoque-registro"));

        document.body.classList.toggle("estoque-buscando", !!termo);

        if (!termo) {
            cards.forEach(card => {
                card.hidden = false;
                card.classList.remove("estoque-resultado-destaque");
            });
            status.hidden = true;
            status.textContent = "";
            return;
        }

        const termoNumerico = /^\d+[a-z0-9._-]*$/i.test(termo.replace(/\s+/g, ""));
        let correspondenciasLote = [];

        if (termoNumerico) {
            correspondenciasLote = cards.filter(card => {
                const lote = obterLoteDoCard(card);
                return lote && lote.includes(termo);
            });
        }

        const usarPrioridadeLote = correspondenciasLote.length > 0;
        let encontrados = 0;
        let primeiro = null;

        cards.forEach(card => {
            const texto = normalizar(card.textContent);
            const lote = obterLoteDoCard(card);
            const combina = usarPrioridadeLote
                ? (lote && lote.includes(termo))
                : texto.includes(termo);

            card.hidden = !combina;
            card.classList.toggle("estoque-resultado-destaque", combina);

            if (combina) {
                encontrados += 1;
                if (!primeiro) primeiro = card;
            }
        });

        status.hidden = false;
        if (encontrados === 0) {
            status.textContent = `Nenhum lote encontrado para “${termoOriginal}”.`;
            status.classList.add("sem-resultado");
        } else {
            status.textContent = encontrados === 1
                ? "1 lote encontrado."
                : `${encontrados} lotes encontrados.`;
            status.classList.remove("sem-resultado");
        }

        campo.dataset.seedPrimeiroResultado = primeiro ? "1" : "0";
    }

    function iniciarBuscaEstoque() {
        const campo = document.getElementById("pesquisa");
        const lista = document.getElementById("lista");
        if (!campo || !lista) return;

        campo.setAttribute("placeholder", "Digite lote, cultivar, fazenda, talhão ou peneira...");
        campo.setAttribute("enterkeyhint", "search");

        campo.addEventListener("input", aplicarBusca, true);
        campo.addEventListener("search", aplicarBusca, true);
        campo.addEventListener("keydown", function (evento) {
            if (evento.key !== "Enter") return;
            aplicarBusca();
            const primeiro = lista.querySelector(".card-registro:not([hidden]), .estoque-registro:not([hidden])");
            if (primeiro) {
                evento.preventDefault();
                try { campo.blur(); } catch (_) {}
                setTimeout(function () {
                    try { primeiro.scrollIntoView({ behavior: "smooth", block: "start" }); } catch (_) {}
                }, 80);
            }
        });

        const observador = new MutationObserver(function () {
            if (campo.value.trim()) aplicarBusca();
        });
        observador.observe(lista, { childList: true, subtree: true });

        aplicarBusca();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarBuscaEstoque, { once: true });
    } else {
        iniciarBuscaEstoque();
    }
})();
'''

if marca_js not in js:
    js += bloco_js
    JS.write_text(js, encoding='utf-8')

marca_css = '/* seedcontrol-busca-estoque-v3828 */'
css = CSS.read_text(encoding='utf-8')
bloco_css = r'''

/* seedcontrol-busca-estoque-v3828 */
.estoque-resultado-pesquisa {
    margin: 10px 2px 0;
    padding: 9px 11px;
    border: 1px solid rgba(74, 222, 128, .25);
    border-radius: 11px;
    background: rgba(16, 85, 48, .20);
    color: #bff7cb;
    font-size: 13px;
    font-weight: 650;
}

.estoque-resultado-pesquisa.sem-resultado {
    border-color: rgba(248, 113, 113, .28);
    background: rgba(127, 29, 29, .16);
    color: #fecaca;
}

body.estoque-buscando .estoque-ordenacao,
body.estoque-buscando .estoque-resumo {
    display: none !important;
}

body.estoque-buscando .estoque-lista-cabecalho {
    margin-top: 14px;
}

body.estoque-buscando .estoque-lista-cabecalho > span {
    display: none;
}

.estoque-body #lista .card-registro[hidden],
.estoque-body #lista .estoque-registro[hidden] {
    display: none !important;
}

.estoque-body #lista .estoque-resultado-destaque {
    border-color: rgba(74, 222, 128, .48) !important;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, .08), 0 8px 22px rgba(0, 0, 0, .22) !important;
}
'''

if marca_css not in css:
    css += bloco_css
    CSS.write_text(css, encoding='utf-8')

js_final = JS.read_text(encoding='utf-8')
css_final = CSS.read_text(encoding='utf-8')

for marca in (marca_js, 'resultadoPesquisaEstoque', 'obterLoteDoCard', 'estoque-buscando', 'scrollIntoView'):
    if marca not in js_final:
        raise SystemExit(f'Marca ausente no estoque.js: {marca}')

for marca in (marca_css, '.estoque-resultado-pesquisa', 'body.estoque-buscando', '.estoque-resultado-destaque'):
    if marca not in css_final:
        raise SystemExit(f'Marca ausente no estoque-v384.css: {marca}')

print('Busca do Estoque corrigida: filtro visível, prioridade para lote numérico e resultado imediato.')
