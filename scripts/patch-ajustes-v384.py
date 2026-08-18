from pathlib import Path

ROOT = Path("native/www")
INDEX = ROOT / "index.html"
RELATORIOS = ROOT / "relatorios.js"
SW = ROOT / "service-worker.js"

for arquivo in (INDEX, RELATORIOS, SW):
    if not arquivo.exists():
        raise SystemExit(f"Arquivo não encontrado: {arquivo}")

# ============================================================
# 1) DASHBOARD: REMOVER CARD GRANDE DO ASSISTENTE
# Mantém somente o botão do Assistente dentro de Ações rápidas.
# ============================================================

index = INDEX.read_text(encoding="utf-8")

inicio = index.find('<section class="assistant-card"')
if inicio == -1:
    raise SystemExit("Card grande do Assistente não encontrado no Dashboard.")

fim = index.find('</section>', inicio)
if fim == -1:
    raise SystemExit("Fim do card grande do Assistente não encontrado.")

fim += len('</section>')
index = index[:inicio] + index[fim:]

if '<section class="assistant-card"' in index:
    raise SystemExit("Card grande do Assistente ainda existe após o patch.")

if "Assistente SeedControl" not in index or "assistente.html" not in index:
    raise SystemExit("Botão normal do Assistente foi removido por engano.")

INDEX.write_text(index, encoding="utf-8")

# ============================================================
# 2) RELATÓRIOS: COMPARTILHAMENTO DE ARQUIVO ÚNICO
# O plugin oficial aceita URL local de arquivo no Android.
# ============================================================

js = RELATORIOS.read_text(encoding="utf-8")

antigo_share = '        files: [temporario.uri],\n'
novo_share = '        url: temporario.uri,\n'

if antigo_share in js:
    js = js.replace(antigo_share, novo_share, 1)
elif '        url: temporario.uri,\n' not in js:
    raise SystemExit("Bloco de compartilhamento do relatório não encontrado.")

# ============================================================
# 3) CLIQUES PROTEGIDOS
# Captura qualquer erro da função inteira e mostra ao usuário.
# ============================================================

bloco_pdf_antigo = '''        botaoPDF.addEventListener(
            "click",
            exportarPDF
        );'''

bloco_pdf_novo = r'''        botaoPDF.addEventListener(
            "click",
            async function (evento) {

                evento.preventDefault();

                try {

                    await exportarPDF();

                } catch (erro) {

                    console.error(
                        "Erro completo ao exportar PDF:",
                        erro
                    );

                    alert(
                        "Falha ao exportar PDF. " +
                        (erro && erro.message
                            ? erro.message
                            : "Erro desconhecido.")
                    );

                }

            }
        );'''

bloco_excel_antigo = '''        botaoExcel.addEventListener(
            "click",
            exportarExcel
        );'''

bloco_excel_novo = r'''        botaoExcel.addEventListener(
            "click",
            async function (evento) {

                evento.preventDefault();

                try {

                    await exportarExcel();

                } catch (erro) {

                    console.error(
                        "Erro completo ao exportar Excel:",
                        erro
                    );

                    alert(
                        "Falha ao exportar Excel. " +
                        (erro && erro.message
                            ? erro.message
                            : "Erro desconhecido.")
                    );

                }

            }
        );'''

if bloco_pdf_antigo not in js:
    raise SystemExit("Listener original do botão PDF não encontrado.")
if bloco_excel_antigo not in js:
    raise SystemExit("Listener original do botão Excel não encontrado.")

js = js.replace(bloco_pdf_antigo, bloco_pdf_novo, 1)
js = js.replace(bloco_excel_antigo, bloco_excel_novo, 1)

# Marca esta correção para validação da build.
marcador = '// seedcontrol-exportacao-protegida-v384\n'
if marcador not in js:
    js = marcador + js

RELATORIOS.write_text(js, encoding="utf-8")

# ============================================================
# 4) FORÇAR ATUALIZAÇÃO DOS ARQUIVOS DO APP
# A troca do cache garante que relatorios.js novo seja carregado
# após atualizar o APK por cima da versão anterior.
# ============================================================

sw = SW.read_text(encoding="utf-8")

if 'seedcontrol-v3.8-pwa-12' in sw:
    sw = sw.replace(
        'seedcontrol-v3.8-pwa-12',
        'seedcontrol-v3.8-pwa-13',
        1
    )
elif 'seedcontrol-v3.8-pwa-13' not in sw:
    raise SystemExit("Versão esperada do cache do Service Worker não encontrada.")

SW.write_text(sw, encoding="utf-8")

# ============================================================
# VALIDAÇÕES
# ============================================================

index_final = INDEX.read_text(encoding="utf-8")
js_final = RELATORIOS.read_text(encoding="utf-8")
sw_final = SW.read_text(encoding="utf-8")

validacoes = [
    ('<section class="assistant-card"', index_final, False),
    ('Assistente SeedControl', index_final, True),
    ('assistente.html', index_final, True),
    ('seedcontrol-exportacao-protegida-v384', js_final, True),
    ('async function (evento)', js_final, True),
    ('await exportarPDF()', js_final, True),
    ('await exportarExcel()', js_final, True),
    ('url: temporario.uri', js_final, True),
    ('files: [temporario.uri]', js_final, False),
    ('seedcontrol-v3.8-pwa-13', sw_final, True),
]

for trecho, conteudo, deve_existir in validacoes:
    existe = trecho in conteudo
    if existe != deve_existir:
        estado = "existir" if deve_existir else "não existir"
        raise SystemExit(f"Validação falhou: {trecho} deveria {estado}.")

print(
    "Ajustes v3.8.4 aplicados: card grande do Assistente removido, "
    "exportação protegida e compartilhamento por URL local ativado."
)
