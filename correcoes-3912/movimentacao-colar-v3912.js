// seedcontrol-movimentacao-colar-v3912
(function () {
  "use strict";

  const alvoIds = ["destino", "obs"];

  function estilo() {
    if (document.getElementById("seed-colar-style-3912")) return;
    const s = document.createElement("style");
    s.id = "seed-colar-style-3912";
    s.textContent = `
      .seed-colar-acoes-3912{display:flex;justify-content:flex-end;margin:4px 0 7px;}
      .seed-colar-btn-3912{width:auto!important;min-height:38px!important;padding:8px 13px!important;margin:0!important;border-radius:10px!important;border:1px solid rgba(74,222,128,.38)!important;background:rgba(10,72,45,.72)!important;color:#eefcf3!important;font-size:14px!important;font-weight:700!important;box-shadow:none!important;}
      .seed-colar-btn-3912:active{transform:scale(.98);}
    `;
    document.head.appendChild(s);
  }

  async function lerClipboard() {
    const cap = window.Capacitor;
    const plugin = cap && cap.Plugins && cap.Plugins.Clipboard;
    if (plugin && typeof plugin.read === "function") {
      const r = await plugin.read();
      return String((r && r.value) || "");
    }
    if (navigator.clipboard && typeof navigator.clipboard.readText === "function") {
      return String(await navigator.clipboard.readText());
    }
    throw new Error("Área de transferência indisponível");
  }

  function inserirNoCursor(campo, texto) {
    if (!campo || !texto) return;
    const atual = String(campo.value || "");
    const ini = Number.isInteger(campo.selectionStart) ? campo.selectionStart : atual.length;
    const fim = Number.isInteger(campo.selectionEnd) ? campo.selectionEnd : ini;
    const novo = atual.slice(0, ini) + texto + atual.slice(fim);
    campo.value = novo;
    campo.dispatchEvent(new Event("input", { bubbles: true }));
    campo.dispatchEvent(new Event("change", { bubbles: true }));
    campo.focus();
    const pos = ini + texto.length;
    try { campo.setSelectionRange(pos, pos); } catch (_) {}
  }

  async function colarNo(campo, botao) {
    const textoOriginal = botao.textContent;
    try {
      botao.disabled = true;
      botao.textContent = "Colando...";
      const valor = await lerClipboard();
      if (!valor) {
        alert("Não há texto copiado para colar.");
        return;
      }
      inserirNoCursor(campo, valor);
    } catch (e) {
      alert("Não foi possível ler o texto copiado. Copie novamente e tente de novo.");
    } finally {
      botao.disabled = false;
      botao.textContent = textoOriginal;
    }
  }

  function prepararCampo(campo) {
    if (!campo || campo.dataset.seedColar3912 === "1") return;
    campo.dataset.seedColar3912 = "1";
    campo.setAttribute("autocomplete", "on");
    campo.setAttribute("autocorrect", "on");
    campo.setAttribute("spellcheck", "true");
    campo.setAttribute("autocapitalize", "sentences");
    campo.setAttribute("inputmode", "text");

    const acoes = document.createElement("div");
    acoes.className = "seed-colar-acoes-3912";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "seed-colar-btn-3912";
    btn.textContent = "📋 Colar";
    btn.addEventListener("click", () => colarNo(campo, btn));
    acoes.appendChild(btn);
    campo.insertAdjacentElement("beforebegin", acoes);
  }

  function varrer() {
    alvoIds.forEach(id => prepararCampo(document.getElementById(id)));
  }

  function iniciar() {
    estilo();
    varrer();
    const obs = new MutationObserver(varrer);
    obs.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => obs.disconnect(), 12000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  else iniciar();
})();
