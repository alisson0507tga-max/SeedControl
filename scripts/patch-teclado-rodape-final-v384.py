from pathlib import Path

ROOT = Path('native/www')
CSS = ROOT / 'seed-teclado-final-v3825.css'
JS = ROOT / 'seed-teclado-final-v3825.js'

if not ROOT.exists():
    raise SystemExit('native/www não encontrado.')

css = r'''/* seedcontrol-teclado-final-v3825 */

/* O Android pode desenhar o WebView por baixo da barra de navegação.
   Esta regra é nova e fica em arquivo próprio para não depender de cache antigo. */
body.assistente-v384-body {
    height: 100dvh !important;
    min-height: 100dvh !important;
    padding-bottom: 62px !important;
    box-sizing: border-box !important;
}

body.assistente-v384-body.seed-teclado-aberto-v3825 {
    padding-bottom: 0 !important;
}

body.assistente-v384-body .assistente-v384-main {
    min-height: 0 !important;
}

body.assistente-v384-body .assistente-v384-composer {
    position: relative !important;
    z-index: 30 !important;
    padding-bottom: 10px !important;
}

.seed-sugestoes-v3825 {
    position: fixed;
    left: 8px;
    right: 8px;
    bottom: 8px;
    z-index: 2147483600;
    display: none;
    align-items: center;
    gap: 7px;
    min-height: 46px;
    padding: 6px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    scrollbar-width: none;
    border: 1px solid rgba(148, 163, 184, .28);
    border-radius: 14px;
    background: rgba(7, 24, 31, .98);
    box-shadow: 0 8px 26px rgba(0, 0, 0, .34);
}

.seed-sugestoes-v3825::-webkit-scrollbar { display: none; }
.seed-sugestoes-v3825.ativo { display: flex; }

.seed-sugestoes-v3825 button {
    flex: 0 0 auto;
    min-height: 34px !important;
    margin: 0 !important;
    padding: 6px 11px !important;
    border: 1px solid rgba(74, 222, 128, .30) !important;
    border-radius: 10px !important;
    background: rgba(17, 91, 49, .82) !important;
    color: #f3fff6 !important;
    font-size: 12px !important;
    font-weight: 650 !important;
    line-height: 1.1 !important;
    white-space: nowrap;
    box-shadow: none !important;
}

.seed-sugestoes-v3825 button.seed-colar-v3825 {
    border-color: rgba(96, 165, 250, .38) !important;
    background: rgba(22, 74, 112, .88) !important;
}

/* Com o teclado fechado a barra de sugestões fica escondida. Com teclado aberto,
   o plugin nativo faz o WebView redimensionar e a barra fica acima do teclado. */
body:not(.seed-teclado-aberto-v3825) .seed-sugestoes-v3825 {
    display: none !important;
}
'''

js = r'''// seedcontrol-teclado-final-v3825
(function () {
    "use strict";

    let campoAtivo = null;
    let tecladoAberto = false;
    let textoClipboard = "";
    let barra = null;

    const TERMOS = [
        "estoque", "bags", "bag", "lote", "lotes", "cultivar", "cultivares",
        "fazenda", "talhão", "peneira", "umidade", "temperatura", "PMS",
        "total", "quanto", "quantas", "temos", "tenho", "entrada", "saída"
    ];

    function plugin(nome) {
        try {
            return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins[nome];
        } catch (_) {
            return null;
        }
    }

    function ehCampoTexto(el) {
        if (!el || el.disabled || el.readOnly) return false;
        if (el.tagName === "TEXTAREA") return true;
        if (el.tagName !== "INPUT") return false;
        return ["text", "search", "email", "url", "tel"].includes(String(el.type || "text").toLowerCase());
    }

    function estoqueAtual() {
        try {
            if (typeof window.carregarEstoque === "function") {
                const e = window.carregarEstoque();
                return Array.isArray(e) ? e : [];
            }
        } catch (_) {}

        for (const chave of ["estoque", "seedcontrol_estoque", "lotes"]) {
            try {
                const valor = JSON.parse(localStorage.getItem(chave) || "[]");
                if (Array.isArray(valor) && valor.length) return valor;
            } catch (_) {}
        }
        return [];
    }

    function unicos(lista) {
        return [...new Set(lista.map(v => String(v == null ? "" : v).trim()).filter(Boolean))];
    }

    function prefixoAtual() {
        if (!campoAtivo) return "";
        const valor = String(campoAtivo.value || "");
        const pos = typeof campoAtivo.selectionStart === "number" ? campoAtivo.selectionStart : valor.length;
        const antes = valor.slice(0, pos);
        const m = antes.match(/([^\s,.;:!?()\[\]{}]+)$/);
        return m ? m[1].toLowerCase() : "";
    }

    function sugestoesDoCampo() {
        const estoque = estoqueAtual();
        const id = String(campoAtivo && campoAtivo.id || "").toLowerCase();
        let lista = [];

        if (id.includes("cultivar")) lista = unicos(estoque.map(x => x.cultivar));
        else if (id.includes("peneira")) lista = unicos(estoque.map(x => x.peneira));
        else if (id.includes("fazenda")) lista = unicos(estoque.map(x => x.fazenda));
        else if (id.includes("talhao") || id.includes("talhão")) lista = unicos(estoque.map(x => x.talhao));
        else lista = TERMOS.concat(unicos(estoque.map(x => x.cultivar))).concat(unicos(estoque.map(x => x.fazenda)));

        const p = prefixoAtual();
        if (p) {
            const comeca = lista.filter(v => String(v).toLowerCase().startsWith(p));
            const contem = lista.filter(v => !comeca.includes(v) && String(v).toLowerCase().includes(p));
            lista = comeca.concat(contem);
        }

        return unicos(lista).slice(0, 5);
    }

    async function lerClipboard() {
        textoClipboard = "";
        const clip = plugin("Clipboard");
        if (clip && typeof clip.read === "function") {
            try {
                const r = await clip.read();
                textoClipboard = String(r && r.value || "").trim();
                return;
            } catch (_) {}
        }

        try {
            if (navigator.clipboard && typeof navigator.clipboard.readText === "function") {
                textoClipboard = String(await navigator.clipboard.readText() || "").trim();
            }
        } catch (_) {}
    }

    function inserirTexto(texto, substituirPalavra) {
        if (!campoAtivo) return;
        const valor = String(campoAtivo.value || "");
        let ini = typeof campoAtivo.selectionStart === "number" ? campoAtivo.selectionStart : valor.length;
        let fim = typeof campoAtivo.selectionEnd === "number" ? campoAtivo.selectionEnd : ini;

        if (substituirPalavra && ini === fim) {
            const antes = valor.slice(0, ini);
            const m = antes.match(/([^\s,.;:!?()\[\]{}]+)$/);
            if (m) ini -= m[1].length;
        }

        const novo = valor.slice(0, ini) + texto + valor.slice(fim);
        campoAtivo.value = novo;
        const pos = ini + texto.length;
        try { campoAtivo.setSelectionRange(pos, pos); } catch (_) {}
        campoAtivo.dispatchEvent(new Event("input", { bubbles: true }));
        campoAtivo.focus();
        renderizar();
    }

    function criarBarra() {
        if (barra) return barra;
        barra = document.createElement("div");
        barra.id = "seedSugestoesV3825";
        barra.className = "seed-sugestoes-v3825";
        barra.setAttribute("aria-label", "Sugestões e área de transferência");
        document.body.appendChild(barra);
        return barra;
    }

    function botao(texto, classe, acao) {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = texto;
        if (classe) b.className = classe;
        b.addEventListener("pointerdown", function (e) { e.preventDefault(); });
        b.addEventListener("click", acao);
        return b;
    }

    function renderizar() {
        criarBarra();
        barra.innerHTML = "";

        if (!tecladoAberto || !ehCampoTexto(campoAtivo)) {
            barra.classList.remove("ativo");
            return;
        }

        if (textoClipboard) {
            const preview = textoClipboard.replace(/\s+/g, " ").slice(0, 22);
            barra.appendChild(botao("📋 " + preview + (textoClipboard.length > 22 ? "…" : ""), "seed-colar-v3825", function () {
                inserirTexto(textoClipboard, false);
            }));
        } else {
            barra.appendChild(botao("📋 Colar", "seed-colar-v3825", async function () {
                await lerClipboard();
                if (textoClipboard) inserirTexto(textoClipboard, false);
                else renderizar();
            }));
        }

        sugestoesDoCampo().forEach(function (s) {
            barra.appendChild(botao(String(s), "", function () {
                inserirTexto(String(s), true);
            }));
        });

        barra.classList.add("ativo");
    }

    function setTeclado(aberto) {
        tecladoAberto = !!aberto;
        document.body.classList.toggle("seed-teclado-aberto-v3825", tecladoAberto);
        if (!tecladoAberto) {
            textoClipboard = "";
            if (barra) barra.classList.remove("ativo");
        } else {
            setTimeout(function () {
                lerClipboard().finally(renderizar);
            }, 80);
        }
    }

    async function ligarKeyboardNativo() {
        const kb = plugin("Keyboard");
        if (!kb || typeof kb.addListener !== "function") return false;
        try {
            await kb.addListener("keyboardWillShow", function () { setTeclado(true); });
            await kb.addListener("keyboardDidShow", function () { setTeclado(true); });
            await kb.addListener("keyboardWillHide", function () { setTeclado(false); });
            await kb.addListener("keyboardDidHide", function () { setTeclado(false); });
            return true;
        } catch (_) {
            return false;
        }
    }

    function ligarFallbackViewport() {
        const base = Math.max(window.innerHeight || 0, document.documentElement.clientHeight || 0);
        function conferir() {
            const atual = window.visualViewport ? window.visualViewport.height : (window.innerHeight || 0);
            setTeclado(base - atual > 140 || (!!campoAtivo && document.activeElement === campoAtivo && atual < base * 0.82));
        }
        if (window.visualViewport) window.visualViewport.addEventListener("resize", conferir, { passive: true });
        window.addEventListener("resize", conferir, { passive: true });
    }

    function iniciar() {
        criarBarra();

        document.addEventListener("focusin", function (e) {
            if (!ehCampoTexto(e.target)) return;
            campoAtivo = e.target;
            campoAtivo.setAttribute("autocomplete", "on");
            campoAtivo.setAttribute("autocorrect", "on");
            campoAtivo.setAttribute("spellcheck", "true");
            setTimeout(function () { lerClipboard().finally(renderizar); }, 120);
        }, true);

        document.addEventListener("input", function (e) {
            if (e.target === campoAtivo) renderizar();
        }, true);

        document.addEventListener("focusout", function (e) {
            if (e.target !== campoAtivo) return;
            setTimeout(function () {
                if (document.activeElement !== campoAtivo && !ehCampoTexto(document.activeElement)) {
                    campoAtivo = null;
                    if (barra) barra.classList.remove("ativo");
                }
            }, 140);
        }, true);

        ligarKeyboardNativo().then(function (ok) {
            if (!ok) ligarFallbackViewport();
        });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    else iniciar();
})();
'''

CSS.write_text(css, encoding='utf-8')
JS.write_text(js, encoding='utf-8')

# Injeta arquivos NOVOS no fim do body/head para vencer cache de versões anteriores.
htmls = 0
for pagina in ROOT.glob('*.html'):
    texto = pagina.read_text(encoding='utf-8')

    if 'seed-teclado-final-v3825.css' not in texto and '</head>' in texto:
        texto = texto.replace('</head>', '    <link rel="stylesheet" href="seed-teclado-final-v3825.css?v=3825">\n</head>', 1)

    if 'seed-teclado-final-v3825.js' not in texto and '</body>' in texto:
        texto = texto.replace('</body>', '    <script src="seed-teclado-final-v3825.js?v=3825"></script>\n</body>', 1)

    pagina.write_text(texto, encoding='utf-8')
    htmls += 1

assistente = ROOT / 'assistente-chat-v384.html'
cadastro = ROOT / 'cadastro.html'
for pagina in (assistente, cadastro):
    if not pagina.exists():
        raise SystemExit(f'Página necessária ausente: {pagina}')
    t = pagina.read_text(encoding='utf-8')
    if 'seed-teclado-final-v3825.css' not in t or 'seed-teclado-final-v3825.js' not in t:
        raise SystemExit(f'Arquivos finais não foram injetados em {pagina.name}')

for marca in ('Clipboard', 'keyboardWillShow', 'seed-teclado-aberto-v3825', 'seed-sugestoes-v3825', 'inserirTexto'):
    if marca not in JS.read_text(encoding='utf-8'):
        raise SystemExit(f'Marca JS ausente: {marca}')

for marca in ('padding-bottom: 62px', 'seed-teclado-aberto-v3825', 'seed-sugestoes-v3825'):
    if marca not in CSS.read_text(encoding='utf-8'):
        raise SystemExit(f'Marca CSS ausente: {marca}')

print(f'Correção final aplicada: rodapé seguro + sugestões próprias + colar. HTMLs processados: {htmls}.')
