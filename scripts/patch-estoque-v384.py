from pathlib import Path

ROOT = Path('native/www')
HTML = ROOT / 'estoque.html'
JS = ROOT / 'estoque.js'
CSS = ROOT / 'estoque-v384.css'
SW = ROOT / 'service-worker.js'

for arquivo in (HTML, JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo não encontrado: {arquivo}')

html = HTML.read_text(encoding='utf-8')
js = JS.read_text(encoding='utf-8')

html_novo = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#071713">
    <title>Estoque - SeedControl</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="estoque-v384.css">
</head>
<body class="estoque-body">

<header class="estoque-topo">
    <div class="estoque-topo-conteudo">
        <div class="estoque-topo-icone" aria-hidden="true">📦</div>
        <div>
            <h1>Estoque</h1>
            <p>Controle de lotes e quantidades</p>
        </div>
    </div>
</header>

<main class="container estoque-container">

    <section class="estoque-painel estoque-pesquisa" aria-label="Pesquisa do estoque">
        <label for="pesquisa">Buscar no estoque</label>
        <div class="estoque-input-wrap">
            <span aria-hidden="true">⌕</span>
            <input
                type="text"
                id="pesquisa"
                placeholder="Cultivar, lote, fazenda, talhão ou peneira..."
                autocomplete="off"
            >
        </div>
    </section>

    <section class="estoque-painel estoque-ordenacao" aria-label="Ordenação do estoque">
        <label for="ordenacao">Ordenar por</label>
        <select id="ordenacao">
            <option value="data_desc">📅 Data de cadastro (mais recentes)</option>
            <option value="cultivar_asc">🌱 Cultivar (A-Z)</option>
            <option value="fazenda_asc">🚜 Fazenda (A-Z)</option>
            <option value="lote_asc">📋 Lote (menor → maior)</option>
            <option value="bags_desc">📦 Quantidade de Bags (maior → menor)</option>
        </select>
    </section>

    <section class="estoque-resumo" aria-label="Resumo do estoque">
        <div class="estoque-resumo-titulo">
            <span aria-hidden="true">▦</span>
            <h2>Resumo do Estoque</h2>
        </div>

        <div class="estoque-resumo-grid">
            <article class="estoque-resumo-item">
                <span class="estoque-resumo-icone" aria-hidden="true">📦</span>
                <div>
                    <small>Total de Bags</small>
                    <strong id="totalBags">0</strong>
                </div>
            </article>

            <article class="estoque-resumo-item">
                <span class="estoque-resumo-icone" aria-hidden="true">⚖️</span>
                <div>
                    <small>Kg (Média)</small>
                    <strong><span id="totalKgsMedia">0</span> kg</strong>
                </div>
            </article>

            <article class="estoque-resumo-item">
                <span class="estoque-resumo-icone" aria-hidden="true">🌾</span>
                <div>
                    <small>Sacas (60 kg)</small>
                    <strong id="totalSacas60kg">0</strong>
                </div>
            </article>

            <article class="estoque-resumo-item">
                <span class="estoque-resumo-icone" aria-hidden="true">📋</span>
                <div>
                    <small>Total de Lotes</small>
                    <strong id="totalLotes">0</strong>
                </div>
            </article>
        </div>
    </section>

    <div class="estoque-lista-cabecalho">
        <h2>Lotes cadastrados</h2>
        <span>Toque no card para abrir a cultivar</span>
    </div>

    <section id="lista" class="estoque-lista" aria-live="polite"></section>

    <button
        class="estoque-voltar"
        type="button"
        onclick="window.location.href='index.html'"
    >
        <span aria-hidden="true">←</span>
        Voltar ao Início
    </button>

</main>

<script src="database.js"></script>
<script src="estoque.js"></script>
</body>
</html>
'''

for id_necessario in ('pesquisa', 'ordenacao', 'totalBags', 'totalKgsMedia', 'totalSacas60kg', 'totalLotes', 'lista'):
    if f'id="{id_necessario}"' not in html_novo:
        raise SystemExit(f'ID obrigatório ausente no novo Estoque: {id_necessario}')

HTML.write_text(html_novo, encoding='utf-8')

js = js.replace(
    'class="card card-registro"',
    'class="card card-registro estoque-registro"'
)

marcador = '// seedcontrol-estoque-ui-v384\n'
if marcador not in js:
    js = marcador + js

JS.write_text(js, encoding='utf-8')

css = r'''/* SeedControl v3.8.4 - Estoque */

.estoque-body {
    min-height: 100vh;
    background:
        radial-gradient(circle at 100% 0%, rgba(34, 197, 94, .09), transparent 30%),
        linear-gradient(180deg, #06111a 0%, #071722 48%, #06141d 100%);
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

.estoque-topo {
    position: relative;
    overflow: hidden;
    padding: 22px 20px 20px;
    background:
        radial-gradient(circle at 92% 12%, rgba(34, 197, 94, .18), transparent 30%),
        linear-gradient(110deg, #071814 0%, #063322 58%, #06251d 100%);
    border-bottom: 1px solid rgba(74, 222, 128, .23);
    box-shadow: 0 10px 28px rgba(0, 0, 0, .28);
}

.estoque-topo::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(74, 222, 128, .78), transparent);
}

.estoque-topo-conteudo {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 13px;
}

.estoque-topo-icone {
    width: 54px;
    height: 54px;
    flex: 0 0 54px;
    display: grid;
    place-items: center;
    border-radius: 16px;
    border: 1px solid rgba(74, 222, 128, .35);
    background: linear-gradient(145deg, rgba(29, 92, 57, .65), rgba(9, 47, 36, .75));
    font-size: 30px;
}

.estoque-topo h1 {
    margin: 0;
    font-size: clamp(29px, 8vw, 36px);
    line-height: 1;
    letter-spacing: -.6px;
    color: #fff;
}

.estoque-topo p {
    margin: 7px 0 0;
    color: #b8c5ca;
    font-size: 15px;
}

.estoque-container {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    padding: 18px 16px calc(26px + env(safe-area-inset-bottom));
}

.estoque-painel,
.estoque-resumo {
    width: 100%;
    margin-bottom: 13px;
    padding: 15px;
    border: 1px solid rgba(148, 163, 184, .20);
    border-radius: 17px;
    background: linear-gradient(145deg, rgba(20, 38, 49, .96), rgba(11, 29, 40, .96));
    box-shadow: 0 8px 22px rgba(0, 0, 0, .20);
}

.estoque-painel label {
    display: block;
    margin: 0 0 9px 2px;
    color: #dce6e9;
    font-size: 14px;
    font-weight: 700;
}

.estoque-input-wrap {
    position: relative;
}

.estoque-input-wrap > span {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
    color: #61d978;
    font-size: 24px;
    pointer-events: none;
}

.estoque-body #pesquisa,
.estoque-body #ordenacao {
    width: 100%;
    min-height: 52px;
    margin: 0;
    border: 1px solid rgba(148, 163, 184, .27);
    border-radius: 13px;
    background: rgba(6, 20, 29, .90);
    color: #f8fafc;
    font-size: 15px;
    outline: none;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .02);
}

.estoque-body #pesquisa {
    padding: 0 14px 0 44px;
}

.estoque-body #ordenacao {
    padding: 0 38px 0 13px;
}

.estoque-body #pesquisa::placeholder {
    color: #81919a;
}

.estoque-body #pesquisa:focus,
.estoque-body #ordenacao:focus {
    border-color: rgba(74, 222, 128, .65);
    box-shadow: 0 0 0 3px rgba(34, 197, 94, .10);
}

.estoque-resumo {
    padding: 16px;
}

.estoque-resumo-titulo {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 13px;
}

.estoque-resumo-titulo > span {
    color: #51d76a;
    font-size: 20px;
}

.estoque-resumo-titulo h2 {
    margin: 0;
    font-size: 18px;
    color: #fff;
}

.estoque-resumo-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
}

.estoque-resumo-item {
    min-width: 0;
    min-height: 84px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, .17);
    background: rgba(4, 24, 33, .60);
}

.estoque-resumo-icone {
    width: 38px;
    height: 38px;
    flex: 0 0 38px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    border: 1px solid rgba(74, 222, 128, .28);
    background: rgba(23, 92, 53, .36);
    font-size: 20px;
}

.estoque-resumo-item div {
    min-width: 0;
}

.estoque-resumo-item small {
    display: block;
    margin-bottom: 4px;
    color: #aab9c0;
    font-size: 12px;
    line-height: 1.2;
}

.estoque-resumo-item strong {
    display: block;
    color: #48d261;
    font-size: clamp(18px, 5.6vw, 24px);
    line-height: 1.1;
    font-weight: 650;
    overflow-wrap: anywhere;
}

.estoque-lista-cabecalho {
    margin: 20px 3px 10px;
}

.estoque-lista-cabecalho h2 {
    margin: 0;
    color: #f7fafc;
    font-size: 18px;
}

.estoque-lista-cabecalho span {
    display: block;
    margin-top: 4px;
    color: #8fa0a8;
    font-size: 12px;
}

.estoque-lista {
    width: 100%;
}

.estoque-body .estoque-registro,
.estoque-body #lista .card-registro {
    position: relative;
    width: 100%;
    margin: 0 0 13px;
    padding: 16px !important;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 13px;
    row-gap: 0;
    border-top: 1px solid rgba(148, 163, 184, .18);
    border-right: 1px solid rgba(148, 163, 184, .18);
    border-bottom: 1px solid rgba(148, 163, 184, .18);
    border-radius: 17px;
    background: linear-gradient(145deg, rgba(20, 38, 49, .98), rgba(10, 28, 39, .98));
    box-shadow: 0 8px 22px rgba(0, 0, 0, .22);
    overflow: hidden;
}

.estoque-body #lista .card-registro > h2 {
    grid-column: 1 / -1;
    margin: 0 0 7px;
    color: #fff;
    font-size: 21px;
    line-height: 1.2;
}

.estoque-body #lista .card-registro > p {
    min-width: 0;
    margin: 5px 0;
    padding: 7px 8px;
    border-radius: 10px;
    background: rgba(6, 21, 30, .50);
    color: #d8e1e5;
    font-size: 13px;
    line-height: 1.35;
    overflow-wrap: anywhere;
}

.estoque-body #lista .card-registro > p:first-of-type {
    grid-column: 1 / -1;
    padding: 0;
    margin: 0 0 7px;
    background: transparent;
}

.estoque-body #lista .card-registro > p:first-of-type span {
    padding: 5px 10px !important;
    border-radius: 999px !important;
    font-size: 12px;
}

.estoque-body #lista .card-registro strong {
    display: block;
    margin-bottom: 2px;
    color: #8fa0a8;
    font-size: 11px;
    font-weight: 600;
}

.estoque-body #lista .btn-movimentar {
    grid-column: 1 / -1;
    min-height: 50px;
    margin: 12px 0 0 !important;
    border: 1px solid rgba(103, 232, 85, .55);
    border-radius: 13px;
    background: linear-gradient(100deg, #147d36, #20a848 58%, #178d3b) !important;
    color: #fff;
    font-size: 15px;
    box-shadow: 0 6px 18px rgba(18, 112, 49, .18);
}

.estoque-body #lista .acoes-registro {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin-top: 8px;
}

.estoque-body #lista .acoes-registro button {
    min-width: 0;
    min-height: 46px;
    padding: 10px 7px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.15;
}

.estoque-body #lista .btn-editar {
    background: #2563a9;
}

.estoque-body #lista .btn-qr {
    background: #6440a8 !important;
}

.estoque-body #lista .btn-excluir {
    background: #b93838;
}

.estoque-body #lista > .card:not(.card-registro) {
    border: 1px solid rgba(148, 163, 184, .18);
    background: rgba(17, 35, 46, .95);
    color: #d8e1e5;
}

.estoque-body button.estoque-voltar {
    min-height: 54px;
    margin-top: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: 1px solid rgba(74, 222, 128, .44);
    border-radius: 14px;
    background: rgba(16, 74, 45, .58);
    color: #e9fff0;
    font-size: 16px;
    box-shadow: none;
}

@media (max-width: 390px) {
    .estoque-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .estoque-resumo-item {
        padding: 10px;
        gap: 8px;
    }

    .estoque-resumo-icone {
        width: 34px;
        height: 34px;
        flex-basis: 34px;
        font-size: 18px;
    }

    .estoque-body #lista .card-registro > p {
        font-size: 12px;
    }
}
'''

CSS.write_text(css, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    if 'seedcontrol-v3.8-pwa-14' in sw:
        sw = sw.replace('seedcontrol-v3.8-pwa-14', 'seedcontrol-v3.8-pwa-15', 1)
    elif 'seedcontrol-v3.8-pwa-15' not in sw:
        raise SystemExit('Versão esperada do cache (pwa-14) não encontrada.')

    if '"estoque-v384.css"' not in sw and "'estoque-v384.css'" not in sw:
        if '"style.css"' in sw:
            sw = sw.replace('"style.css",', '"style.css",\n    "estoque-v384.css",', 1)
        elif "'style.css'" in sw:
            sw = sw.replace("'style.css',", "'style.css',\n    'estoque-v384.css',", 1)
        else:
            raise SystemExit('style.css não encontrado na lista do Service Worker.')

    SW.write_text(sw, encoding='utf-8')

html_final = HTML.read_text(encoding='utf-8')
js_final = JS.read_text(encoding='utf-8')
css_final = CSS.read_text(encoding='utf-8')

validacoes = [
    ('estoque-v384.css', html_final),
    ('class="estoque-body"', html_final),
    ('id="pesquisa"', html_final),
    ('id="ordenacao"', html_final),
    ('id="totalBags"', html_final),
    ('id="totalKgsMedia"', html_final),
    ('id="totalSacas60kg"', html_final),
    ('id="totalLotes"', html_final),
    ('id="lista"', html_final),
    ('seedcontrol-estoque-ui-v384', js_final),
    ('data-action="movimentar"', js_final),
    ('.estoque-resumo-grid', css_final),
    ('.estoque-registro', css_final),
]

for trecho, conteudo in validacoes:
    if trecho not in conteudo:
        raise SystemExit(f'Validação do Estoque falhou: {trecho}')

print('Estoque v3.8.4 modernizado sem alterar regras de negócio, filtros ou ações.')
