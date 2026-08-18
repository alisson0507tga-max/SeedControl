from pathlib import Path
import re

ROOT = Path('native/www')
SW = ROOT / 'service-worker.js'
INDEX = ROOT / 'index.html'
ASSIST = ROOT / 'assistente.html'
CSS = ROOT / 'assistente-v384.css'
JS = ROOT / 'assistente-v384.js'

for arquivo in (ASSIST, CSS, JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo do Assistente não encontrado: {arquivo}')

# Marca a tela nova para validação e diagnóstico visual.
html = ASSIST.read_text(encoding='utf-8')
if 'data-assistente-versao="38418"' not in html:
    html = html.replace(
        '<body class="seed-v384-page seed-v384-assistente assistente-v384-body">',
        '<body class="seed-v384-page seed-v384-assistente assistente-v384-body" data-assistente-versao="38418">',
        1
    )
ASSIST.write_text(html, encoding='utf-8')

# Bump de cache para obrigar o WebView a abandonar a versão antiga.
if SW.exists():
    sw = SW.read_text(encoding='utf-8')

    # Aceita qualquer cache pwa recente da v3.8 e força um nome novo.
    sw, qtd = re.subn(
        r'seedcontrol-v3\.8-pwa-\d+',
        'seedcontrol-v3.8-pwa-18',
        sw,
        count=1
    )

    if qtd == 0 and 'seedcontrol-v3.8-pwa-18' not in sw:
        print('Aviso: nome do cache não reconhecido; seguindo sem falhar a build.')

    # Tenta incluir explicitamente os arquivos do novo Assistente no precache.
    arquivos = ['assistente.html', 'assistente-v384.css', 'assistente-v384.js']
    for nome in arquivos:
        if nome in sw:
            continue

        padrao = re.compile(r'(["\'](?:\./)?index\.html["\'])\s*,?')
        achou = padrao.search(sw)
        if achou:
            ancora = achou.group(1)
            insercao = ancora + ',\n    "' + nome + '",'
            sw = sw[:achou.start()] + insercao + sw[achou.end():]
        else:
            print(f'Aviso: não foi possível adicionar {nome} ao precache; seguirá empacotado no APK.')

    SW.write_text(sw, encoding='utf-8')

# Adiciona versão na navegação do Dashboard para evitar resposta antiga por URL idêntica.
if INDEX.exists():
    index = INDEX.read_text(encoding='utf-8')
    index = index.replace('assistente.html"', 'assistente.html?v=38418"')
    index = index.replace("assistente.html'", "assistente.html?v=38418'")
    INDEX.write_text(index, encoding='utf-8')

html_final = ASSIST.read_text(encoding='utf-8')
if 'data-assistente-versao="38418"' not in html_final:
    raise SystemExit('Marca da versão nova do Assistente não foi aplicada.')

if INDEX.exists() and 'assistente.html?v=38418' not in INDEX.read_text(encoding='utf-8'):
    raise SystemExit('Dashboard não foi apontado para a URL nova do Assistente.')

print('Cache do Assistente v3.8.4 atualizado e navegação forçada para a versão 38418.')
