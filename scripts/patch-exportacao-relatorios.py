from pathlib import Path
import re

ROOT = Path("native/www")
HTML = ROOT / "relatorios.html"
JS = ROOT / "relatorios.js"

if not HTML.exists() or not JS.exists():
    raise SystemExit("relatorios.html ou relatorios.js não encontrado.")

html = HTML.read_text(encoding="utf-8")
js = JS.read_text(encoding="utf-8")

# Mantém jsPDF e XLSX dentro do APK, sem depender de CDN durante o uso.
html, qtd_pdf = re.subn(
    r'<script\s+src="https://cdnjs\.cloudflare\.com/ajax/libs/jspdf/[^\"]+/jspdf\.umd\.min\.js"></script>',
    '<script src="vendor/jspdf.umd.min.js"></script>',
    html,
    count=1,
)
html, qtd_xlsx = re.subn(
    r'<script\s+src="https://cdn\.jsdelivr\.net/npm/xlsx[^\"]*"></script>',
    '<script src="vendor/xlsx.full.min.js"></script>',
    html,
    count=1,
)

if qtd_pdf != 1:
    raise SystemExit("Não foi possível trocar o jsPDF remoto pelo arquivo local.")
if qtd_xlsx != 1:
    raise SystemExit("Não foi possível trocar o XLSX remoto pelo arquivo local.")

helper = r'''
// ===============================
// SALVAMENTO NATIVO DE RELATÓRIOS
// APK / CAPACITOR
// ===============================

function seedRelatorioPlataformaNativa() {

    const capacitor = window.Capacitor;

    return Boolean(
        capacitor &&
        typeof capacitor.isNativePlatform === "function" &&
        capacitor.isNativePlatform()
    );

}


function seedRelatorioArrayParaBase64(dados) {

    const bytes =
        dados instanceof Uint8Array
            ? dados
            : new Uint8Array(dados);

    let binario = "";
    const tamanhoBloco = 0x8000;

    for (
        let inicio = 0;
        inicio < bytes.length;
        inicio += tamanhoBloco
    ) {
        const bloco = bytes.subarray(
            inicio,
            Math.min(inicio + tamanhoBloco, bytes.length)
        );

        binario += String.fromCharCode.apply(
            null,
            bloco
        );
    }

    return btoa(binario);

}


async function seedRelatorioSalvarNativo(
    nomeArquivo,
    dadosBinarios
) {

    const capacitor = window.Capacitor;
    const filesystem =
        capacitor &&
        capacitor.Plugins &&
        capacitor.Plugins.Filesystem;

    if (!filesystem) {
        throw new Error(
            "Plugin Filesystem não está disponível no APK."
        );
    }

    const base64 =
        seedRelatorioArrayParaBase64(
            dadosBinarios
        );

    const caminho =
        "SeedControl/Relatorios/" +
        nomeArquivo;

    const resultado =
        await filesystem.writeFile({
            path: caminho,
            data: base64,
            directory: "DOCUMENTS",
            recursive: true
        });

    if (!resultado || !resultado.uri) {
        throw new Error(
            "O Android não confirmou o salvamento do relatório."
        );
    }

    alert(
        "Relatório salvo com sucesso!\n\n" +
        "Arquivo: " + nomeArquivo +
        "\nLocal: Documentos/SeedControl/Relatorios"
    );

    return resultado;

}
'''

marcador_pdf = "// ===============================\n// EXPORTAR PDF\n// ==============================="
if "seedRelatorioSalvarNativo" not in js:
    if marcador_pdf not in js:
        raise SystemExit("Marcador de exportação PDF não encontrado.")
    js = js.replace(
        marcador_pdf,
        helper + "\n\n" + marcador_pdf,
        1,
    )

js, qtd_func_pdf = re.subn(
    r'function\s+exportarPDF\s*\(\s*\)\s*\{',
    'async function exportarPDF() {',
    js,
    count=1,
)
if qtd_func_pdf != 1:
    raise SystemExit("Função exportarPDF não encontrada.")

salvar_pdf_antigo = '''    pdf.save(
        "Relatorio_SeedControl.pdf"
    );'''
salvar_pdf_novo = r'''    const nomeArquivoPDF =
        "Relatorio_SeedControl.pdf";

    if (seedRelatorioPlataformaNativa()) {

        try {

            const dadosPDF =
                pdf.output("arraybuffer");

            await seedRelatorioSalvarNativo(
                nomeArquivoPDF,
                dadosPDF
            );

            return;

        } catch (erro) {

            console.error(
                "Falha ao salvar PDF:",
                erro
            );

            alert(
                "Não foi possível salvar o PDF.\n\n" +
                (erro && erro.message
                    ? erro.message
                    : "Erro desconhecido.")
            );

            return;

        }

    }

    pdf.save(
        nomeArquivoPDF
    );'''

if salvar_pdf_antigo not in js:
    raise SystemExit("Bloco final de salvamento do PDF não encontrado.")
js = js.replace(
    salvar_pdf_antigo,
    salvar_pdf_novo,
    1,
)

js, qtd_func_excel = re.subn(
    r'function\s+exportarExcel\s*\(\s*\)\s*\{',
    'async function exportarExcel() {',
    js,
    count=1,
)
if qtd_func_excel != 1:
    raise SystemExit("Função exportarExcel não encontrada.")

salvar_excel_antigo = '''    XLSX.writeFile(
        workbook,
        "Relatorio_SeedControl.xlsx"
    );'''
salvar_excel_novo = r'''    const nomeArquivoExcel =
        "Relatorio_SeedControl.xlsx";

    if (seedRelatorioPlataformaNativa()) {

        try {

            const dadosExcel =
                XLSX.write(
                    workbook,
                    {
                        bookType: "xlsx",
                        type: "array"
                    }
                );

            await seedRelatorioSalvarNativo(
                nomeArquivoExcel,
                dadosExcel
            );

            return;

        } catch (erro) {

            console.error(
                "Falha ao salvar Excel:",
                erro
            );

            alert(
                "Não foi possível salvar o Excel.\n\n" +
                (erro && erro.message
                    ? erro.message
                    : "Erro desconhecido.")
            );

            return;

        }

    }

    XLSX.writeFile(
        workbook,
        nomeArquivoExcel
    );'''

if salvar_excel_antigo not in js:
    raise SystemExit("Bloco final de salvamento do Excel não encontrado.")
js = js.replace(
    salvar_excel_antigo,
    salvar_excel_novo,
    1,
)

HTML.write_text(html, encoding="utf-8")
JS.write_text(js, encoding="utf-8")

# Validações objetivas do patch.
html_final = HTML.read_text(encoding="utf-8")
js_final = JS.read_text(encoding="utf-8")

validacoes = [
    ('vendor/jspdf.umd.min.js', html_final),
    ('vendor/xlsx.full.min.js', html_final),
    ('async function exportarPDF()', js_final),
    ('async function exportarExcel()', js_final),
    ('SeedControl/Relatorios/', js_final),
    ('directory: "DOCUMENTS"', js_final),
    ('pdf.output("arraybuffer")', js_final),
    ('type: "array"', js_final),
    ('Não foi possível salvar o PDF.\\n\\n', js_final),
    ('Não foi possível salvar o Excel.\\n\\n', js_final),
]

for trecho, conteudo in validacoes:
    if trecho not in conteudo:
        raise SystemExit(
            f"Validação da exportação falhou: {trecho}"
        )

print(
    "Exportação PDF/Excel corrigida para APK: bibliotecas locais e salvamento em Documentos/SeedControl/Relatorios."
)
