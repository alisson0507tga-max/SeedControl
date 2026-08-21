// seedcontrol-nota-zoom-pan-v3916
(function () {
  "use strict";

  const INSTANCIAS = new WeakMap();

  const CONFIGS = [
    { modalId: "seedNotaModal3839", imgId: "seedNotaImg3839", areaId: "seedNotaArea3839", zoomId: "seedNotaZoom3839" },
    { modalId: "seedNotaModal3909", imgId: "seedNotaImg3909", areaSelector: ".seed-nota-area-v3909", zoomId: "seedNotaZoom3909" },
    { modalId: "ecNotaModal3907", imgId: "ecNotaImagem3907", areaSelector: ".ec-nota-modal-area-3907", zoomId: null }
  ];

  function limitar(v, min, max) {
    return Math.min(max, Math.max(min, v));
  }

  function instalarEstilo() {
    if (document.getElementById("seedNotaZoomStyle3916")) return;
    const s = document.createElement("style");
    s.id = "seedNotaZoomStyle3916";
    s.textContent = `
      .seed-nota-zoom-area-v3916{touch-action:none!important;overscroll-behavior:contain!important;position:relative!important;overflow:hidden!important}
      .seed-nota-zoom-img-v3916{touch-action:none!important;user-select:none!important;-webkit-user-drag:none!important;max-width:100%!important;max-height:100%!important;object-fit:contain!important;transform-origin:center center!important;transition:none!important;will-change:transform;cursor:grab}
      .seed-nota-zoom-img-v3916.seed-arrastando-v3916{cursor:grabbing}
      .seed-nota-controles-v3916{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;padding-top:10px}
      .seed-nota-controles-v3916 button{min-height:44px;border-radius:12px;border:1px solid rgba(74,222,128,.34);background:rgba(18,112,55,.78);color:#fff;font:inherit;font-weight:750}
      .seed-nota-dica-v3916{padding:8px 4px 0;color:#9fb1b8;font-size:12px;text-align:center}
    `;
    document.head.appendChild(s);
  }

  function criarEstado(img, area, modal, zoomBtn) {
    const estado = {
      img, area, modal, zoomBtn,
      scale: 1,
      x: 0,
      y: 0,
      ponteiros: new Map(),
      ultimaDist: 0,
      ultimoCentro: null,
      ultimoUm: null
    };

    function limites() {
      const iw = img.clientWidth || 1;
      const ih = img.clientHeight || 1;
      const aw = area.clientWidth || 1;
      const ah = area.clientHeight || 1;
      return {
        x: Math.max(0, (iw * estado.scale - aw) / 2) + 48,
        y: Math.max(0, (ih * estado.scale - ah) / 2) + 48
      };
    }

    function aplicar() {
      if (estado.scale <= 1.001) {
        estado.scale = 1;
        estado.x = 0;
        estado.y = 0;
      } else {
        const l = limites();
        estado.x = limitar(estado.x, -l.x, l.x);
        estado.y = limitar(estado.y, -l.y, l.y);
      }
      img.style.transform = `translate3d(${estado.x}px,${estado.y}px,0) scale(${estado.scale})`;
      if (zoomBtn) zoomBtn.textContent = estado.scale > 1.05 ? "🔎 Normal" : "🔍 Ampliar";
      const pct = modal.querySelector("[data-seed-zoom-pct-v3916]");
      if (pct) pct.textContent = `${Math.round(estado.scale * 100)}%`;
    }

    function resetar() {
      estado.scale = 1;
      estado.x = 0;
      estado.y = 0;
      estado.ponteiros.clear();
      estado.ultimaDist = 0;
      estado.ultimoCentro = null;
      estado.ultimoUm = null;
      aplicar();
    }

    function zoom(delta) {
      estado.scale = limitar(estado.scale + delta, 1, 5);
      aplicar();
    }

    function distancia(a, b) {
      return Math.hypot(a.x - b.x, a.y - b.y);
    }

    function centro(a, b) {
      return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
    }

    area.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      try { area.setPointerCapture(e.pointerId); } catch (_) {}
      estado.ponteiros.set(e.pointerId, { x: e.clientX, y: e.clientY });
      img.classList.add("seed-arrastando-v3916");

      const pts = Array.from(estado.ponteiros.values());
      if (pts.length === 1) estado.ultimoUm = pts[0];
      if (pts.length >= 2) {
        estado.ultimaDist = distancia(pts[0], pts[1]);
        estado.ultimoCentro = centro(pts[0], pts[1]);
      }
      e.preventDefault();
    }, { passive: false });

    area.addEventListener("pointermove", function (e) {
      if (!estado.ponteiros.has(e.pointerId)) return;
      estado.ponteiros.set(e.pointerId, { x: e.clientX, y: e.clientY });
      const pts = Array.from(estado.ponteiros.values());

      if (pts.length >= 2) {
        const d = distancia(pts[0], pts[1]);
        const c = centro(pts[0], pts[1]);
        if (estado.ultimaDist > 0) {
          estado.scale = limitar(estado.scale * (d / estado.ultimaDist), 1, 5);
        }
        if (estado.ultimoCentro && estado.scale > 1) {
          estado.x += c.x - estado.ultimoCentro.x;
          estado.y += c.y - estado.ultimoCentro.y;
        }
        estado.ultimaDist = d;
        estado.ultimoCentro = c;
        aplicar();
      } else if (pts.length === 1 && estado.scale > 1) {
        const p = pts[0];
        if (estado.ultimoUm) {
          estado.x += p.x - estado.ultimoUm.x;
          estado.y += p.y - estado.ultimoUm.y;
        }
        estado.ultimoUm = p;
        aplicar();
      }
      e.preventDefault();
    }, { passive: false });

    function soltar(e) {
      estado.ponteiros.delete(e.pointerId);
      const pts = Array.from(estado.ponteiros.values());
      if (pts.length === 1) estado.ultimoUm = pts[0];
      else estado.ultimoUm = null;
      if (pts.length < 2) {
        estado.ultimaDist = 0;
        estado.ultimoCentro = null;
      }
      if (!pts.length) img.classList.remove("seed-arrastando-v3916");
      aplicar();
    }

    area.addEventListener("pointerup", soltar);
    area.addEventListener("pointercancel", soltar);
    area.addEventListener("lostpointercapture", soltar);

    area.addEventListener("wheel", function (e) {
      e.preventDefault();
      zoom(e.deltaY < 0 ? 0.35 : -0.35);
    }, { passive: false });

    let ultimoToque = 0;
    area.addEventListener("pointerup", function (e) {
      if (e.pointerType !== "touch") return;
      const agora = Date.now();
      if (agora - ultimoToque < 320) {
        if (estado.scale > 1.05) resetar();
        else { estado.scale = 2; aplicar(); }
        ultimoToque = 0;
      } else {
        ultimoToque = agora;
      }
    });

    img.addEventListener("load", resetar);

    if (zoomBtn) {
      document.addEventListener("click", function (e) {
        if (e.target !== zoomBtn) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        if (estado.scale > 1.05) resetar();
        else { estado.scale = 2; aplicar(); }
      }, true);
    }

    const controles = document.createElement("div");
    controles.className = "seed-nota-controles-v3916";
    controles.innerHTML = `
      <button type="button" data-seed-zoom-out-v3916>−</button>
      <button type="button" data-seed-zoom-pct-v3916>100%</button>
      <button type="button" data-seed-zoom-in-v3916>＋</button>
    `;
    const dica = document.createElement("div");
    dica.className = "seed-nota-dica-v3916";
    dica.textContent = "Use dois dedos para ampliar e arraste a imagem para visualizar os detalhes.";

    const acoesExistentes = modal.querySelector(".seed-nota-acoes-v3839,.seed-nota-acoes-v3909");
    if (acoesExistentes) modal.insertBefore(controles, acoesExistentes);
    else modal.appendChild(controles);
    if (acoesExistentes) modal.insertBefore(dica, controles);
    else modal.insertBefore(dica, controles);

    controles.querySelector("[data-seed-zoom-out-v3916]").addEventListener("click", () => zoom(-0.5));
    controles.querySelector("[data-seed-zoom-in-v3916]").addEventListener("click", () => zoom(0.5));
    controles.querySelector("[data-seed-zoom-pct-v3916]").addEventListener("click", resetar);

    new MutationObserver(function () {
      if (modal.classList.contains("ativo")) setTimeout(resetar, 0);
    }).observe(modal, { attributes: true, attributeFilter: ["class"] });

    aplicar();
    return estado;
  }

  function instalarConfig(cfg) {
    const modal = document.getElementById(cfg.modalId);
    const img = document.getElementById(cfg.imgId);
    if (!modal || !img || INSTANCIAS.has(img)) return false;
    const area = cfg.areaId ? document.getElementById(cfg.areaId) : modal.querySelector(cfg.areaSelector);
    if (!area) return false;
    const zoomBtn = cfg.zoomId ? document.getElementById(cfg.zoomId) : null;
    area.classList.add("seed-nota-zoom-area-v3916");
    img.classList.add("seed-nota-zoom-img-v3916");
    INSTANCIAS.set(img, criarEstado(img, area, modal, zoomBtn));
    return true;
  }

  function instalarTudo() {
    instalarEstilo();
    CONFIGS.forEach(instalarConfig);
  }

  function iniciar() {
    instalarTudo();
    new MutationObserver(function () {
      requestAnimationFrame(instalarTudo);
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
