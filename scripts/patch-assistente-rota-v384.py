from pathlib import Path

ROOT = Path('native/www')
ANTIGA = ROOT / 'assistente.html'
NOVA = ROOT / 'assistente-chat-v384.html'

if not ANTIGA.exists():
    raise SystemExit('assistente.html não encontrado após patch do Assistente.')

html_chat = ANTIGA.read_text(encoding='utf-8')

if 'btnMicrofoneAssistente' not in html_chat or 'assistente-v384.js' not in html_chat:
    raise SystemExit('A página assistente.html ainda não contém o novo chat.')

# Marca exclusiva para validar que a nova rota foi realmente empacotada.
if 'seedcontrol-assistente-rota-chat-v384' not in html_chat:
    html_chat = html_chat.replace(
        '<body ',
        '<body data-assistente-rota="seedcontrol-assistente-rota-chat-v384" ',
        1
    )

NOVA.write_text(html_chat, encoding='utf-8')

# Troca todas as entradas do app para a nova rota, sem depender da página antiga/cache antigo.
for pagina in ROOT.glob('*.html'):
    if pagina == NOVA:
        continue
    texto = pagina.read_text(encoding='utf-8')
    if 'assistente.html' in texto:
        texto = texto.replace('assistente.html', 'assistente-chat-v384.html')
        pagina.write_text(texto, encoding='utf-8')

index = ROOT / 'index.html'
if not index.exists():
    raise SystemExit('index.html não encontrado.')

index_final = index.read_text(encoding='utf-8')
chat_final = NOVA.read_text(encoding='utf-8')

if 'assistente-chat-v384.html' not in index_final:
    raise SystemExit('Dashboard não aponta para a nova rota do Assistente.')

if 'seedcontrol-assistente-rota-chat-v384' not in chat_final:
    raise SystemExit('Marca da nova rota do Assistente não encontrada.')

if 'btnMicrofoneAssistente' not in chat_final:
    raise SystemExit('Microfone não encontrado na nova rota do Assistente.')

print('Nova rota do Assistente criada e Dashboard redirecionado para assistente-chat-v384.html.')
