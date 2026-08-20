// seedcontrol-nota-visualizador-v3839
(function () {
    "use strict";

    let notaAtual = null;
    let loteAtual = null;
    let observer = null;

    function norm(v) {
        return String(v == null ? "" : v)
            .trim()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function carregarLotes() {
        try {
            if (typeof window.carregarEstoque === "function") {
                const dados = window.carregarEstoque();
                if (Array.isArray(dados)) return dados;
            }
        } catch (_) {}

        try {
            const bruto = localStorage.getItem("estoque");
            const dados = bruto ? JSON.parse(bruto) : [];
            return Array.isArray(dados) ? dados : [];
        } catch (_) {
            return [];
        }
    }

    function textoCampo(card, nome) {
        const rx = new RegExp(nome + "\\s*:\\s*", "i");
        const ps = Array.from(card.querySelectorAll("p"));
        const p = ps.find(el => rx.test(el.textContent || ""));
        if (!p) return "";
        return String(p.textContent || "").replace(rx, "").trim();
    }

    function cultivarCard(card) {
        const h = card.querySelector("h2");
        if (!h) return "";
        return String(h.textContent || "")
            .replace(/^\s*🌱\s*/, "")
            .trim();
    }

    function encontrarLote(card) {
        const cultivar = cultivarCard(card);
        const lote = textoCampo(card, "Lote");
        if (!cultivar || !lote) return null;

        const comNota = carregarLotes().filter(item =>
            item && item.notaEntradaFoto &&
            norm(item.cultivar) === norm(cultivar) &&
            norm(item.lote) === norm(lote)
        );

        if (comNota.length <= 1) return comNota[0] || null;

        const fazenda = textoCampo(card, "Fazenda");
        const peneira = textoCampo(card, "Peneira");
        const talhao = textoCampo(card, "Talh[aã]o");

        return comNota.find(item =>
            (!fazenda || norm(item.fazenda) === norm(fazenda)) &&
            (!peneira || norm(item.peneira) === norm(peneira)) &&
            (!talhao || norm(item.talhao) === norm(talhao))
        ) || comNota[0];
    }

    function instalarEstilo() {
        if (document.getElementById("seedNotaViewerStyle3839")) return;
        const style = document.createElement("style");
        style.id = "seedNotaViewerStyle3839";
        style.textContent = `
            .seed-nota-btn-v3839 {
                grid-column: 1 / -1;
                width: 100%;
                min-height: 48px;
                margin-top: 10px;
                border: 1px solid rgba(74,222,128,.42);
                border-radius: 13px;
                background: rgba(16,94,53,.72);
                color: #f1fff5;
                font: inherit;
                font-weight: 700;
            }
            .seed-nota-modal-v3839 {
                position: fixed;
                inset: 0;
                z-index: 2147483000;
                display: none;
                flex-direction: column;
                background: rgba(2,8,12,.96);
                color: #fff;
                padding: max(14px, env(safe-area-inset-top)) 12px max(14px, env(safe-area-inset-bottom));
            }
            .seed-nota-modal-v3839.ativo { display: flex; }
            .seed-nota-top-v3839 {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                padding: 4px 4px 12px;
            }
            .seed-nota-top-v3839 strong { font-size: 17px; }
            .seed-nota-fechar-v3839 {
                min-width: 44px;
                min-height: 44px;
                border: 1px solid rgba(255,255,255,.18);
                border-radius: 12px;
                background: rgba(255,255,255,.08);
                color: #fff;
                font-size: 22px;
            }
            .seed-nota-area-v3839 {
                flex: 1;
                min-height: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: auto;
                border: 1px solid rgba(148,163,184,.18);
                border-radius: 16px;
                background: #02090d;
            }
            .seed-nota-img-v3839 {
                display: block;
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                transform-origin: center center;
                transition: transform .18s ease;
            }
            .seed-nota-img-v3839.zoom { transform: scale(1.65); }
            .seed-nota-acoes-v3839 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                padding-top: 12px;
            }
            .seed-nota-acoes-v3839 button {
                min-height: 50px;
                border-radius: 13px;
                border: 1px solid rgba(74,222,128,.34);
                background: rgba(18,112,55,.78);
                color: #fff;
                font: inherit;
                font-weight: 700;
            }
        `;
        document.head.appendChild(style);
    }

    function criarModal() {
        if (document.getElementById("seedNotaModal3839")) return;

        const modal = document.createElement("div");
        modal.id = "seedNotaModal3839";
        modal.className = "seed-nota-modal-v3839";
        modal.innerHTML = `
            <div class="seed-nota-top-v3839">
                <strong id="seedNotaTitulo3839">Nota de entrada</strong>
                <button type="button" class="seed-nota-fechar-v3839" id="seedNotaFechar3839" aria-label="Fechar">✕</button>
            </div>
            <div class="seed-nota-area-v3839" id="seedNotaArea3839">
                <img class="seed-nota-img-v3839" id="seedNotaImg3839" alt="Nota de entrada do lote">
            </div>
            <div class="seed-nota-acoes-v3839">
                <button type="button" id="seedNotaZoom3839">🔍 Ampliar</button>
                <button type="button" id="seedNotaCompartilhar3839">↗ Compartilhar</button>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById("seedNotaFechar3839").addEventListener("click", fecharNota);
        document.getElementById("seedNotaZoom3839").addEventListener("click", function () {
            const img = document.getElementById("seedNotaImg3839");
            const zoom = img.classList.toggle("zoom");
            this.textContent = zoom ? "🔎 Normal" : "🔍 Ampliar";
        });
        document.getElementById("seedNotaCompartilhar3839").addEventListener("click", compartilharNota);
        modal.addEventListener("click", function (e) {
            if (e.target === modal) fecharNota();
        });
    }

    function abrirNota(lote) {
        if (!lote || !lote.notaEntradaFoto) return;
        notaAtual = lote.notaEntradaFoto;
        loteAtual = lote;

        criarModal();
        const img = document.getElementById("seedNotaImg3839");
        const titulo = document.getElementById("seedNotaTitulo3839");
        img.classList.remove("zoom");
        img.src = notaAtual;
        titulo.textContent = `Nota de entrada • Lote ${String(lote.lote || "")}`;
        document.getElementById("seedNotaZoom3839").textContent = "🔍 Ampliar";
        document.getElementById("seedNotaModal3839").classList.add("ativo");
        document.documentElement.style.overflow = "hidden";
    }

    function fecharNota() {
        const modal = document.getElementById("seedNotaModal3839");
        if (modal) modal.classList.remove("ativo");
        document.documentElement.style.overflow = "";
    }

    function dataUrlParaFile(dataUrl, nome) {
        const partes = String(dataUrl).split(",");
        const mime = ((partes[0] || "").match(/data:([^;]+)/) || [])[1] || "image/jpeg";
        const bin = atob(partes[1] || "");
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
        return new File([bytes], nome, { type: mime });
    }

    async function compartilharNota() {
        if (!notaAtual) return;
        const lote = String((loteAtual && loteAtual.lote) || "lote").replace(/[^a-z0-9_-]+/gi, "-");
        const nome = `SeedControl-nota-${lote}.jpg`;

        try {
            const arquivo = dataUrlParaFile(notaAtual, nome);
            if (navigator.share && (!navigator.canShare || navigator.canShare({ files: [arquivo] }))) {
                await navigator.share({
                    title: `Nota de entrada - Lote ${loteAtual && loteAtual.lote ? loteAtual.lote : ""}`,
                    text: "Nota de entrada do SeedControl",
                    files: [arquivo]
                });
                return;
            }
        } catch (_) {}

        try {
            const cap = window.Capacitor && window.Capacitor.Plugins;
            if (cap && cap.Filesystem && cap.Share) {
                const base64 = String(notaAtual).split(",")[1] || "";
                const salvo = await cap.Filesystem.writeFile({
                    path: nome,
                    data: base64,
                    directory: "CACHE"
                });
                await cap.Share.share({
                    title: `Nota de entrada - Lote ${loteAtual && loteAtual.lote ? loteAtual.lote : ""}`,
                    text: "Nota de entrada do SeedControl",
                    url: salvo.uri,
                    dialogTitle: "Compartilhar nota"
                });
                return;
            }
        } catch (_) {}

        alert("A nota está disponível para visualização, mas o compartilhamento não foi disponibilizado pelo Android neste aparelho.");
    }

    function decorarCards() {
        const lista = document.getElementById("lista");
        if (!lista) return;

        const cards = Array.from(lista.querySelectorAll(".card-registro, .estoque-registro"));
        cards.forEach(card => {
            const existente = card.querySelector(".seed-nota-btn-v3839");
            const lote = encontrarLote(card);

            if (!lote || !lote.notaEntradaFoto) {
                if (existente) existente.remove();
                return;
            }

            if (existente) return;

            const botao = document.createElement("button");
            botao.type = "button";
            botao.className = "seed-nota-btn-v3839";
            botao.textContent = "📄 Ver nota";
            botao.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                abrirNota(lote);
            });
            card.appendChild(botao);
        });
    }

    function iniciar() {
        instalarEstilo();
        criarModal();
        decorarCards();

        const lista = document.getElementById("lista");
        if (lista && !observer) {
            observer = new MutationObserver(function () {
                window.requestAnimationFrame(decorarCards);
            });
            observer.observe(lista, { childList: true, subtree: true });
        }

        document.addEventListener("visibilitychange", function () {
            if (!document.hidden) decorarCards();
        });
        window.addEventListener("storage", decorarCards);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    } else {
        iniciar();
    }
})();
