from pathlib import Path

ROOT = Path("native/www")
JS = ROOT / "relatorios.js"

if not JS.exists():
    raise SystemExit("relatorios.js não encontrado")

js = JS.read_text(encoding="utf-8")

# 1) Corrige o salvamento local: não abre mais o Share depois de salvar.
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

# 2) Deixa o PDF mais parecido com o relatório de saídas mostrado no app:
# faixa verde no topo, título branco centralizado e conteúdo abaixo.
if "SEEDCONTROL_PDF_VISUAL_3935" not in js:
    ass_pdf = "async function exportarPDF()"
    p_ini = js.find(ass_pdf)
    if p_ini >= 0:
        p_abre = js.find("{", p_ini)
        nivel = 0
        p_fim = None
        for i in range(p_abre, len(js)):
            ch = js[i]
            if ch == "{":
                nivel += 1
            elif ch == "}":
                nivel -= 1
                if nivel == 0:
                    p_fim = i + 1
                    break

        if p_fim:
            bloco = js[p_ini:p_fim]
            pos_new = bloco.find("new jsPDF")
            if pos_new >= 0:
                pos_ponto = bloco.find(";", pos_new)
                if pos_ponto >= 0:
                    visual = r'''

    // SEEDCONTROL_PDF_VISUAL_3935
    const seedLarguraPagina = pdf.internal.pageSize.getWidth();
    pdf.setFillColor(20, 125, 54);
    pdf.rect(10, 7, seedLarguraPagina - 20, 12, "F");
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(13);
    pdf.text("RELATÓRIO - SEEDCONTROL", seedLarguraPagina / 2, 15, { align: "center" });
    pdf.setTextColor(0, 0, 0);
'''
                    bloco = bloco[:pos_ponto + 1] + visual + bloco[pos_ponto + 1:]
                    js = js[:p_ini] + bloco + js[p_fim:]

JS.write_text(js, encoding="utf-8")

final = JS.read_text(encoding="utf-8")
for trecho in (
    'directory: "DOCUMENTS"',
    'Documentos/SeedControl/Relatorios/',
    'async function seedRelatorioSalvarECompartilhar',
):
    if trecho not in final:
        raise SystemExit(f"Validação falhou: {trecho}")

print("Relatórios 3935: salva em Documentos sem Share e PDF com cabeçalho verde estilo relatório de saídas.")
