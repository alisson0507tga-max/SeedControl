from pathlib import Path
import shutil
import re

ROOT = Path('native/www')
SRC = Path('correcoes-3912')

arquivos = {
    'movimentacao-colar-v3912.js': ROOT / 'movimentacao-colar-v3912.js',
    'relatorio-dia-v3912.js': ROOT / 'relatorio-dia-v3912.js',
}

for nome, destino in arquivos.items():
    origem = SRC / nome
    if not origem.exists():
        raise SystemExit(f'Arquivo ausente: {origem}')
    shutil.copy2(origem, destino)

mov = ROOT / 'movimentacao.html'
rel = ROOT / 'relatorio-saidas.html'

if not mov.exists():
    raise SystemExit('movimentacao.html ausente')
if not rel.exists():
    raise SystemExit('relatorio-saidas.html ausente')

injecoes = {
    mov: '<script src="movimentacao-colar-v3912.js?v=3912"></script>',
    rel: '<script src="relatorio-dia-v3912.js?v=3912"></script>',
}

for pagina, tag in injecoes.items():
    html = pagina.read_text(encoding='utf-8')
    if tag not in html:
        if '</body>' not in html:
            raise SystemExit(f'</body> ausente em {pagina.name}')
        html = html.replace('</body>', f'    {tag}\n</body>', 1)
    pagina.write_text(html, encoding='utf-8')

# Forca cache novo para o APK atualizado nao reaproveitar paginas antigas.
sw = ROOT / 'service-worker.js'
if sw.exists():
    texto = sw.read_text(encoding='utf-8')
    texto = re.sub(r'seedcontrol-v3\.8-pwa-[A-Za-z0-9._-]+', 'seedcontrol-v3.8-pwa-3912', texto, count=1)
    sw.write_text(texto, encoding='utf-8')

validacoes = {
    ROOT / 'movimentacao-colar-v3912.js': ['seedcontrol-movimentacao-colar-v3912', '📋 Colar', 'Plugins.Clipboard'],
    ROOT / 'relatorio-dia-v3912.js': ['seedcontrol-relatorio-dia-v3912', 'Data da saída', 'Ver saídas do dia'],
    mov: ['movimentacao-colar-v3912.js?v=3912'],
    rel: ['relatorio-dia-v3912.js?v=3912'],
}

for arquivo, marcas in validacoes.items():
    texto = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in texto:
            raise SystemExit(f'Validacao falhou em {arquivo.name}: {marca}')

print('Correcao 3912 aplicada: colar em Destino/Observacao e Relatorio de Saidas filtrado somente por dia.')
