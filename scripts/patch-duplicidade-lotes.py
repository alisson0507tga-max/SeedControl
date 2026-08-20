from pathlib import Path

CADASTRO_GUARD = r'''// seedcontrol-duplicidade-cadastro-v384
(function () {
    function normalizar(valor) {
        return String(valor == null ? "" : valor).trim().toLowerCase();
    }

    function normalizarLote(valor) {
        const texto = String(valor == null ? "" : valor).trim().toLowerCase();
        if (/^\d+$/.test(texto)) return String(Number(texto));
        return texto;
    }

    function chave(lote) {
        return [
            normalizar(lote && lote.cultivar),
            normalizarLote(lote && lote.lote),
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
                lote: document.getElementById("lote")?.value || "",
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

EDITAR_GUARD = r'''// seedcontrol-duplicidade-edicao-v384
(function () {
    let chaveOriginal = "";

    function normalizar(valor) {
        return String(valor == null ? "" : valor).trim().toLowerCase();
    }

    function normalizarLote(valor) {
        const texto = String(valor == null ? "" : valor).trim().toLowerCase();
        if (/^\d+$/.test(texto)) return String(Number(texto));
        return texto;
    }

    function chave(lote) {
        return [
            normalizar(lote && lote.cultivar),
            normalizarLote(lote && lote.lote),
            normalizar(lote && lote.fazenda),
            normalizar(lote && lote.peneira),
            normalizar(lote && lote.talhao)
        ].join("|");
    }

    function valoresFormulario() {
        return {
            cultivar: document.getElementById("cultivar")?.value || "",
            lote: document.getElementById("lote")?.value || "",
            fazenda: document.getElementById("fazenda")?.value || "",
            peneira: document.getElementById("peneira")?.value || "",
            talhao: document.getElementById("talhao")?.value || ""
        };
    }

    function formularioPreenchido() {
        const atual = valoresFormulario();
        return Boolean(String(atual.cultivar).trim() || String(atual.lote).trim());
    }

    function capturarChaveOriginal() {
        if (chaveOriginal || !formularioPreenchido()) return;
        chaveOriginal = chave(valoresFormulario());
    }

    function agendarCapturaOriginal() {
        let tentativas = 0;
        const timer = setInterval(function () {
            tentativas += 1;
            capturarChaveOriginal();
            if (chaveOriginal || tentativas >= 30) clearInterval(timer);
        }, 50);
    }

    function idsDaUrl() {
        const params = new URLSearchParams(window.location.search);
        const nomes = ["id", "registro", "registroId", "loteId"];
        const ids = [];
        nomes.forEach(function (nome) {
            const valor = params.get(nome);
            if (valor != null && String(valor).trim()) ids.push(String(valor).trim());
        });
        return ids;
    }

    function indiceDaUrl() {
        const params = new URLSearchParams(window.location.search);
        for (const nome of ["index", "indice", "i"]) {
            const valor = params.get(nome);
            if (valor != null && /^\d+$/.test(String(valor))) return Number(valor);
        }
        return -1;
    }

    function instalarProtecaoEdicao() {
        const botao = document.getElementById("salvar");
        if (!botao || botao.dataset.seedcontrolDuplicidadeEdicao === "1") return;

        botao.dataset.seedcontrolDuplicidadeEdicao = "1";
        agendarCapturaOriginal();

        document.addEventListener("focusin", function () {
            capturarChaveOriginal();
        }, true);

        botao.addEventListener("click", function (evento) {
            capturarChaveOriginal();

            const candidato = valoresFormulario();
            const base = typeof carregarEstoque === "function"
                ? carregarEstoque()
                : [];

            const chaveCandidato = chave(candidato);
            const idsUrl = idsDaUrl();
            const indiceUrl = indiceDaUrl();
            let originalIgnorado = false;

            const duplicado = Array.isArray(base) && base.some(function (item, indice) {
                if (!item) return false;

                if (idsUrl.length && idsUrl.includes(String(item.id == null ? "" : item.id))) {
                    return false;
                }

                if (indiceUrl >= 0 && indice === indiceUrl) {
                    return false;
                }

                if (!originalIgnorado && chaveOriginal && chave(item) === chaveOriginal) {
                    originalIgnorado = true;
                    return false;
                }

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
for marcador in (
    "// seedcontrol-duplicidade-cadastro-v383",
    "// seedcontrol-duplicidade-cadastro-v384"
):
    if marcador in texto_cadastro:
        inicio = texto_cadastro.find(marcador)
        fim = texto_cadastro.find("\n\n", inicio)
        # A proteção antiga ocupa um IIFE no topo. Remove pelo fechamento conhecido.
        fechamento = texto_cadastro.find("})();", inicio)
        if fechamento != -1:
            texto_cadastro = texto_cadastro[fechamento + len("})();"):].lstrip("\n")
        break
cadastro.write_text(CADASTRO_GUARD + texto_cadastro, encoding="utf-8")

editar = Path("native/www/editar.js")
if editar.exists():
    texto_editar = editar.read_text(encoding="utf-8")
    for marcador in (
        "// seedcontrol-duplicidade-edicao-v383",
        "// seedcontrol-duplicidade-edicao-v384"
    ):
        if marcador in texto_editar:
            inicio = texto_editar.find(marcador)
            fechamento = texto_editar.find("})();", inicio)
            if fechamento != -1:
                texto_editar = texto_editar[fechamento + len("})();"):].lstrip("\n")
            break
    editar.write_text(EDITAR_GUARD + texto_editar, encoding="utf-8")

print("Proteção de duplicidade corrigida: edição ignora o próprio lote e aceita códigos alfanuméricos.")
