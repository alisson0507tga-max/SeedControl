from pathlib import Path

ROOT = Path('native/www')
HTML = ROOT / 'estoque.html'
JS = ROOT / 'estoque-busca-v384.js'

if not HTML.exists():
    raise SystemExit('estoque.html não encontrado.')

js = r'''// seedcontrol-estoque-busca-funcional-v384
// seedcontrol-estoque-busca-exata-v3829
(function () {
    "use strict";

    function normalizar(valor) {
        return String(valor == null ? "" : valor)
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function textoDoCard(card) {
        return normalizar(card.innerText || card.textContent || "");
    }

    function valorPorRotulo(card, rotuloRegex) {
        const bruto = String(card.innerText || card.textContent || "");
        const re = new RegExp(rotuloRegex + "\\s*:\\s*([^\\n\\r]+)", "i");
        const m = bruto.match(re);
        if (!m) return "";
        return normalizar(m[1]).replace(/\s+/g, " ").trim();
    }

    function loteDoCard(card) {
        return valorPorRotulo(card, "(?:📋\\s*)?Lote");
    }

    function cultivarDoCard(card) {
        const titulo = card.querySelector('h2');
        if (!titulo) return "";
        return normalizar(titulo.textContent || "")
            .replace(/^[^a-z0-9]+/i, "")
            .trim();
    }

    function camposNumericosPesquisaveis(card) {
        return [
            loteDoCard(card),
            cultivarDoCard(card),
            valorPorRotulo(card, "(?:🚜\\s*)?Fazenda"),
            valorPorRotulo(card, "(?:📍\\s*)?Talh(?:a|ã)o"),
            valorPorRotulo(card, "(?:🌾\\s*)?Peneira")
        ].filter(Boolean);
    }

    function correspondeNumeroExato(card, termo) {
        return camposNumericosPesquisaveis(card).some(valor => valor === termo);
    }

    function cards() {
        return Array.from(document.querySelectorAll('#lista .card-registro, #lista .estoque-registro'));
    }

    function criarStatus(painel) {
        let status = document.getElementById('estoqueBuscaStatus');
        if (status) return status;

        status = document.createElement('div');
        status.id = 'estoqueBuscaStatus';
        status.className = 'estoque-busca-status';
        status.setAttribute('aria-live', 'polite');
        painel.insertAdjacentElement('afterend', status);
        return status;
    }

    function instalarEstilo() {
        if (document.getElementById('estoqueBuscaEstiloV384')) return;
        const style = document.createElement('style');
        style.id = 'estoqueBuscaEstiloV384';
        style.textContent = `
            .estoque-busca-status {
                display: none;
                margin: -2px 2px 12px;
                padding: 10px 12px;
                border: 1px solid rgba(74, 222, 128, .24);
                border-radius: 12px;
                background: rgba(8, 35, 31, .72);
                color: #cde8d4;
                font-size: 13px;
                line-height: 1.35;
            }
            .estoque-busca-status.ativo { display: block; }
            .estoque-busca-status.vazio {
                border-color: rgba(248, 113, 113, .28);
                background: rgba(69, 18, 24, .42);
                color: #fecaca;
            }
            .estoque-body.estoque-buscando .estoque-ordenacao,
            .estoque-body.estoque-buscando .estoque-resumo {
                display: none !important;
            }
            .estoque-body.estoque-buscando .estoque-lista-cabecalho {
                margin-top: 8px !important;
            }
            .estoque-body.estoque-buscando .estoque-lista-cabecalho h2::after {
                content: " — resultados";
                color: #7fdc91;
                font-size: 13px;
                font-weight: 500;
            }
            #lista .card-registro.seed-busca-oculto,
            #lista .estoque-registro.seed-busca-oculto {
                display: none !important;
            }
            #lista .card-registro.seed-busca-destaque,
            #lista .estoque-registro.seed-busca-destaque {
                border-color: rgba(74, 222, 128, .58) !important;
                box-shadow: 0 0 0 2px rgba(34, 197, 94, .10), 0 8px 22px rgba(0,0,0,.22) !important;
            }
        `;
        document.head.appendChild(style);
    }

    function iniciar() {
        const campo = document.getElementById('pesquisa');
        const painel = campo && campo.closest('.estoque-pesquisa');
        const lista = document.getElementById('lista');
        if (!campo || !painel || !lista) return;

        instalarEstilo();
        const status = criarStatus(painel);
        let aplicando = false;

        function aplicarBusca() {
            if (aplicando) return;
            aplicando = true;

            try {
                const termoOriginal = String(campo.value || '').trim();
                const termo = normalizar(termoOriginal);
                const todos = cards();

                todos.forEach(card => {
                    card.classList.remove('seed-busca-oculto', 'seed-busca-destaque');
                });

                if (!termo) {
                    document.body.classList.remove('estoque-buscando');
                    status.classList.remove('ativo', 'vazio');
                    status.textContent = '';
                    return;
                }

                document.body.classList.add('estoque-buscando');

                const somenteNumero = /^\d+$/.test(termo);
                let correspondentes = [];

                if (somenteNumero) {
                    // Número puro é busca EXATA. Ex.: 11 nunca pode retornar 112.
                    // São considerados os campos indicados na própria busca:
                    // lote, cultivar, fazenda, talhão e peneira.
                    correspondentes = todos.filter(card => correspondeNumeroExato(card, termo));
                } else {
                    // Texto continua flexível: pode localizar parte do nome/descrição.
                    correspondentes = todos.filter(card => textoDoCard(card).includes(termo));
                }

                const conjunto = new Set(correspondentes);
                todos.forEach(card => {
                    if (conjunto.has(card)) card.classList.add('seed-busca-destaque');
                    else card.classList.add('seed-busca-oculto');
                });

                const qtd = correspondentes.length;
                status.classList.add('ativo');
                status.classList.toggle('vazio', qtd === 0);

                if (qtd === 0) {
                    status.textContent = somenteNumero
                        ? `Nenhum resultado exato encontrado para “${termoOriginal}”.`
                        : `Nenhum resultado encontrado para “${termoOriginal}”.`;
                } else if (qtd === 1) {
                    status.textContent = `1 resultado encontrado para “${termoOriginal}”.`;
                } else {
                    status.textContent = `${qtd} resultados encontrados para “${termoOriginal}”.`;
                }
            } finally {
                aplicando = false;
            }
        }

        // Captura antes do listener antigo para a busca nova ser a responsável pelo filtro.
        campo.addEventListener('input', function (event) {
            event.stopImmediatePropagation();
            aplicarBusca();
        }, true);

        campo.addEventListener('search', function (event) {
            event.stopImmediatePropagation();
            aplicarBusca();
        }, true);

        campo.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            aplicarBusca();
            const primeiro = cards().find(card => !card.classList.contains('seed-busca-oculto'));
            if (primeiro) {
                try { campo.blur(); } catch (_) {}
                setTimeout(() => primeiro.scrollIntoView({ behavior: 'smooth', block: 'center' }), 80);
            }
        }, true);

        // Se estoque.js renderizar novamente por ordenação/storage, reaplica o filtro.
        const observer = new MutationObserver(function () {
            if (String(campo.value || '').trim()) requestAnimationFrame(aplicarBusca);
        });
        observer.observe(lista, { childList: true, subtree: true });

        aplicarBusca();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciar, { once: true });
    } else {
        iniciar();
    }
})();
'''

JS.write_text(js, encoding='utf-8')

html = HTML.read_text(encoding='utf-8')
if 'estoque-busca-v384.js' not in html:
    alvo = '<script src="estoque.js"></script>'
    if alvo not in html:
        raise SystemExit('Não foi possível localizar estoque.js em estoque.html')
    html = html.replace(alvo, alvo + '\n<script src="estoque-busca-v384.js?v=3829"></script>', 1)
else:
    html = html.replace('estoque-busca-v384.js?v=3828', 'estoque-busca-v384.js?v=3829')
HTML.write_text(html, encoding='utf-8')

final_html = HTML.read_text(encoding='utf-8')
final_js = JS.read_text(encoding='utf-8')

for marca in (
    'seedcontrol-estoque-busca-funcional-v384',
    'seedcontrol-estoque-busca-exata-v3829',
    'cultivarDoCard',
    'correspondeNumeroExato',
    'Nenhum resultado exato encontrado',
    'stopImmediatePropagation'
):
    if marca not in final_js:
        raise SystemExit(f'Marca ausente na busca nova: {marca}')

if 'estoque-busca-v384.js?v=3829' not in final_html:
    raise SystemExit('Script da busca 3829 não foi injetado em estoque.html')

print('Busca do Estoque corrigida: número puro exige correspondência exata e não retorna prefixos como 112 para 11.')
