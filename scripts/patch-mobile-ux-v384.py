from pathlib import Path

ROOT = Path('native/www')
SCRIPT = ROOT / 'mobile-ux-v384.js'

if not ROOT.exists():
    raise SystemExit('native/www não encontrado.')

js = r'''// seedcontrol-mobile-ux-v384
(function () {
    "use strict";

    let ultimoVoltarInicio = 0;

    function arquivoAtual() {
        const p = String(window.location.pathname || "").split("/").pop().toLowerCase();
        return p || "index.html";
    }

    function estaNoInicio() {
        const p = arquivoAtual();
        return p === "index.html" || p === "";
    }

    function mostrarAvisoSaida() {
        let aviso = document.getElementById("seedAvisoVoltarV384");
        if (!aviso) {
            aviso = document.createElement("div");
            aviso.id = "seedAvisoVoltarV384";
            aviso.textContent = "Pressione voltar novamente para sair";
            Object.assign(aviso.style, {
                position: "fixed",
                left: "50%",
                bottom: "calc(24px + env(safe-area-inset-bottom))",
                transform: "translateX(-50%) translateY(12px)",
                zIndex: "2147483647",
                maxWidth: "88vw",
                padding: "10px 14px",
                borderRadius: "12px",
                background: "rgba(5, 20, 28, .96)",
                border: "1px solid rgba(74, 222, 128, .35)",
                color: "#f8fafc",
                fontSize: "13px",
                boxShadow: "0 8px 24px rgba(0,0,0,.35)",
                opacity: "0",
                transition: "opacity .15s ease, transform .15s ease",
                pointerEvents: "none",
                textAlign: "center"
            });
            document.body.appendChild(aviso);
        }

        aviso.style.opacity = "1";
        aviso.style.transform = "translateX(-50%) translateY(0)";
        clearTimeout(aviso._timerSeed);
        aviso._timerSeed = setTimeout(function () {
            aviso.style.opacity = "0";
            aviso.style.transform = "translateX(-50%) translateY(12px)";
        }, 1600);
    }

    function voltarDentroDoApp(canGoBack) {
        if (!estaNoInicio()) {
            if (canGoBack || window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = "index.html";
            }
            return;
        }

        const agora = Date.now();
        const app = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;

        if (agora - ultimoVoltarInicio < 1800) {
            if (app && typeof app.exitApp === "function") {
                app.exitApp();
            }
            return;
        }

        ultimoVoltarInicio = agora;
        mostrarAvisoSaida();
    }

    async function ativarBotaoVoltarAndroid() {
        try {
            const app = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;
            if (!app || typeof app.addListener !== "function") return;

            await app.addListener("backButton", function (evento) {
                voltarDentroDoApp(!!(evento && evento.canGoBack));
            });
        } catch (erro) {
            console.warn("SeedControl: não foi possível registrar o botão Voltar do Android.", erro);
        }
    }

    function campoPodeAvancar(el) {
        if (!el || el.disabled || el.readOnly) return false;
        if (el.hidden || el.getAttribute("aria-hidden") === "true") return false;
        if (el.tabIndex < 0) return false;

        if (el.tagName === "INPUT") {
            const tipo = String(el.type || "text").toLowerCase();
            if (["hidden", "file", "checkbox", "radio", "button", "submit", "reset", "image"].includes(tipo)) {
                return false;
            }
        }

        return el.offsetParent !== null;
    }

    function camposNovoLote() {
        const todos = Array.from(document.querySelectorAll("input, select, textarea"));
        return todos.filter(campoPodeAvancar);
    }

    function avancarCampo(el) {
        const campos = camposNovoLote();
        const indice = campos.indexOf(el);
        if (indice < 0) return false;

        const proximo = campos[indice + 1];
        if (!proximo) {
            if (typeof el.blur === "function") el.blur();
            return true;
        }

        try {
            proximo.focus({ preventScroll: true });
        } catch (_) {
            proximo.focus();
        }

        if (proximo.tagName === "INPUT" && /^(text|search|tel|url|email|number|decimal)$/i.test(proximo.type || "text")) {
            try { proximo.select(); } catch (_) {}
        }

        try {
            proximo.scrollIntoView({ behavior: "smooth", block: "center", inline: "nearest" });
        } catch (_) {
            proximo.scrollIntoView();
        }

        return true;
    }

    function ativarEnterNovoLote() {
        if (arquivoAtual() !== "cadastro.html") return;

        const configurar = function () {
            const campos = camposNovoLote();
            campos.forEach(function (campo, indice) {
                if (campo.tagName === "INPUT" || campo.tagName === "TEXTAREA") {
                    campo.setAttribute("enterkeyhint", indice < campos.length - 1 ? "next" : "done");
                }
            });
        };

        configurar();

        document.addEventListener("keydown", function (evento) {
            if (evento.key !== "Enter" || evento.shiftKey || evento.ctrlKey || evento.altKey || evento.metaKey) return;
            const alvo = evento.target;
            if (!campoPodeAvancar(alvo)) return;

            evento.preventDefault();
            avancarCampo(alvo);
        }, true);

        const observador = new MutationObserver(function () {
            configurar();
        });
        observador.observe(document.body, { childList: true, subtree: true });
    }

    function iniciar() {
        ativarBotaoVoltarAndroid();
        ativarEnterNovoLote();
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
    texto = pagina.read_text(encoding='utf-8')
    if 'mobile-ux-v384.js' in texto:
        continue
    if '</body>' not in texto:
        continue
    texto = texto.replace(
        '</body>',
        '    <script src="mobile-ux-v384.js?v=3821"></script>\n</body>',
        1
    )
    pagina.write_text(texto, encoding='utf-8')
    injetadas += 1

cadastro = ROOT / 'cadastro.html'
index = ROOT / 'index.html'

if not cadastro.exists() or not index.exists():
    raise SystemExit('cadastro.html ou index.html não encontrado.')

if 'mobile-ux-v384.js' not in cadastro.read_text(encoding='utf-8'):
    raise SystemExit('Script de UX móvel não foi injetado no Novo Lote.')

if 'mobile-ux-v384.js' not in index.read_text(encoding='utf-8'):
    raise SystemExit('Script de UX móvel não foi injetado no Dashboard.')

final = SCRIPT.read_text(encoding='utf-8')
for marca in ('backButton', 'enterkeyhint', 'avancarCampo', 'Pressione voltar novamente para sair'):
    if marca not in final:
        raise SystemExit(f'Marca ausente no mobile-ux-v384.js: {marca}')

print(f'UX móvel aplicada: botão Voltar Android + Enter Próximo Campo. HTMLs atualizados: {injetadas}.')
