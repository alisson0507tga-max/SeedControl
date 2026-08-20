from pathlib import Path

ROOT = Path('native/www')
HTML = ROOT / 'estoque.html'
ASSET = Path('assets/nota-visualizador-v3839.js')
DEST = ROOT / 'nota-visualizador-v3839.js'

if not HTML.exists():
    raise SystemExit('estoque.html nao encontrado.')
if not ASSET.exists():
    raise SystemExit('Asset do visualizador da nota nao encontrado.')

DEST.write_text(ASSET.read_text(encoding='utf-8'), encoding='utf-8')

html = HTML.read_text(encoding='utf-8')
script = '<script src="nota-visualizador-v3839.js?v=3839"></script>'

if script not in html:
    if '</body>' not in html:
        raise SystemExit('Nao foi possivel localizar </body> em estoque.html')
    html = html.replace('</body>', f'    {script}\n</body>', 1)

HTML.write_text(html, encoding='utf-8')

final = HTML.read_text(encoding='utf-8')
js = DEST.read_text(encoding='utf-8')

checks = [
    ('nota-visualizador-v3839.js?v=3839', final),
    ('seedcontrol-nota-visualizador-v3839', js),
    ('notaEntradaFoto', js),
    ('📄 Ver nota', js),
    ('Compartilhar', js),
]
for trecho, conteudo in checks:
    if trecho not in conteudo:
        raise SystemExit(f'Validacao falhou: {trecho}')

print('Visualizador da nota preparado no Estoque: abrir, ampliar e compartilhar foto salva.')
