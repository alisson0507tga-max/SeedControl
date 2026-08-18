from pathlib import Path

ROOT = Path('native/www')
ANTIGA = ROOT / 'assistente.html'
NOVA = ROOT / 'assistente-chat-v384.html'
INDEX = ROOT / 'index.html'

if not ANTIGA.exists():
    raise SystemExit('assistente.html não encontrado após patch do Assistente.')

if not INDEX.exists():
    raise SystemExit('index.html não encontrado.')

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

# No APK o conteúdo já vem empacotado. Desregistramos Service Workers antigos e
# apagamos apenas caches de páginas/arquivos; os dados do app em localStorage ficam intactos.
index_texto = INDEX.read_text(encoding='utf-8')
marcador_cache = 'seedcontrol-apk-limpar-cache-assistente-v384'
if marcador_cache not in index_texto:
    script = r'''
<script>
// seedcontrol-apk-limpar-cache-assistente-v384
(function () {
    try {
        if ('serviceWorker' in navigator && navigator.serviceWorker.getRegistrations) {
            navigator.serviceWorker.getRegistrations().then(function (regs) {
                regs.forEach(function (reg) { reg.unregister(); });
            }).catch(function () {});
        }
        if ('caches' in window && caches.keys) {
            caches.keys().then(function (nomes) {
                return Promise.all(nomes.map(function (nome) { return caches.delete(nome); }));
            }).catch(function () {});
        }
    } catch (e) {}
})();
</script>
'''
    if '</body>' not in index_texto:
        raise SystemExit('</body> não encontrado no index.html.')
    index_texto = index_texto.replace('</body>', script + '\n</body>', 1)
    INDEX.write_text(index_texto, encoding='utf-8')

index_final = INDEX.read_text(encoding='utf-8')
chat_final = NOVA.read_text(encoding='utf-8')

if 'assistente-chat-v384.html' not in index_final:
    raise SystemExit('Dashboard não aponta para a nova rota do Assistente.')

if marcador_cache not in index_final:
    raise SystemExit('Limpeza de cache do APK não foi instalada no Dashboard.')

if 'seedcontrol-assistente-rota-chat-v384' not in chat_final:
    raise SystemExit('Marca da nova rota do Assistente não encontrada.')

if 'btnMicrofoneAssistente' not in chat_final:
    raise SystemExit('Microfone não encontrado na nova rota do Assistente.')

print('Nova rota do Assistente criada, Dashboard redirecionado e cache antigo neutralizado.')
