from pathlib import Path

CADASTRO_GUARD = r'''// seedcontrol-duplicidade-cadastro-v383
(function () {
    function normalizar(valor) {
        return String(valor == null ? "" : valor).trim().toLowerCase();
    }

    function chave(lote) {
        return [
            normalizar(lote && lote.cultivar),
            String(Number(lote && lote.lote) || ""),
            normalizar(lote && lote.fazenda),
            normalizar(lote && lote.peneira),
            normalizar(lote && lote.talhao)
        ].join("|");
    }

    function instalarProtecaoCadastro() {
        const botao = document.getElementById("salvar");
        if (!botao || botao.dataset.seedcontrolDuplicidadeCadastro === "1") return;

        botao.dataset.seedcontrolDuplicidadeCadastro = "1";

        botao.addEventListener("click", function (evento) {
            const candidato = {
                cultivar: document.getElementById("cultivar")?.value || "",
                lote: Number(document.getElementById("lote")?.value),
                fazenda: document.getElementById("fazenda")?.value || "",
                peneira: document.getElementById("peneira")?.value || "",
                talhao: document.getElementById("talhao")?.value || ""
            };

            const base = typeof carregarEstoque === "function"
                ? carregarEstoque()
                : [];

            const chaveCandidato = chave(candidato);
            const duplicado = Array.isArray(base) && base.some(function (item) {
                return item && chave(item) === chaveCandidato;
            });

            if (!duplicado) return;

            evento.preventDefault();
            evento.stopImmediatePropagation();

            alert(
                "Este lote já está cadastrado com a mesma cultivar, fazenda, peneira e talhão."
            );
        }, true);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", instalarProtecaoCadastro);
    } else {
        instalarProtecaoCadastro();
    }
})();

'''

EDITAR_GUARD = r'''// seedcontrol-duplicidade-edicao-v383
(function () {
    function normalizar(valor) {
        return String(valor == null ? "" : valor).trim().toLowerCase();
    }

    function chave(lote) {
        return [
            normalizar(lote && lote.cultivar),
            String(Number(lote && lote.lote) || ""),
            normalizar(lote && lote.fazenda),
            normalizar(lote && lote.peneira),
            normalizar(lote && lote.talhao)
        ].join("|");
    }

    function instalarProtecaoEdicao() {
        const botao = document.getElementById("salvar");
        if (!botao || botao.dataset.seedcontrolDuplicidadeEdicao === "1") return;

        botao.dataset.seedcontrolDuplicidadeEdicao = "1";

        botao.addEventListener("click", function (evento) {
            const parametrosDuplicidade = new URLSearchParams(window.location.search);
            const idAtual = Number(parametrosDuplicidade.get("id"));

            const candidato = {
                cultivar: document.getElementById("cultivar")?.value || "",
                lote: Number(document.getElementById("lote")?.value),
                fazenda: document.getElementById("fazenda")?.value || "",
                peneira: document.getElementById("peneira")?.value || "",
                talhao: document.getElementById("talhao")?.value || ""
            };

            const base = typeof carregarEstoque === "function"
                ? carregarEstoque()
                : [];

            const chaveCandidato = chave(candidato);
            const duplicado = Array.isArray(base) && base.some(function (item) {
                if (!item) return false;
                if (Number(item.id) === idAtual) return false;
                return chave(item) === chaveCandidato;
            });

            if (!duplicado) return;

            evento.preventDefault();
            evento.stopImmediatePropagation();

            alert(
                "Já existe outro lote cadastrado com a mesma cultivar, fazenda, peneira e talhão."
            );
        }, true);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", instalarProtecaoEdicao);
    } else {
        instalarProtecaoEdicao();
    }
})();

'''

cadastro = Path("native/www/cadastro.js")
if not cadastro.exists():
    raise SystemExit("cadastro.js não encontrado em native/www")

texto_cadastro = cadastro.read_text(encoding="utf-8")
if "// seedcontrol-duplicidade-cadastro-v383" not in texto_cadastro:
    cadastro.write_text(CADASTRO_GUARD + texto_cadastro, encoding="utf-8")

editar = Path("native/www/editar.js")
if editar.exists():
    texto_editar = editar.read_text(encoding="utf-8")
    if "// seedcontrol-duplicidade-edicao-v383" not in texto_editar:
        editar.write_text(EDITAR_GUARD + texto_editar, encoding="utf-8")

print("Proteção de duplicidade aplicada no cadastro e na edição.")
