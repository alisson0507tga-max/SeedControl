from pathlib import Path

ROOT = Path('native/www')
SCRIPT = ROOT / 'teclado-sugestoes-v384.js'

if not ROOT.exists():
    raise SystemExit('native/www não encontrado.')

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
        campo.setAttribute("autocapitalize", "sentences");

        if (campo.tagName === "INPUT" && (tipo === "text" || tipo === "search")) {
            campo.setAttribute("inputmode", "text");
        }

        // No Assistente, reforça explicitamente o comportamento de texto normal
        // para o Android/WebView oferecer a faixa de sugestões do teclado.
        if (campo.id === "assistenteEntrada") {
            campo.setAttribute("autocomplete", "on");
            campo.setAttribute("autocorrect", "on");
            campo.setAttribute("spellcheck", "true");
            campo.setAttribute("autocapitalize", "sentences");
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

injetadas = 0
for pagina in ROOT.glob('*.html'):
    html = pagina.read_text(encoding='utf-8')
    if 'teclado-sugestoes-v384.js' in html:
        continue
    if '</body>' not in html:
        continue
    html = html.replace(
        '</body>',
        '    <script src="teclado-sugestoes-v384.js?v=3823"></script>\n</body>',
        1
    )
    pagina.write_text(html, encoding='utf-8')
    injetadas += 1

cadastro = ROOT / 'cadastro.html'
assistente = ROOT / 'assistente-chat-v384.html'

for pagina in (cadastro, assistente):
    if not pagina.exists():
        raise SystemExit(f'Página obrigatória não encontrada: {pagina.name}')
    if 'teclado-sugestoes-v384.js' not in pagina.read_text(encoding='utf-8'):
        raise SystemExit(f'Script de sugestões não foi injetado em {pagina.name}')

final = SCRIPT.read_text(encoding='utf-8')
for marca in ('autocomplete', 'autocorrect', 'spellcheck', 'autocapitalize', 'inputmode', 'assistenteEntrada'):
    if marca not in final:
        raise SystemExit(f'Marca ausente no teclado-sugestoes-v384.js: {marca}')

print(f'Sugestões/autocorreção habilitadas em todas as telas textuais. HTMLs atualizados: {injetadas}.')
