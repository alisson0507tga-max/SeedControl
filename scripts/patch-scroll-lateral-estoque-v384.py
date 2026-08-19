from pathlib import Path
import re

ROOT = Path('native/www')
HTML = ROOT / 'estoque.html'
JS = ROOT / 'scroll-lateral-estoque-v3834.js'
CSS = ROOT / 'scroll-lateral-estoque-v3834.css'
SW = ROOT / 'service-worker.js'

if not HTML.exists():
    raise SystemExit('estoque.html não encontrado.')

css = r'''/* seedcontrol-scroll-lateral-estoque-v3834 */
#seedScrollLateral {
    position: fixed;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 9997;
    display: none;
    width: 38px;
    padding: 4px;
    border-radius: 20px;
    background: rgba(55, 65, 70, .92);
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 7px 18px rgba(0,0,0,.28);
    backdrop-filter: blur(7px);
    -webkit-backdrop-filter: blur(7px);
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}

#seedScrollLateral.seed-scroll-visivel {
    display: flex;
    flex-direction: column;
    align-items: center;
}

#seedScrollLateral button {
    width: 30px !important;
    min-width: 30px !important;
    height: 32px !important;
    min-height: 32px !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    border-radius: 14px !important;
    background: transparent !important;
    color: #f5f7f8 !important;
    box-shadow: none !important;
    font-size: 19px !important;
    line-height: 32px !important;
    font-weight: 900 !important;
    text-align: center;
    -webkit-tap-highlight-color: transparent;
}

#seedScrollLateral button:active,
#seedScrollLateral button.seed-scroll-pressionado {
    background: rgba(255,255,255,.15) !important;
    transform: none !important;
}

#seedScrollLateral .seed-scroll-divisor {
    width: 20px;
    height: 1px;
    margin: 1px 0;
    background: rgba(255,255,255,.18);
}

@media (max-width: 390px) {
    #seedScrollLateral {
        right: 5px;
        width: 36px;
    }
}
'''
CSS.write_text(css, encoding='utf-8')

js = r'''// seedcontrol-scroll-lateral-estoque-v3834
(function () {
    'use strict';

    if (document.getElementById('seedScrollLateral')) return;

    const controle = document.createElement('div');
    controle.id = 'seedScrollLateral';
    controle.setAttribute('aria-label', 'Controle rápido de rolagem');
    controle.innerHTML = `
        <button type="button" id="seedScrollUp" aria-label="Subir">▲</button>
        <div class="seed-scroll-divisor"></div>
        <button type="button" id="seedScrollDown" aria-label="Descer">▼</button>
    `;
    document.body.appendChild(controle);

    const btnUp = document.getElementById('seedScrollUp');
    const btnDown = document.getElementById('seedScrollDown');

    let timerAtraso = null;
    let frame = null;
    let segurando = false;
    let direcao = 0;
    let inicioPressao = 0;

    function maxScroll() {
        return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    }

    function atualizarVisibilidade() {
        const max = maxScroll();
        const tecladoAberto = window.visualViewport && window.visualViewport.height < window.innerHeight * 0.72;
        if (max > 420 && !tecladoAberto) {
            controle.classList.add('seed-scroll-visivel');
        } else {
            controle.classList.remove('seed-scroll-visivel');
        }

        btnUp.style.opacity = window.scrollY <= 8 ? '.38' : '1';
        btnDown.style.opacity = window.scrollY >= max - 8 ? '.38' : '1';
    }

    function passoRapido(dir) {
        const tamanho = Math.max(360, Math.round(window.innerHeight * 0.72));
        window.scrollBy({ top: dir * tamanho, left: 0, behavior: 'smooth' });
    }

    function loopContinuo() {
        if (!segurando) return;

        const tempo = performance.now() - inicioPressao;
        let velocidade = 12;
        if (tempo > 1200) velocidade = 18;
        if (tempo > 2600) velocidade = 26;

        window.scrollBy(0, direcao * velocidade);
        frame = requestAnimationFrame(loopContinuo);
    }

    function iniciar(btn, dir, ev) {
        if (ev) ev.preventDefault();
        parar();
        direcao = dir;
        inicioPressao = performance.now();
        btn.classList.add('seed-scroll-pressionado');

        timerAtraso = setTimeout(function () {
            segurando = true;
            frame = requestAnimationFrame(loopContinuo);
        }, 260);
    }

    function parar(ev) {
        if (ev) ev.preventDefault();
        if (timerAtraso) clearTimeout(timerAtraso);
        timerAtraso = null;
        if (frame) cancelAnimationFrame(frame);
        frame = null;
        segurando = false;
        btnUp.classList.remove('seed-scroll-pressionado');
        btnDown.classList.remove('seed-scroll-pressionado');
    }

    function configurar(botao, dir) {
        let pressionou = false;
        let virouSegurar = false;

        botao.addEventListener('pointerdown', function (ev) {
            pressionou = true;
            virouSegurar = false;
            iniciar(botao, dir, ev);
            setTimeout(function () {
                if (pressionou && segurando) virouSegurar = true;
            }, 300);
            try { botao.setPointerCapture(ev.pointerId); } catch (_) {}
        });

        botao.addEventListener('pointerup', function (ev) {
            const foiSegurar = virouSegurar || segurando;
            pressionou = false;
            parar(ev);
            if (!foiSegurar) passoRapido(dir);
        });

        botao.addEventListener('pointercancel', function (ev) {
            pressionou = false;
            parar(ev);
        });

        botao.addEventListener('lostpointercapture', function () {
            pressionou = false;
            parar();
        });

        botao.addEventListener('contextmenu', function (ev) { ev.preventDefault(); });
    }

    configurar(btnUp, -1);
    configurar(btnDown, 1);

    window.addEventListener('scroll', atualizarVisibilidade, { passive: true });
    window.addEventListener('resize', atualizarVisibilidade, { passive: true });
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) parar();
        else atualizarVisibilidade();
    });

    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', atualizarVisibilidade, { passive: true });
    }

    const observer = new MutationObserver(atualizarVisibilidade);
    observer.observe(document.body, { childList: true, subtree: true });

    atualizarVisibilidade();
})();
'''
JS.write_text(js, encoding='utf-8')

html = HTML.read_text(encoding='utf-8')
if 'scroll-lateral-estoque-v3834.css' not in html:
    if '</head>' not in html:
        raise SystemExit('</head> não encontrado em estoque.html')
    html = html.replace('</head>', '    <link rel="stylesheet" href="scroll-lateral-estoque-v3834.css?v=3834">\n</head>', 1)

if 'scroll-lateral-estoque-v3834.js' not in html:
    if '</body>' not in html:
        raise SystemExit('</body> não encontrado em estoque.html')
    html = html.replace('</body>', '    <script src="scroll-lateral-estoque-v3834.js?v=3834"></script>\n</body>', 1)

HTML.write_text(html, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-34', sw, count=1)
    if 'scroll-lateral-estoque-v3834.js' not in sw:
        m = re.search(r'(const\s+APP_SHELL\s*=\s*\[)(.*?)(\];)', sw, flags=re.S)
        if m:
            miolo = m.group(2).rstrip()
            virg = ',' if miolo and not miolo.rstrip().endswith(',') else ''
            extra = f'{virg}\n  "./scroll-lateral-estoque-v3834.js",\n  "./scroll-lateral-estoque-v3834.css"\n'
            sw = sw[:m.start(2)] + miolo + extra + sw[m.end(2):]
    SW.write_text(sw, encoding='utf-8')

for arquivo, marcas in {
    HTML: ['scroll-lateral-estoque-v3834.css?v=3834', 'scroll-lateral-estoque-v3834.js?v=3834'],
    JS: ['seedcontrol-scroll-lateral-estoque-v3834', 'pointerdown', 'requestAnimationFrame', 'passoRapido'],
    CSS: ['#seedScrollLateral', 'seed-scroll-visivel']
}.items():
    txt = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in txt:
            raise SystemExit(f'Validação falhou em {arquivo.name}: {marca}')

print('Controle lateral de rolagem do Estoque preparado: toque por página e pressão contínua com aceleração.')
