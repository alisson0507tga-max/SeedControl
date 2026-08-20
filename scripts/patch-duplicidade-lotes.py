from pathlib import Path

GUARD = r'''// seedcontrol-duplicidade-universal-v3902
(function () {
    "use strict";

    if (window.__seedcontrolDuplicidadeUniversalV3902) return;
    window.__seedcontrolDuplicidadeUniversalV3902 = true;

    let chaveOriginalEdicao = "";

    function normalizar(valor) {
        return String(valor == null ? "" : valor).trim().toLowerCase();
    }

    function normalizarLote(valor) {
        const texto = normalizar(valor);
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

    function modoEdicao() {
        const botao = document.getElementById("salvar");
        const textoBotao = normalizar(botao && botao.textContent);
        const caminho = normalizar(window.location.pathname);
        const params = new URLSearchParams(window.location.search);

        return (
            caminho.includes("editar") ||
            textoBotao.includes("alter") ||
            params.has("editar") ||
            params.has("registro") ||
            params.has("registroId") ||
            params.has("loteId")
        );
    }

    function capturarOriginal() {
        if (!modoEdicao() || chaveOriginalEdicao || !formularioPreenchido()) return;
        chaveOriginalEdicao = chave(valoresFormulario());
    }

    function agendarCapturaOriginal() {
        let tentativas = 0;
        const timer = setInterval(function () {
            tentativas += 1;
            capturarOriginal();
            if (chaveOriginalEdicao || tentativas >= 50) clearInterval(timer);
        }, 60);
    }

    function idsDaUrl() {
        const params = new URLSearchParams(window.location.search);
        const nomes = ["id", "registro", "registroId", "loteId"];
        const ids = [];

        nomes.forEach(function (nome) {
            const valor = params.get(nome);
            if (valor != null && String(valor).trim()) {
                ids.push(String(valor).trim());
            }
        });

        return ids;
    }

    function indiceDaUrl() {
        const params = new URLSearchParams(window.location.search);
        for (const nome of ["index", "indice", "i"]) {
            const valor = params.get(nome);
            if (valor != null && /^\d+$/.test(String(valor))) {
                return Number(valor);
            }
        }
        return -1;
    }

    function instalar() {
        const botao = document.getElementById("salvar");
        if (!botao || botao.dataset.seedcontrolDuplicidadeUniversalV3902 === "1") return;

        botao.dataset.seedcontrolDuplicidadeUniversalV3902 = "1";

        agendarCapturaOriginal();
        document.addEventListener("focusin", capturarOriginal, true);

        botao.addEventListener("click", function (evento) {
            capturarOriginal();

            const base = typeof carregarEstoque === "function"
                ? carregarEstoque()
                : [];

            if (!Array.isArray(base)) return;

            const candidato = valoresFormulario();
            const chaveCandidato = chave(candidato);
            const editando = modoEdicao();
            const idsUrl = idsDaUrl();
            const indiceUrl = indiceDaUrl();
            let originalIgnorado = false;

            const duplicado = base.some(function (item, indice) {
                if (!item) return false;

                if (editando) {
                    if (idsUrl.length && idsUrl.includes(String(item.id == null ? "" : item.id))) {
                        return false;
                    }

                    if (indiceUrl >= 0 && indice === indiceUrl) {
                        return false;
                    }

                    if (!originalIgnorado && chaveOriginalEdicao && chave(item) === chaveOriginalEdicao) {
                        originalIgnorado = true;
                        return false;
                    }
                }

                return chave(item) === chaveCandidato;
            });

            if (!duplicado) return;

            evento.preventDefault();
            evento.stopImmediatePropagation();

            if (editando) {
                alert("Já existe OUTRO lote cadastrado com a mesma cultivar, fazenda, peneira e talhão.");
            } else {
                alert("Este lote já está cadastrado com a mesma cultivar, fazenda, peneira e talhão.");
            }
        }, true);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", instalar);
    } else {
        instalar();
    }
})();

'''


def remover_guardas_antigas(texto: str) -> str:
    marcadores = (
        "// seedcontrol-duplicidade-cadastro-v383",
        "// seedcontrol-duplicidade-cadastro-v384",
        "// seedcontrol-duplicidade-edicao-v383",
        "// seedcontrol-duplicidade-edicao-v384",
        "// seedcontrol-duplicidade-universal-v3902",
    )

    alterou = True
    while alterou:
        alterou = False
        posicoes = [(texto.find(m), m) for m in marcadores if texto.find(m) != -1]
        if not posicoes:
            break

        inicio, _ = min(posicoes, key=lambda x: x[0])
        fechamento = texto.find("})();", inicio)
        if fechamento == -1:
            raise SystemExit("Protecao de duplicidade antiga encontrada sem fechamento IIFE.")

        texto = texto[:inicio] + texto[fechamento + len("})();"):]
        texto = texto.lstrip("\n")
        alterou = True

    return texto


for nome in ("cadastro.js", "editar.js"):
    path = Path("native/www") / nome
    if not path.exists():
        if nome == "cadastro.js":
            raise SystemExit("cadastro.js nao encontrado em native/www")
        continue

    texto = path.read_text(encoding="utf-8")
    texto = remover_guardas_antigas(texto)
    path.write_text(GUARD + texto, encoding="utf-8")

print("Protecao universal de duplicidade v3902 aplicada em Cadastro e Editar.")
