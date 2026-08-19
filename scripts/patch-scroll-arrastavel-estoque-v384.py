from pathlib import Path
import re

ROOT = Path('native/www')
HTML = ROOT / 'estoque.html'
JS = ROOT / 'scroll-rapido-estoque-v3835.js'
CSS = ROOT / 'scroll-rapido-estoque-v3835.css'
SW = ROOT / 'service-worker.js'

if not HTML.exists():
    raise SystemExit('estoque.html não encontrado.')

css = r'''/* seedcontrol-scroll-rapido-estoque-v3835 */
#seedFastTrack {
    position: fixed;
    top: calc(92px + env(safe-area-inset-top));
    bottom: calc(58px + env(safe-area-inset-bottom));
    right: 0;
    width: 30px;
    z-index: 9998;
    display: none;
    pointer-events: none;
    user-select: none;
    -webkit-user-select: none;
}

#seedFastTrack.seed-fast-visible {
    display: block;
}

#seedFastThumb {
    position: absolute;
    right: 0;
    top: 0;
    width: 18px;
    height: 72px;
    border-radius: 13px 0 0 13px;
    border: 1px solid rgba(255,255,255,.16);
    border-right: 0;
    background: rgba(69, 78, 83, .78);
    box-shadow: -3px 5px 14px rgba(0,0,0,.24);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    touch-action: none;
    pointer-events: auto;
    opacity: .68;
    transition: width .12s ease, opacity .12s ease, background .12s ease;
    -webkit-tap-highlight-color: transparent;
}

#seedFastThumb::before {
    content: '';
    position: absolute;
    left: 7px;
    top: 20px;
    width: 3px;
    height: 30px;
    border-radius: 4px;
    background: rgba(255,255,255,.72);
    box-shadow: 0 0 0 1px rgba(0,0,0,.08);
}

#seedFastThumb.seed-fast-dragging {
    width: 24px;
    opacity: 1;
    background: rgba(50, 68, 65, .94);
}

#seedFastBubble {
    position: absolute;
    right: 31px;
    top: 50%;
    transform: translateY(-50%);
    min-width: 82px;
    max-width: 150px;
    padding: 8px 10px;
    border-radius: 12px;
    background: rgba(8, 28, 36, .96);
    border: 1px solid rgba(74,222,128,.38);
    color: #f8fafc;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    white-space: nowrap;
    box-shadow: 0 6px 18px rgba(0,0,0,.28);
    opacity: 0;
    pointer-events: none;
    transition: opacity .1s ease;
}

#seedFastThumb.seed-fast-dragging #seedFastBubble {
    opacity: 1;
}

@media (max-width: 390px) {
    #seedFastTrack { width: 28px; }
    #seedFastThumb { width: 17px; }
    #seedFastThumb.seed-fast-dragging { width: 23px; }
}
'''
CSS.write_text(css, encoding='utf-8')

js = r'''// seedcontrol-scroll-rapido-estoque-v3835
(function () {
    'use strict';

    if (document.getElementById('seedFastTrack')) return;

    const track = document.createElement('div');
    track.id = 'seedFastTrack';
    track.setAttribute('aria-hidden', 'true');
    track.innerHTML = '<div id="seedFastThumb"><div id="seedFastBubble">Lote</div></div>';
    document.body.appendChild(track);

    const thumb = document.getElementById('seedFastThumb');
    const bubble = document.getElementById('seedFastBubble');

    let dragging = false;
    let pointerId = null;
    let offsetY = 0;
    let raf = null;

    function maxScroll() {
        return Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    }

    function trackRange() {
        return Math.max(1, track.clientHeight - thumb.offsetHeight);
    }

    function tecladoAberto() {
        return !!(window.visualViewport && window.visualViewport.height < window.innerHeight * 0.72);
    }

    function posicaoThumb() {
        const max = maxScroll();
        if (max <= 0) return 0;
        return Math.max(0, Math.min(trackRange(), (window.scrollY / max) * trackRange()));
    }

    function atualizarThumb() {
        if (!dragging) thumb.style.top = posicaoThumb() + 'px';
        const mostrar = maxScroll() > 600 && !tecladoAberto();
        track.classList.toggle('seed-fast-visible', mostrar);
    }

    function loteVisivel() {
        const cards = Array.from(document.querySelectorAll('#lista .card-registro, #lista .estoque-registro'));
        if (!cards.length) return '';
        const alvoY = window.innerHeight * 0.48;
        let melhor = null;
        let melhorDist = Infinity;
        for (const card of cards) {
            const r = card.getBoundingClientRect();
            const centro = (r.top + r.bottom) / 2;
            const dist = Math.abs(centro - alvoY);
            if (dist < melhorDist) {
                melhorDist = dist;
                melhor = card;
            }
        }
        if (!melhor) return '';
        const texto = String(melhor.innerText || melhor.textContent || '');
        const m = texto.match(/Lote\s*:?\s*([^\n\r]+)/i);
        if (m && m[1]) return m[1].trim().split(/\s+/)[0];
        return '';
    }

    function atualizarBubble() {
        const lote = loteVisivel();
        if (lote) bubble.textContent = 'Lote ' + lote;
        else {
            const max = maxScroll();
            const pct = max > 0 ? Math.round((window.scrollY / max) * 100) : 0;
            bubble.textContent = pct + '%';
        }
    }

    function scrollPeloPointer(clientY) {
        const rect = track.getBoundingClientRect();
        let top = clientY - rect.top - offsetY;
        top = Math.max(0, Math.min(trackRange(), top));
        thumb.style.top = top + 'px';
        const proporcao = top / trackRange();
        const destino = proporcao * maxScroll();
        window.scrollTo(0, destino);
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(atualizarBubble);
    }

    thumb.addEventListener('pointerdown', function (ev) {
        if (ev.pointerType === 'mouse' && ev.button !== 0) return;
        ev.preventDefault();
        dragging = true;
        pointerId = ev.pointerId;
        const rect = thumb.getBoundingClientRect();
        offsetY = ev.clientY - rect.top;
        thumb.classList.add('seed-fast-dragging');
        atualizarBubble();
        try { thumb.setPointerCapture(pointerId); } catch (_) {}
    });

    thumb.addEventListener('pointermove', function (ev) {
        if (!dragging || ev.pointerId !== pointerId) return;
        ev.preventDefault();
        scrollPeloPointer(ev.clientY);
    });

    function finalizar(ev) {
        if (!dragging) return;
        if (ev) ev.preventDefault();
        dragging = false;
        thumb.classList.remove('seed-fast-dragging');
        try {
            if (pointerId !== null && thumb.hasPointerCapture(pointerId)) thumb.releasePointerCapture(pointerId);
        } catch (_) {}
        pointerId = null;
        atualizarThumb();
    }

    thumb.addEventListener('pointerup', finalizar);
    thumb.addEventListener('pointercancel', finalizar);
    thumb.addEventListener('lostpointercapture', function () {
        if (dragging) finalizar();
    });
    thumb.addEventListener('contextmenu', function (ev) { ev.preventDefault(); });

    window.addEventListener('scroll', function () {
        if (!dragging) atualizarThumb();
    }, { passive: true });
    window.addEventListener('resize', atualizarThumb, { passive: true });
    if (window.visualViewport) window.visualViewport.addEventListener('resize', atualizarThumb, { passive: true });

    const observer = new MutationObserver(function () {
        if (!dragging) atualizarThumb();
    });
    observer.observe(document.getElementById('lista') || document.body, { childList: true, subtree: true });

    atualizarThumb();
})();
'''
JS.write_text(js, encoding='utf-8')

html = HTML.read_text(encoding='utf-8')
if 'scroll-rapido-estoque-v3835.css' not in html:
    if '</head>' not in html:
        raise SystemExit('</head> não encontrado em estoque.html')
    html = html.replace('</head>', '    <link rel="stylesheet" href="scroll-rapido-estoque-v3835.css?v=3835">\n</head>', 1)

if 'scroll-rapido-estoque-v3835.js' not in html:
    if '</body>' not in html:
        raise SystemExit('</body> não encontrado em estoque.html')
    html = html.replace('</body>', '    <script src="scroll-rapido-estoque-v3835.js?v=3835"></script>\n</body>', 1)

HTML.write_text(html, encoding='utf-8')

if SW.exists():
    sw = SW.read_text(encoding='utf-8')
    sw = re.sub(r'seedcontrol-v3\.8-pwa-\d+', 'seedcontrol-v3.8-pwa-35', sw, count=1)
    if 'scroll-rapido-estoque-v3835.js' not in sw:
        m = re.search(r'(const\s+APP_SHELL\s*=\s*\[)(.*?)(\];)', sw, flags=re.S)
        if m:
            miolo = m.group(2).rstrip()
            virg = ',' if miolo and not miolo.rstrip().endswith(',') else ''
            extra = f'{virg}\n  "./scroll-rapido-estoque-v3835.js",\n  "./scroll-rapido-estoque-v3835.css"\n'
            sw = sw[:m.start(2)] + miolo + extra + sw[m.end(2):]
    SW.write_text(sw, encoding='utf-8')

for arquivo, marcas in {
    HTML: ['scroll-rapido-estoque-v3835.css?v=3835', 'scroll-rapido-estoque-v3835.js?v=3835'],
    JS: ['seedcontrol-scroll-rapido-estoque-v3835', 'pointermove', 'scrollPeloPointer', 'loteVisivel'],
    CSS: ['#seedFastTrack', '#seedFastThumb', 'seed-fast-dragging']
}.items():
    txt = arquivo.read_text(encoding='utf-8')
    for marca in marcas:
        if marca not in txt:
            raise SystemExit(f'Validação falhou em {arquivo.name}: {marca}')

print('Aba lateral arrastável do Estoque preparada: arraste proporcional e indicação do lote visível.')
