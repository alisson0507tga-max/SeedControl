from pathlib import Path
import shutil

ROOT = Path('native/www')
SRC = Path('correcoes-3909')

ordem_src = SRC / 'estoque-ordem-v3909.js'
nota_src = SRC / 'nota-visualizador-v3909.js'
ordem_dst = ROOT / 'estoque-ordem-v3909.js'
nota_dst = ROOT / 'nota-visualizador-v3909.js'

for arq in (ordem_src, nota_src):
    if not arq.exists():
        raise SystemExit(f'Arquivo 3909 ausente: {arq}')

if not ROOT.exists():
    raise SystemExit('native/www nao encontrado')

shutil.copy2(ordem_src, ordem_dst)
shutil.copy2(nota_src, nota_dst)

# Ordem: precisa carregar no cadastro para carimbar lotes novos e no estoque para reordenar os cards.
for nome in ('cadastro.html', 'estoque.html'):
    pagina = ROOT / nome
    if not pagina.exists():
        raise SystemExit(f'Pagina ausente: {nome}')
    html = pagina.read_text(encoding='utf-8')
    if 'estoque-ordem-v3909.js' not in html:
        tag = '<script src="estoque-ordem-v3909.js?v=3909"></script>'
        html = html.replace('</body>', tag + '\n</body>', 1) if '</body>' in html else html + '\n' + tag
        pagina.write_text(html, encoding='utf-8')

# Nota: no Estoque e na tela da cultivar/detalhe.
paginas_nota = [ROOT / 'estoque.html']
paginas_nota.extend(sorted(ROOT.glob('*cultivar*.html')))

injetadas = 0
for pagina in paginas_nota:
    if not pagina.exists():
        continue
    html = pagina.read_text(encoding='utf-8')
    if 'nota-visualizador-v3909.js' not in html:
        tag = '<script src="nota-visualizador-v3909.js?v=3909"></script>'
        html = html.replace('</body>', tag + '\n</body>', 1) if '</body>' in html else html + '\n' + tag
        pagina.write_text(html, encoding='utf-8')
    injetadas += 1

if injetadas < 1:
    raise SystemExit('Nenhuma pagina recebeu o visualizador 3909')

checks = {
    ordem_dst: ('seedcontrol-estoque-ordem-real-v3909', 'data_desc', 'carimbarNovos', 'ordenarAgora'),
    nota_dst: ('seedcontrol-nota-visualizador-robusto-v3909', 'notaEntradaFoto', 'Ver nota', 'seedcontrol_entrada_comercial_notas_2026'),
}
for arquivo, marcas in checks.items():
    conteudo = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in conteudo:
            raise SystemExit(f'Marca ausente em {arquivo.name}: {marca}')

for nome in ('cadastro.html', 'estoque.html'):
    html = (ROOT / nome).read_text(encoding='utf-8')
    if 'estoque-ordem-v3909.js?v=3909' not in html:
        raise SystemExit(f'Ordem 3909 nao entrou em {nome}')

estoque_html = (ROOT / 'estoque.html').read_text(encoding='utf-8')
if 'nota-visualizador-v3909.js?v=3909' not in estoque_html:
    raise SystemExit('Visualizador 3909 nao entrou no estoque.html')

print('Correcoes 3909 aplicadas: ordem real por cadastro e visualizador da nota no Estoque/Cultivar.')
