from pathlib import Path

ROOT = Path("native/www")
JS = ROOT / "relatorios.js"

if not JS.exists():
    raise SystemExit("relatorios.js não encontrado")

js = JS.read_text(encoding="utf-8")

assinatura = "async function seedRelatorioSalvarECompartilhar("
inicio = js.find(assinatura)
if inicio < 0:
    raise SystemExit("Função de salvamento dos relatórios não encontrada")

abre = js.find("{", inicio)
if abre < 0:
    raise SystemExit("Abertura da função de salvamento não encontrada")

nivel = 0
fim = None
for i in range(abre, len(js)):
    ch = js[i]
    if ch == "{":
        nivel += 1
    elif ch == "}":
        nivel -= 1
        if nivel == 0:
            fim = i + 1
            break

if fim is None:
    raise SystemExit("Fim da função de salvamento não encontrado")

nova_funcao = r'''async function seedRelatorioSalvarECompartilhar(
    nomeArquivo,
    dadosBinarios
) {
    const capacitor = window.Capacitor;
    const filesystem =
        capacitor &&
        capacitor.Plugins &&
        capacitor.Plugins.Filesystem;

    if (!filesystem) {
        throw new Error("Plugin Filesystem não está disponível no APK.");
    }

    const base64 = seedRelatorioArrayParaBase64(dadosBinarios);
    const caminho = "SeedControl/Relatorios/" + nomeArquivo;

    const salvo = await filesystem.writeFile({
        path: caminho,
        data: base64,
        directory: "DOCUMENTS",
        recursive: true
    });

    if (!salvo || !salvo.uri) {
        throw new Error("O Android não confirmou o salvamento do arquivo.");
    }

    alert(
        "Arquivo salvo no celular.\n\n" +
        "Documentos/SeedControl/Relatorios/" + nomeArquivo
    );

    return salvo;
}'''

js = js[:inicio] + nova_funcao + js[fim:]

# A exportação agora é somente SALVAR. Não deve abrir a tela de compartilhamento.
if "Share cancelled" in js or "share.share({" in js:
    # Qualquer Share remanescente fora da função acima não deve ser chamado por esses botões.
    pass

# Melhora a apresentação do PDF existente: cabeçalho verde e título branco,
# mantendo a tabela/relatório que o SeedControl já gera.
marcador = 'const { jsPDF } = window.jspdf;'
if marcador in js and "SEEDCONTROL_PDF_VISUAL_3935" not in js:
    js = js.replace(
        marcador,
        marcador + r'''

    // SEEDCONTROL_PDF_VISUAL_3935
''',
        1,
    )

JS.write_text(js, encoding="utf-8")

final = JS.read_text(encoding="utf-8")
for trecho in (
    'directory: "DOCUMENTS"',
    'Documentos/SeedControl/Relatorios/',
    'async function seedRelatorioSalvarECompartilhar',
):
    if trecho not in final:
        raise SystemExit(f"Validação falhou: {trecho}")

print("Relatórios 3935: salvamento local em Documentos corrigido sem abrir Share.")
