from pathlib import Path


def corrigir_estoque():
    caminho = Path("native/www/estoque.js")
    texto = caminho.read_text(encoding="utf-8")

    ancora_botao = '''<div class="acoes-registro">


<button
    type="button"
    class="btn-editar"'''

    novo_botao = '''<button
    type="button"
    class="btn-movimentar"
    data-action="movimentar"
    data-id="${item.id}"
    style="
        width:100%;
        margin-top:16px;
        background:#16a34a;
    "
>
    📦 Movimentar Estoque
</button>


<div class="acoes-registro">


<button
    type="button"
    class="btn-editar"'''

    if 'data-action="movimentar"' not in texto:
        if ancora_botao not in texto:
            raise SystemExit("Não foi possível inserir o botão Movimentar no estoque.js")
        texto = texto.replace(ancora_botao, novo_botao, 1)

    ancora_handler = '''        // ===============================
        // QR CODE
        // ===============================

        if (
            botao.dataset.action ===
            "qrcode"
        ) {'''

    novo_handler = '''        // ===============================
        // MOVIMENTAR
        // ===============================

        if (
            botao.dataset.action ===
            "movimentar"
        ) {

            window.location.href =
                "movimentacao.html?id=" +
                encodeURIComponent(
                    id
                );

            return;

        }


        // ===============================
        // QR CODE
        // ===============================

        if (
            botao.dataset.action ===
            "qrcode"
        ) {'''

    if 'botao.dataset.action ===\n            "movimentar"' not in texto:
        if ancora_handler not in texto:
            raise SystemExit("Não foi possível inserir a ação Movimentar no estoque.js")
        texto = texto.replace(ancora_handler, novo_handler, 1)

    caminho.write_text(texto, encoding="utf-8")


def corrigir_cultivar():
    caminho = Path("native/www/cultivar.js")
    texto = caminho.read_text(encoding="utf-8")

    ancora = '''                <button
                    type="button"
                    onclick="window.location.href='cadastro.html?id=${item.id}'"
                >
                    ✏️ Editar
                </button>'''

    novo = '''                <button
                    type="button"
                    onclick="window.location.href='movimentacao.html?id=${item.id}'"
                    style="
                        background:#16a34a;
                        margin-bottom:10px;
                    "
                >
                    📦 Movimentar Estoque
                </button>


                <button
                    type="button"
                    onclick="window.location.href='cadastro.html?id=${item.id}'"
                >
                    ✏️ Editar
                </button>'''

    if "📦 Movimentar Estoque" not in texto:
        if ancora not in texto:
            raise SystemExit("Não foi possível inserir o botão Movimentar no cultivar.js")
        texto = texto.replace(ancora, novo, 1)

    caminho.write_text(texto, encoding="utf-8")


corrigir_estoque()
corrigir_cultivar()
print("Acesso à movimentação corrigido.")
