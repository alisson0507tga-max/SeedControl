from pathlib import Path
import re

ROOT = Path("native/www")
PLANILHA = ROOT / "planilha.js"

if not PLANILHA.exists():
    raise SystemExit("planilha.js não encontrado.")

js = PLANILHA.read_text(encoding="utf-8")

nova_funcao = r'''
async function exportarPlanilhaExcel() {

    const registros =
        obterRegistrosAtuaisPlanilha();

    if (!registros.length) {
        alert("Não há lotes para exportar.");
        return;
    }

    const textoOriginal =
        btnExportarExcel
            ? btnExportarExcel.textContent
            : "";

    try {

        if (btnExportarExcel) {
            btnExportarExcel.disabled = true;
            btnExportarExcel.textContent = "⏳ Preparando Excel...";
        }

        await carregarBibliotecaExcel();

        const resumo =
            resumirEstoque(registros);

        const cabecalhos = [
            "CULTIVAR",
            "PENEIRA",
            "LOTES",
            "QUANTIDADE BAGS ",
            "Kgs(MÉDIA)",
            "SACAS(60kgs)",
            "UMIDADE %",
            "TEMPERATURA °C",
            "PMS ( g )",
            "FAZENDA ",
            "TALHÃO",
            "SECAGEM"
        ];

        const linhas =
            registros.map(item => [
                item.cultivar || "",
                item.peneira || "",
                Number(item.lote) || 0,
                Number(item.bags) || 0,
                Number(item.kgsMedia) || 0,
                Number(item.sacas60kg) || 0,
                Number(item.umidade) || 0,
                Number(item.temperatura) || 0,
                Number(item.pms) || 0,
                item.fazenda || "",
                item.talhao || "",
                obterTextoSecagemPlanilha(item.secagem)
            ]);

        const dados = [
            ["CONTROLE DE SEMENTES DE SOJA"],
            cabecalhos,
            ...linhas,
            [
                "",
                "",
                "",
                Number(resumo.totalBags) || 0,
                Number(resumo.totalKgsMedia) || 0,
                Number(resumo.totalSacas60kg) || 0,
                "",
                "",
                "",
                "",
                "",
                ""
            ]
        ];

        const worksheet =
            XLSX.utils.aoa_to_sheet(dados);

        worksheet["!merges"] = [{
            s: { r: 0, c: 0 },
            e: { r: 0, c: 11 }
        }];

        worksheet["!cols"] = [
            { wch: 24 },
            { wch: 10 },
            { wch: 8 },
            { wch: 16 },
            { wch: 14 },
            { wch: 15 },
            { wch: 12 },
            { wch: 16 },
            { wch: 12 },
            { wch: 19 },
            { wch: 11 },
            { wch: 10 }
        ];

        const totalLinhas = registros.length + 3;
        worksheet["!rows"] = [];
        worksheet["!rows"][0] = { hpt: 26 };
        worksheet["!rows"][1] = { hpt: 22 };
        for (let i = 2; i < totalLinhas; i++) {
            worksheet["!rows"][i] = { hpt: 19 };
        }

        const COR_TITULO = "4DD0E1";
        const COR_AZUL_CLARO = "E0F7FA";
        const COR_BRANCO = "FFFFFF";
        const COR_TEXTO = "111111";
        const COR_BORDA = "CFD8DC";

        function bordaFiel() {
            const lado = {
                style: "thin",
                color: { rgb: COR_BORDA }
            };
            return {
                top: lado,
                bottom: lado,
                left: lado,
                right: lado
            };
        }

        function garantirCelula(linha, coluna) {
            const endereco =
                XLSX.utils.encode_cell({
                    r: linha,
                    c: coluna
                });

            if (!worksheet[endereco]) {
                worksheet[endereco] = {
                    t: "s",
                    v: ""
                };
            }

            return worksheet[endereco];
        }

        for (let coluna = 0; coluna < 12; coluna++) {
            const celula = garantirCelula(0, coluna);
            celula.s = {
                fill: {
                    patternType: "solid",
                    fgColor: { rgb: COR_TITULO }
                },
                font: {
                    name: "Oswald",
                    bold: true,
                    sz: 14,
                    color: { rgb: "000000" }
                },
                alignment: {
                    horizontal: "center",
                    vertical: "center"
                },
                border: bordaFiel()
            };
        }

        for (let coluna = 0; coluna < 12; coluna++) {
            const celula = garantirCelula(1, coluna);
            celula.s = {
                fill: {
                    patternType: "solid",
                    fgColor: { rgb: COR_AZUL_CLARO }
                },
                font: {
                    name: "Oswald",
                    bold: true,
                    sz: 10,
                    color: { rgb: "000000" }
                },
                alignment: {
                    horizontal: "center",
                    vertical: "center",
                    wrapText: true
                },
                border: bordaFiel()
            };
        }

        registros.forEach(function (_, indice) {
            const linha = indice + 2;
            const corLinha =
                indice % 2 === 0
                    ? COR_BRANCO
                    : COR_AZUL_CLARO;

            for (let coluna = 0; coluna < 12; coluna++) {
                const celula = garantirCelula(linha, coluna);

                celula.s = {
                    fill: {
                        patternType: "solid",
                        fgColor: { rgb: corLinha }
                    },
                    font: {
                        name: "Oswald",
                        bold: true,
                        sz: coluna === 11 ? 12 : 9,
                        color: { rgb: COR_TEXTO }
                    },
                    alignment: {
                        horizontal: "center",
                        vertical: "center",
                        wrapText: false
                    },
                    border: bordaFiel()
                };

                if (coluna === 2 || coluna === 3 || coluna === 4) {
                    celula.z = "0";
                }

                if (coluna === 5) {
                    celula.z = "0.#";
                }

                if (coluna === 6 || coluna === 7) {
                    celula.z = "0.0";
                }

                if (coluna === 8) {
                    celula.z = "0.00";
                }
            }
        });

        const linhaTotal = registros.length + 2;

        for (let coluna = 0; coluna < 12; coluna++) {
            const celula = garantirCelula(linhaTotal, coluna);

            celula.s = {
                fill: {
                    patternType: "solid",
                    fgColor: { rgb: COR_BRANCO }
                },
                font: {
                    name: "Oswald",
                    bold: coluna >= 3 && coluna <= 5,
                    sz: 10,
                    color: { rgb: COR_TEXTO }
                },
                alignment: {
                    horizontal: "center",
                    vertical: "center"
                },
                border: bordaFiel()
            };
        }

        garantirCelula(linhaTotal, 3).z = "0";
        garantirCelula(linhaTotal, 4).z = "0";
        garantirCelula(linhaTotal, 5).z = "0.#";

        delete worksheet["!autofilter"];

        const workbook =
            XLSX.utils.book_new();

        XLSX.utils.book_append_sheet(
            workbook,
            worksheet,
            "Controle de Sementes"
        );

        const hoje = new Date();
        const dataNome =
            hoje.getFullYear() +
            "-" +
            String(hoje.getMonth() + 1).padStart(2, "0") +
            "-" +
            String(hoje.getDate()).padStart(2, "0");

        const nomeArquivoExcel =
            "SeedControl_Controle_Sementes_" +
            dataNome +
            ".xlsx";

        if (
            typeof seedPlanilhaPlataformaNativa === "function" &&
            seedPlanilhaPlataformaNativa()
        ) {
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
        }

    } catch (erro) {

        console.error(
            "Erro ao exportar Excel fiel:",
            erro
        );

        alert(
            "Não foi possível exportar o Excel. " +
            (erro && erro.message
                ? erro.message
                : "Erro desconhecido.")
        );

    } finally {

        if (btnExportarExcel) {
            btnExportarExcel.disabled = false;
            btnExportarExcel.textContent =
                textoOriginal ||
                "📗 Exportar Excel";
        }
    }
}
'''

padrao = re.compile(
    r'async function exportarPlanilhaExcel\(\)\s*\{.*?\n\}\n\n\n// ==========================================\n// EXPORTAR PDF',
    re.S
)

substituto = nova_funcao + '\n\n// ==========================================\n// EXPORTAR PDF'

js_novo, qtd = padrao.subn(substituto, js, count=1)
if qtd != 1:
    raise SystemExit("Não foi possível substituir exportarPlanilhaExcel().")

if "// seedcontrol-planilha-fiel-soja2026-v3830" not in js_novo:
    js_novo = "// seedcontrol-planilha-fiel-soja2026-v3830\n" + js_novo

PLANILHA.write_text(js_novo, encoding="utf-8")

final = PLANILHA.read_text(encoding="utf-8")
for trecho in (
    "seedcontrol-planilha-fiel-soja2026-v3830",
    '"CONTROLE DE SEMENTES DE SOJA"',
    '"QUANTIDADE BAGS "',
    '"SACAS(60kgs)"',
    'e: { r: 0, c: 11 }',
    'name: "Oswald"',
    'const COR_TITULO = "4DD0E1"',
    'const COR_AZUL_CLARO = "E0F7FA"',
    'delete worksheet["!autofilter"]',
    '"SECAGEM"',
    'SeedControl_Controle_Sementes_'
):
    if trecho not in final:
        raise SystemExit(f"Validação da planilha fiel falhou: {trecho}")

trecho_excel = final.split("// EXPORTAR EXCEL", 1)[-1].split("// EXPORTAR PDF", 1)[0]
if '"MÉTODO / PESO BAG"' in trecho_excel:
    raise SystemExit("A exportação fiel ainda contém a 13ª coluna de método/peso.")

print("Excel fiel à referência Soja 2026 preparado: 12 colunas, título, cabeçalho, alternância, formatos e totais.")
