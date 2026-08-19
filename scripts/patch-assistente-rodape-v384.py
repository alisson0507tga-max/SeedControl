from pathlib import Path

ROOT = Path('native/www')
CSS = ROOT / 'assistente-v384.css'
JS = ROOT / 'assistente-v384.js'

for arquivo in (CSS, JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo não encontrado: {arquivo}')

css = CSS.read_text(encoding='utf-8')
marca_css = '/* seedcontrol-assistente-rodape-safe-v384 */'

bloco_css = r'''

/* seedcontrol-assistente-rodape-safe-v384 */
:root {
    --seed-assistente-nav-safe: 78px;
}

/* No Android com barra de 3 botões, o WebView pode desenhar por baixo da
   navegação do sistema. Reservamos esse espaço somente com teclado fechado. */
.assistente-v384-composer {
    padding-bottom: calc(12px + env(safe-area-inset-bottom) + var(--seed-assistente-nav-safe)) !important;
}

body.seed-assistente-teclado-aberto .assistente-v384-composer {
    padding-bottom: calc(10px + env(safe-area-inset-bottom)) !important;
}

body.seed-assistente-teclado-aberto {
    height: var(--seed-assistente-altura-visivel, 100dvh) !important;
    min-height: var(--seed-assistente-altura-visivel, 100dvh) !important;
}

@media (min-height: 900px) {
    :root { --seed-assistente-nav-safe: 82px; }
}
'''

if marca_css not in css:
    css += bloco_css
    CSS.write_text(css, encoding='utf-8')

js = JS.read_text(encoding='utf-8')
marca_js = '// seedcontrol-assistente-rodape-safe-v384'

bloco_js = r'''

// seedcontrol-assistente-rodape-safe-v384
(function () {
    "use strict";

    function atualizarAreaVisivel() {
        const vv = window.visualViewport;
        const alturaJanela = window.innerHeight || document.documentElement.clientHeight || 0;
        const alturaVisivel = vv ? vv.height : alturaJanela;
        const diferenca = Math.max(0, alturaJanela - alturaVisivel);
        const tecladoAberto = diferenca > 140;

        document.body.classList.toggle("seed-assistente-teclado-aberto", tecladoAberto);
        document.documentElement.style.setProperty(
            "--seed-assistente-altura-visivel",
            Math.max(320, Math.round(alturaVisivel)) + "px"
        );

        if (tecladoAberto) {
            const campo = document.getElementById("assistenteEntrada");
            if (campo === document.activeElement) {
                setTimeout(function () {
                    try { campo.scrollIntoView({ block: "nearest", inline: "nearest" }); } catch (_) {}
                }, 60);
            }
        }
    }

    function iniciarRodapeSeguro() {
        atualizarAreaVisivel();
        window.addEventListener("resize", atualizarAreaVisivel, { passive: true });
        window.addEventListener("orientationchange", atualizarAreaVisivel, { passive: true });
        if (window.visualViewport) {
            window.visualViewport.addEventListener("resize", atualizarAreaVisivel, { passive: true });
            window.visualViewport.addEventListener("scroll", atualizarAreaVisivel, { passive: true });
        }

        const campo = document.getElementById("assistenteEntrada");
        if (campo) {
            campo.addEventListener("focus", function () {
                setTimeout(atualizarAreaVisivel, 80);
            });
            campo.addEventListener("blur", function () {
                setTimeout(atualizarAreaVisivel, 80);
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarRodapeSeguro, { once: true });
    } else {
        iniciarRodapeSeguro();
    }
})();
'''

if marca_js not in js:
    js += bloco_js
    JS.write_text(js, encoding='utf-8')

css_final = CSS.read_text(encoding='utf-8')
js_final = JS.read_text(encoding='utf-8')

for marca in (marca_css, '--seed-assistente-nav-safe', 'seed-assistente-teclado-aberto'):
    if marca not in css_final:
        raise SystemExit(f'Marca CSS ausente: {marca}')

for marca in (marca_js, 'visualViewport', 'seed-assistente-teclado-aberto', 'assistenteEntrada'):
    if marca not in js_final:
        raise SystemExit(f'Marca JS ausente: {marca}')

print('Rodapé do Assistente corrigido para barra de navegação Android e teclado.')
