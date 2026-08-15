from pathlib import Path

arquivo = Path("native/www/backup.js")

if not arquivo.exists():
    raise SystemExit("backup.js não encontrado em native/www")

texto = arquivo.read_text(encoding="utf-8")

inicio = texto.find("function fazerBackup()")
fim_marcador = "// ===============================\n// RESTAURAR BACKUP"
fim = texto.find(fim_marcador)

if inicio == -1 or fim == -1 or fim <= inicio:
    raise SystemExit("Não foi possível localizar a função fazerBackup() no backup.js")

nova_funcao = r'''async function fazerBackup() {

    try {

        // ===============================
        // SERVIÇO CENTRAL
        // ===============================

        const dados = gerarBackup();

        if (
            !dados ||
            !Array.isArray(dados.estoque) ||
            !Array.isArray(dados.historico)
        ) {
            throw new Error("Estrutura de backup inválida.");
        }

        const agora = new Date();

        const dataArquivo = [
            agora.getFullYear(),
            String(agora.getMonth() + 1).padStart(2, "0"),
            String(agora.getDate()).padStart(2, "0")
        ].join("-");

        const horaArquivo = [
            String(agora.getHours()).padStart(2, "0"),
            String(agora.getMinutes()).padStart(2, "0"),
            String(agora.getSeconds()).padStart(2, "0")
        ].join("-");

        const nomeArquivo =
            "SeedControl_Backup_" +
            dataArquivo +
            "_" +
            horaArquivo +
            ".json";

        const conteudo = JSON.stringify(dados, null, 2);

        // ===============================
        // APK / CAPACITOR
        // Salva de verdade na pasta pública
        // Documentos/SeedControl
        // ===============================

        const capacitor = window.Capacitor;
        const plataformaNativa =
            capacitor &&
            typeof capacitor.isNativePlatform === "function" &&
            capacitor.isNativePlatform();

        if (plataformaNativa) {

            const filesystem =
                capacitor.Plugins &&
                capacitor.Plugins.Filesystem;

            if (!filesystem) {
                throw new Error(
                    "Plugin Filesystem não está disponível no APK."
                );
            }

            const caminho =
                "SeedControl/" + nomeArquivo;

            const resultado =
                await filesystem.writeFile({
                    path: caminho,
                    data: conteudo,
                    directory: "DOCUMENTS",
                    encoding: "utf8",
                    recursive: true
                });

            if (!resultado || !resultado.uri) {
                throw new Error(
                    "O Android não confirmou o salvamento do arquivo."
                );
            }

            alert(
                "Backup salvo com sucesso!\n\n" +
                "Lotes: " + dados.estoque.length +
                "\nHistórico: " + dados.historico.length +
                "\n\nArquivo: " + nomeArquivo +
                "\nLocal: Documentos/SeedControl"
            );

            return;
        }

        // ===============================
        // NAVEGADOR / PWA
        // Mantém o download tradicional
        // ===============================

        const blob = new Blob(
            [conteudo],
            { type: "application/json;charset=utf-8" }
        );

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = nomeArquivo;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        setTimeout(function () {
            URL.revokeObjectURL(url);
        }, 1000);

        alert(
            "Backup criado com sucesso!\n\n" +
            "Lotes: " + dados.estoque.length +
            "\nHistórico: " + dados.historico.length +
            "\n\nGuarde este arquivo em local seguro."
        );

    } catch (erro) {

        console.error(
            "Erro ao gerar backup:",
            erro
        );

        alert(
            "Não foi possível salvar o backup.\n\n" +
            (erro && erro.message
                ? erro.message
                : "Erro desconhecido.")
        );
    }
}


'''

novo_texto = texto[:inicio] + nova_funcao + texto[fim:]
arquivo.write_text(novo_texto, encoding="utf-8")

print("backup.js corrigido para salvamento nativo no Android")
