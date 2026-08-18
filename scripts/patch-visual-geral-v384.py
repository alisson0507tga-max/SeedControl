from pathlib import Path
import re

ROOT = Path('native/www')
CSS = ROOT / 'app-v384.css'
SW = ROOT / 'service-worker.js'

if not ROOT.exists():
    raise SystemExit('native/www não encontrado.')

EXCLUIR = {'index.html', 'estoque.html', 'cadastro.html', 'teste.html'}
paginas = [p for p in ROOT.glob('*.html') if p.name not in EXCLUIR]

if not paginas:
    raise SystemExit('Nenhuma tela restante encontrada para aplicar o visual geral.')

for pagina in paginas:
    html = pagina.read_text(encoding='utf-8')

    if 'app-v384.css' not in html:
        if '</head>' not in html:
            raise SystemExit(f'</head> não encontrado em {pagina.name}')
        html = html.replace(
            '</head>',
            '    <link rel="stylesheet" href="app-v384.css">\n</head>',
            1
        )

    classe_pagina = 'seed-v384-' + re.sub(r'[^a-z0-9-]+', '-', pagina.stem.lower())

    def ajustar_body(match):
        attrs = match.group(1) or ''
        classe_match = re.search(r'class=["\']([^"\']*)["\']', attrs)
        classes = ['seed-v384-page', classe_pagina]

        if classe_match:
            atuais = classe_match.group(1).split()
            for classe in classes:
                if classe not in atuais:
                    atuais.append(classe)
            novo = 'class="' + ' '.join(atuais) + '"'
            attrs_novos = attrs[:classe_match.start()] + novo + attrs[classe_match.end():]
        else:
            attrs_novos = attrs + ' class="' + ' '.join(classes) + '"'

        return '<body' + attrs_novos + '>'

    html, qtd = re.subn(r'<body([^>]*)>', ajustar_body, html, count=1, flags=re.I)
    if qtd != 1:
        raise SystemExit(f'<body> não encontrado em {pagina.name}')

    pagina.write_text(html, encoding='utf-8')

css = r'''/* seedcontrol-visual-geral-v384 */

body.seed-v384-page {
    min-height: 100vh;
    margin: 0;
    background:
        radial-gradient(circle at 100% 0%, rgba(34, 197, 94, .08), transparent 28%),
        linear-gradient(180deg, #06111a 0%, #071722 48%, #06141d 100%);
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

body.seed-v384-page .topo,
body.seed-v384-page > header:not(.modal):not(.dialog) {
    position: relative;
    overflow: hidden;
    padding: 22px 20px 20px;
    background:
        radial-gradient(circle at 92% 12%, rgba(34, 197, 94, .18), transparent 30%),
        linear-gradient(110deg, #071814 0%, #063322 58%, #06251d 100%) !important;
    border-bottom: 1px solid rgba(74, 222, 128, .23);
    box-shadow: 0 10px 28px rgba(0, 0, 0, .25);
}

body.seed-v384-page .topo h1,
body.seed-v384-page > header h1 {
    margin: 0;
    color: #fff !important;
    font-size: clamp(28px, 7.5vw, 36px);
    line-height: 1.08;
    letter-spacing: -.5px;
}

body.seed-v384-page .topo p,
body.seed-v384-page > header p {
    margin: 7px 0 0;
    color: #b7c5c9 !important;
}

body.seed-v384-page .container,
body.seed-v384-page main {
    width: 100%;
    max-width: 760px;
    margin-left: auto;
    margin-right: auto;
    padding-left: 16px;
    padding-right: 16px;
    padding-bottom: calc(28px + env(safe-area-inset-bottom));
}

body.seed-v384-page .container {
    padding-top: 18px;
}

body.seed-v384-page .card,
body.seed-v384-page .painel,
body.seed-v384-page .secao,
body.seed-v384-page .box,
body.seed-v384-page .filtros,
body.seed-v384-page .resumo,
body.seed-v384-page .resultado,
body.seed-v384-page .relatorio,
body.seed-v384-page .config-card,
body.seed-v384-page form {
    border: 1px solid rgba(148, 163, 184, .18) !important;
    border-radius: 18px !important;
    background: linear-gradient(145deg, rgba(20, 38, 49, .98), rgba(10, 28, 39, .98)) !important;
    box-shadow: 0 9px 24px rgba(0, 0, 0, .20) !important;
    color: #f8fafc;
}

body.seed-v384-page .card,
body.seed-v384-page .painel,
body.seed-v384-page .secao,
body.seed-v384-page .box,
body.seed-v384-page .filtros,
body.seed-v384-page .resumo,
body.seed-v384-page .resultado,
body.seed-v384-page .relatorio,
body.seed-v384-page .config-card {
    padding: 16px !important;
    margin-bottom: 13px;
}

body.seed-v384-page h2,
body.seed-v384-page h3 {
    color: #f8fafc;
}

body.seed-v384-page label {
    display: block;
    margin: 12px 0 7px;
    color: #e6edef !important;
    font-size: 14px;
    font-weight: 700;
}

body.seed-v384-page input:not([type="checkbox"]):not([type="radio"]):not([type="file"]),
body.seed-v384-page select,
body.seed-v384-page textarea {
    width: 100%;
    min-height: 50px;
    margin: 0;
    padding: 0 14px;
    border: 1px solid rgba(148, 163, 184, .26) !important;
    border-radius: 13px !important;
    outline: none;
    background: rgba(6, 20, 29, .92) !important;
    color: #f8fafc !important;
    font-size: 15px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .02) !important;
}

body.seed-v384-page textarea {
    min-height: 94px;
    padding-top: 12px;
    padding-bottom: 12px;
}

body.seed-v384-page input::placeholder,
body.seed-v384-page textarea::placeholder {
    color: #7f9099 !important;
}

body.seed-v384-page input:focus,
body.seed-v384-page select:focus,
body.seed-v384-page textarea:focus {
    border-color: rgba(74, 222, 128, .65) !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, .10) !important;
}

body.seed-v384-page button,
body.seed-v384-page .btn,
body.seed-v384-page a.botao {
    min-height: 50px;
    border: 1px solid rgba(103, 232, 85, .48) !important;
    border-radius: 13px !important;
    background: linear-gradient(100deg, #147d36, #20a848 58%, #178d3b) !important;
    color: #fff !important;
    font-weight: 700;
    box-shadow: 0 6px 18px rgba(18, 112, 49, .16) !important;
}

body.seed-v384-page button:active,
body.seed-v384-page .btn:active,
body.seed-v384-page a.botao:active {
    transform: translateY(1px);
}

body.seed-v384-page .btn-excluir,
body.seed-v384-page .excluir,
body.seed-v384-page button[data-action="excluir"] {
    border-color: rgba(248, 113, 113, .36) !important;
    background: linear-gradient(100deg, #9e3030, #bf4040) !important;
}

body.seed-v384-page .btn-editar,
body.seed-v384-page .editar {
    border-color: rgba(96, 165, 250, .38) !important;
    background: linear-gradient(100deg, #225a9e, #2c70bd) !important;
}

body.seed-v384-page .btn-qr,
body.seed-v384-page .qr {
    border-color: rgba(167, 139, 250, .40) !important;
    background: linear-gradient(100deg, #5a3797, #7047bd) !important;
}

body.seed-v384-page table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, .18);
    border-radius: 14px;
    background: rgba(6, 20, 29, .72);
    color: #eaf0f2;
}

body.seed-v384-page th {
    padding: 11px 9px;
    background: rgba(18, 82, 49, .72) !important;
    color: #fff !important;
    font-size: 12px;
}

body.seed-v384-page td {
    padding: 10px 9px;
    border-top: 1px solid rgba(148, 163, 184, .12);
    color: #dce5e8 !important;
    font-size: 13px;
}

body.seed-v384-page .table-container,
body.seed-v384-page .tabela-container,
body.seed-v384-page .table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 14px;
}

body.seed-v384-page .acoes,
body.seed-v384-page .acoes-registro,
body.seed-v384-page .botoes,
body.seed-v384-page .button-group {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
}

body.seed-v384-page .alerta,
body.seed-v384-page .mensagem,
body.seed-v384-page .info,
body.seed-v384-page .status {
    border-radius: 13px;
}

body.seed-v384-page pre,
body.seed-v384-page code {
    max-width: 100%;
    overflow-x: auto;
    color: #d9e4e7;
}

body.seed-v384-page img,
body.seed-v384-page canvas,
body.seed-v384-page svg {
    max-width: 100%;
}

body.seed-v384-page a {
    color: #73df88;
}

body.seed-v384-page .voltar,
body.seed-v384-page .btn-voltar,
body.seed-v384-page button[onclick*="index.html"] {
    border-color: rgba(74, 222, 128, .38) !important;
    background: rgba(16, 74, 45, .58) !important;
    color: #e9fff0 !important;
    box-shadow: none !important;
}

@media (max-width: 390px) {
    body.seed-v384-page .container,
    body.seed-v384-page main {
        padding-left: 12px;
        padding-right: 12px;
    }

    body.seed-v384-page .acoes,
    body.seed-v384-page .acoes-registro,
    body.seed-v384-page .botoes,
    body.seed-v384-page .button-group {
        grid-template-columns: 1fr;
    }
}
'''

CSS.write_text(css, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')

    for anterior in ('seedcontrol-v3.8-pwa-15', 'seedcontrol-v3.8-pwa-16'):
        if anterior in sw:
            sw = sw.replace(anterior, 'seedcontrol-v3.8-pwa-17', 1)
            break

    if 'app-v384.css' not in sw:
        padrao = re.compile(r'(["\'](?:\./)?(?:dashboard-v384|estoque-v384|cadastro-v384|style)\.css["\'])\s*,?')
        encontrado = padrao.search(sw)
        if encontrado:
            ancora = encontrado.group(1)
            substituicao = ancora + ',\n    "app-v384.css",'
            sw = sw[:encontrado.start()] + substituicao + sw[encontrado.end():]
        else:
            print('Aviso: cache do Service Worker não reconhecido; tema geral seguirá empacotado no APK.')

    SW.write_text(sw, encoding='utf-8')

for pagina in paginas:
    conteudo = pagina.read_text(encoding='utf-8')
    if 'app-v384.css' not in conteudo or 'seed-v384-page' not in conteudo:
        raise SystemExit(f'Visual geral não aplicado corretamente em {pagina.name}')

if 'seedcontrol-visual-geral-v384' not in CSS.read_text(encoding='utf-8'):
    raise SystemExit('CSS geral v3.8.4 não foi criado corretamente.')

print('Visual geral v3.8.4 aplicado às telas restantes:')
for pagina in paginas:
    print(' -', pagina.name)
