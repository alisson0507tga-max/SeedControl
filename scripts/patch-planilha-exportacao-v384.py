from pathlib import Path
import re

ROOT = Path("native/www")
PLANILHA = ROOT / "planilha.js"
SW = ROOT / "service-worker.js"

for arquivo in (PLANILHA, SW):
    if not arquivo.exists():
        raise SystemExit(f"Arquivo não encontrado: {arquivo}")

js = PLANILHA.read_text(encoding="utf-8")
sw = SW.read_text(encoding="utf-8")

# Bibliotecas da Planilha passam a ser locais dentro do APK.
substituicoes = {
    "https://cdn.jsdelivr.net/npm/xlsx-js-style@1.2.0/dist/xlsx.bundle.js": "vendor/xlsx-js-style.bundle.js",
    "https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js": "vendor/jspdf.umd.min.js",
    "https://cdn.jsdelivr.net/npm/jspdf-autotable@3.8.2/dist/jspdf.plugin.autotable.min.js": "vendor/jspdf.plugin.autotable.min.js",
}

for antigo, novo in substituicoes.items():
    if antigo not in js:
        raise SystemExit(f"URL original não encontrada em planilha.js: {antigo}")
    js = js.replace(antigo, novo, 1)

helper = r'''
// seedcontrol-planilha-exportacao-nativa-v384

function seedPlanilhaPlataformaNativa() {
    const capacitor = window.Capacitor;
    return Boolean(
        capacitor &&
        typeof capacitor.isNativePlatform === "function" &&
        capacitor.isNativePlatform()
    );
}

function seedPlanilhaArrayParaBase64(dados) {
    const bytes = dados instanceof Uint8Array
        ? dados
        : new Uint8Array(dados);

    let binario = "";
    const tamanhoBloco = 0x8000;

    for (let inicio = 0; inicio < bytes.length; inicio += tamanhoBloco) {
        const bloco = bytes.subarray(
            inicio,
            Math.min(inicio + tamanhoBloco, bytes.length)
        );
        binario += String.fromCharCode.apply(null, bloco);
    }

    return btoa(binario);
}

async function seedPlanilhaSalvarECompartilhar(nomeArquivo, dadosBinarios) {
    const capacitor = window.Capacitor;
    const filesystem =
        capacitor && capacitor.Plugins && capacitor.Plugins.Filesystem;
    const share =
        capacitor && capacitor.Plugins && capacitor.Plugins.Share;

    if (!filesystem) {
        throw new Error("Plugin Filesystem não está disponível no APK.");
    }

    if (!share) {
        throw new Error("Plugin de compartilhamento não está disponível no APK.");
    }

    const base64 = seedPlanilhaArrayParaBase64(dadosBinarios);

    const salvo = await filesystem.writeFile({
        path: "SeedControl/Planilhas/" + nomeArquivo,
        data: base64,
        directory: "DOCUMENTS",
        recursive: true
    });

    if (!salvo || !salvo.uri) {
        throw new Error("O Android não confirmou o salvamento do arquivo.");
    }

    const temporario = await filesystem.writeFile({
        path: "SeedControlShare/" + nomeArquivo,
        data: base64,
        directory: "CACHE",
        recursive: true
    });

    if (!temporario || !temporario.uri) {
        throw new Error("Não foi possível preparar o arquivo para compartilhar.");
    }

    await share.share({
        title: nomeArquivo,
        text: "Planilha gerada pelo SeedControl",
        url: temporario.uri,
        dialogTitle: "Compartilhar planilha"
    });

    return salvo;
}

'''

marcador_excel = "// ==========================================\n// EXPORTAR EXCEL\n// =========================================="
if "seedcontrol-planilha-exportacao-nativa-v384" not in js:
    if marcador_excel not in js:
        raise SystemExit("Marcador EXPORTAR EXCEL não encontrado em planilha.js")
    js = js.replace(marcador_excel, helper + marcador_excel, 1)

padrao_excel = re.compile(
    r'''\n\s*XLSX\.writeFile\(\s*\n\s*workbook,\s*\n\s*"SeedControl_Controle_Sementes_"\s*\+\s*\n\s*dataNome\s*\+\s*\n\s*"\.xlsx"\s*\n\s*\);''',
    re.MULTILINE,
)

novo_excel = r'''

        const nomeArquivoExcel =
            "SeedControl_Controle_Sementes_" +
            dataNome +
            ".xlsx";

        if (seedPlanilhaPlataformaNativa()) {

            const dadosExcel =
                XLSX.write(
                    workbook,
                    {
                        bookType: "xlsx",
                        type: "array"
                    }
                );

            await seedPlanilhaSalvarECompartilhar(
                nomeArquivoExcel,
                dadosExcel
            );

        } else {

            XLSX.writeFile(
                workbook,
                nomeArquivoExcel
            );

        }'''

js, qtd_excel = padrao_excel.subn(novo_excel, js, count=1)
if qtd_excel != 1:
    raise SystemExit("Não foi possível substituir o salvamento Excel da Planilha.")

salvar_pdf_antigo = '''        pdf.save(\n            "SeedControl_Controle_Sementes.pdf"\n        );'''

salvar_pdf_novo = r'''        const nomeArquivoPDF =
            "SeedControl_Controle_Sementes.pdf";

        if (seedPlanilhaPlataformaNativa()) {

            const dadosPDF =
                pdf.output("arraybuffer");

            await seedPlanilhaSalvarECompartilhar(
                nomeArquivoPDF,
                dadosPDF
            );

        } else {

            pdf.save(
                nomeArquivoPDF
            );

        }'''

if salvar_pdf_antigo not in js:
    raise SystemExit("Não foi possível localizar o salvamento PDF da Planilha.")
js = js.replace(salvar_pdf_antigo, salvar_pdf_novo, 1)

# Mensagens de erro mostram a causa real, em vez de culpar apenas a internet.
js = js.replace(
    '''        alert(\n            "Não foi possível gerar o Excel. Verifique sua conexão com a internet."\n        );''',
    r'''        alert(
            "Não foi possível exportar o Excel. " +
            (erro && erro.message
                ? erro.message
                : "Erro desconhecido.")
        );''',
    1,
)

js = js.replace(
    '''        alert(\n            "Não foi possível gerar o PDF. Verifique sua conexão com a internet."\n        );''',
    r'''        alert(
            "Não foi possível exportar o PDF. " +
            (erro && erro.message
                ? erro.message
                : "Erro desconhecido.")
        );''',
    1,
)

PLANILHA.write_text(js, encoding="utf-8")

# Força o WebView/Service Worker a abandonar a versão antiga de planilha.js.
if "seedcontrol-v3.8-pwa-13" in sw:
    sw = sw.replace(
        "seedcontrol-v3.8-pwa-13",
        "seedcontrol-v3.8-pwa-14",
        1,
    )
elif "seedcontrol-v3.8-pwa-14" not in sw:
    raise SystemExit("Cache esperado pwa-13/pwa-14 não encontrado.")

SW.write_text(sw, encoding="utf-8")

js_final = PLANILHA.read_text(encoding="utf-8")
sw_final = SW.read_text(encoding="utf-8")

validacoes = [
    "seedcontrol-planilha-exportacao-nativa-v384",
    "vendor/xlsx-js-style.bundle.js",
    "vendor/jspdf.umd.min.js",
    "vendor/jspdf.plugin.autotable.min.js",
    "SeedControl/Planilhas/",
    'directory: "DOCUMENTS"',
    'directory: "CACHE"',
    "capacitor.Plugins.Share",
    "url: temporario.uri",
    'XLSX.write(',
    'type: "array"',
    'pdf.output("arraybuffer")',
]

for trecho in validacoes:
    if trecho not in js_final:
        raise SystemExit(f"Validação da Planilha falhou: {trecho}")

if "seedcontrol-v3.8-pwa-14" not in sw_final:
    raise SystemExit("Service Worker não foi atualizado para pwa-14.")

print(
    "Planilha de Lotes corrigida: Excel/PDF locais, salvamento em Documentos e compartilhamento Android."
)
