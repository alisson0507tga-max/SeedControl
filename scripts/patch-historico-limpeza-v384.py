from pathlib import Path
import re

ROOT = Path('native/www')
HTML = ROOT / 'historico.html'
ASSET = Path('assets/historico-limpeza-v3836.js')
DEST = ROOT / 'historico-limpeza-v3836.js'
SW = ROOT / 'service-worker.js'

if not HTML.exists():
    raise SystemExit('historico.html não encontrado.')
if not ASSET.exists():
    raise SystemExit('asset historico-limpeza-v3836.js não encontrado.')

DEST.write_text(ASSET.read_text(encoding='utf-8'), encoding='utf-8')

html = HTML.read_text(encoding='utf-8')
script = '<script src="historico-limpeza-v3836.js?v=3836"></script>'
if 'historico-limpeza-v3836.js' not in html:
    if '</body>' not in html:
        raise SystemExit('</body> não encontrado em historico.html')
    html = html.replace('</body>', f'    {script}\n</body>', 1)
HTML.write_text(html, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-36', sw, count=1)
    if 'historico-limpeza-v3836.js' not in sw:
        m = re.search(r'(const\s+APP_SHELL\s*=\s*\[)(.*?)(\];)', sw, flags=re.S)
        if m:
            miolo = m.group(2).rstrip()
            virg = ',' if miolo and not miolo.rstrip().endswith(',') else ''
            extra = f'{virg}\n  "./historico-limpeza-v3836.js"\n'
            sw = sw[:m.start(2)] + miolo + extra + sw[m.end(2):]
    SW.write_text(sw, encoding='utf-8')

final_html = HTML.read_text(encoding='utf-8')
final_js = DEST.read_text(encoding='utf-8')
for marca in (
    'historico-limpeza-v3836.js?v=3836',
):
    if marca not in final_html:
        raise SystemExit(f'Validação falhou em historico.html: {marca}')

for marca in (
    'seedcontrol-historico-limpeza-v3836',
    'salvarHistorico([])',
    'seedcontrol_historico_lixeira_v3836',
    'O ESTOQUE E OS LOTES NÃO SERÃO APAGADOS',
    'Desfazer última limpeza',
):
    if marca not in final_js:
        raise SystemExit(f'Validação falhou em historico-limpeza-v3836.js: {marca}')

print('Limpeza segura do Histórico preparada: apaga só histórico e preserva estoque/lotes, com desfazer temporário.')
