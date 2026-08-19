from pathlib import Path

ROOT = Path('native/www')
CADASTRO = ROOT / 'cadastro.html'
SCRIPT = ROOT / 'teclado-sugestoes-v384.js'

if not CADASTRO.exists():
    raise SystemExit('cadastro.html não encontrado.')

js = r'''// seedcontrol-teclado-sugestoes-v384
(function () {
    "use strict";

    function prepararCampo(campo) {
        if (!campo || campo.disabled || campo.readOnly) return;
        if (campo.tagName !== "INPUT" && campo.tagName !== "TEXTAREA") return;

        const tipo = String(campo.type || "text").toLowerCase();
        const textuais = ["text", "search", "email", "url", "tel"];

        if (campo.tagName === "INPUT" && !textuais.includes(tipo)) return;

        campo.setAttribute("autocomplete", "on");
        campo.setAttribute("autocorrect", "on");
        campo.setAttribute("spellcheck", "true");
        campo.setAttribute("autocapitalize", "words");

        if (campo.tagName === "INPUT" && (tipo === "text" || tipo === "search")) {
            campo.setAttribute("inputmode", "text");
        }
    }

    function prepararTodos() {
        document.querySelectorAll('input, textarea').forEach(prepararCampo);
    }

    function iniciar() {
        prepararTodos();

        document.addEventListener("focusin", function (evento) {
            prepararCampo(evento.target);
        }, true);

        const observador = new MutationObserver(prepararTodos);
        observador.observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    } else {
        iniciar();
    }
})();
'''

SCRIPT.write_text(js, encoding='utf-8')

html = CADASTRO.read_text(encoding='utf-8')
if 'teclado-sugestoes-v384.js' not in html:
    if '</body>' not in html:
        raise SystemExit('Não foi possível localizar </body> em cadastro.html')
    html = html.replace(
        '</body>',
        '    <script src="teclado-sugestoes-v384.js?v=3822"></script>\n</body>',
        1
    )
    CADASTRO.write_text(html, encoding='utf-8')

final = SCRIPT.read_text(encoding='utf-8')
for marca in ('autocomplete', 'autocorrect', 'spellcheck', 'autocapitalize', 'inputmode'):
    if marca not in final:
        raise SystemExit(f'Marca ausente no teclado-sugestoes-v384.js: {marca}')

if 'teclado-sugestoes-v384.js' not in CADASTRO.read_text(encoding='utf-8'):
    raise SystemExit('Script de sugestões não foi injetado no cadastro.html')

print('Sugestões/autocorreção do teclado habilitadas para campos textuais do Novo Lote.')
