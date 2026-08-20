// seedcontrol-entrada-comercial-foto-v3907
(function () {
    "use strict";

    const CHAVE_NOTAS = "seedcontrol_entrada_comercial_notas_2026";
    const CAMPO_BACKUP = "entradaComercialNotas2026";
    const $ = id => document.getElementById(id);

    const carregarBase = window.carregarEntradasComerciais3904;
    const salvarBase = window.salvarEntradasComerciais3904;

    if (typeof carregarBase !== "function" || typeof salvarBase !== "function") {
        console.error("Entrada Comercial 3904 não disponível para extensão de fotos.");
        return;
    }

    let idEdicao3907 = "";
    let fotoAtual3907 = "";

    function texto(v) {
        return String(v == null ? "" : v).trim();
    }

    function norm(v) {
        return texto(v).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    function numero(v) {
        const n = Number(String(v == null ? "" : v).replace(",", "."));
        return Number.isFinite(n) ? n : 0;
    }

    function lerConfiguracoes() {
        try {
            if (typeof window.carregarConfiguracoes === "function") {
                const cfg = window.carregarConfiguracoes();
                return cfg && typeof cfg === "object" && !Array.isArray(cfg) ? cfg : {};
            }
            const bruto = localStorage.getItem("configuracoes");
            const cfg = bruto ? JSON.parse(bruto) : {};
            return cfg && typeof cfg === "object" && !Array.isArray(cfg) ? cfg : {};
        } catch (_) {
            return {};
        }
    }

    function gravarConfiguracoes(cfg) {
        try {
            if (typeof window.salvarConfiguracoes === "function") {
                window.salvarConfiguracoes(cfg);
            } else {
                localStorage.setItem("configuracoes", JSON.stringify(cfg));
            }
        } catch (_) {}
    }

    function carregarMapaNotas() {
        let mapa = {};
        try {
            const bruto = localStorage.getItem(CHAVE_NOTAS);
            const parsed = bruto ? JSON.parse(bruto) : null;
            if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) mapa = parsed;
        } catch (_) {}

        if (!Object.keys(mapa).length) {
            const cfg = lerConfiguracoes();
            const salvo = cfg[CAMPO_BACKUP];
            if (salvo && typeof salvo === "object" && !Array.isArray(salvo)) mapa = salvo;
        }

        return mapa;
    }

    function salvarMapaNotas(mapa) {
        const limpo = mapa && typeof mapa === "object" && !Array.isArray(mapa) ? mapa : {};
        localStorage.setItem(CHAVE_NOTAS, JSON.stringify(limpo));
        const cfg = lerConfiguracoes();
        cfg[CAMPO_BACKUP] = limpo;
        gravarConfiguracoes(cfg);
    }

    function carregarEstoque() {
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

    function acharLoteEstoque(registro, estoque) {
        const lista = Array.isArray(estoque) ? estoque : carregarEstoque();
        const origem = texto(registro && registro.origemLoteId);
        if (origem) {
            const porId = lista.find(item => texto(item && item.id) === origem);
            if (porId) return porId;
        }

        const cultivar = norm(registro && registro.cultivar);
        const lote = norm(registro && registro.lote);
        if (!cultivar || !lote) return null;

        const iguais = lista.filter(item =>
            norm(item && item.cultivar) === cultivar &&
            norm(item && item.lote) === lote
        );

        return iguais.length === 1 ? iguais[0] : null;
    }

    function fotoDoRegistro(registro) {
        if (!registro) return "";
        const mapa = carregarMapaNotas();
        const propria = texto(mapa[texto(registro.id)]);
        if (propria) return propria;
        const lote = acharLoteEstoque(registro);
        return texto(lote && lote.notaEntradaFoto);
    }

    function sincronizarComEstoque(registro, foto) {
        try {
            const estoque = carregarEstoque();
            const lote = acharLoteEstoque(registro, estoque);
            if (!lote) return false;

            const indice = estoque.indexOf(lote);
            if (indice < 0) return false;

            estoque[indice] = { ...lote, notaEntradaFoto: foto || "" };

            if (typeof window.salvarEstoque === "function") {
                try {
                    window.salvarEstoque(estoque);
                    return true;
                } catch (_) {}
            }

            localStorage.setItem("estoque", JSON.stringify(estoque));
            return true;
        } catch (erro) {
            console.error("Falha ao sincronizar nota com Estoque:", erro);
            return false;
        }
    }

    function comprimirImagem(arquivo) {
        return new Promise(function (resolve, reject) {
            if (!arquivo || !arquivo.type || !arquivo.type.startsWith("image/")) {
                reject(new Error("Selecione uma imagem válida."));
                return;
            }

            const leitor = new FileReader();
            leitor.onerror = () => reject(new Error("Não foi possível ler a foto."));
            leitor.onload = function () {
                const imagem = new Image();
                imagem.onerror = () => reject(new Error("Não foi possível abrir a foto."));
                imagem.onload = function () {
                    const limite = 1100;
                    let largura = imagem.naturalWidth || imagem.width;
                    let altura = imagem.naturalHeight || imagem.height;

                    if (largura > limite || altura > limite) {
                        const escala = Math.min(limite / largura, limite / altura);
                        largura = Math.max(1, Math.round(largura * escala));
                        altura = Math.max(1, Math.round(altura * escala));
                    }

                    const canvas = document.createElement("canvas");
                    canvas.width = largura;
                    canvas.height = altura;
                    const ctx = canvas.getContext("2d", { alpha: false });
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(0, 0, largura, altura);
                    ctx.drawImage(imagem, 0, 0, largura, altura);

                    let resultado = canvas.toDataURL("image/jpeg", 0.66);
                    if (resultado.length > 650000) resultado = canvas.toDataURL("image/jpeg", 0.48);
                    resolve(resultado);
                };
                imagem.src = String(leitor.result || "");
            };
            leitor.readAsDataURL(arquivo);
        });
    }

    function instalarEstilo() {
        if ($("seedFotoComercial3907Style")) return;
        const style = document.createElement("style");
        style.id = "seedFotoComercial3907Style";
        style.textContent = `
            .ec-foto-3907{grid-column:1/-1;margin-top:4px;padding:14px;border:1px solid rgba(74,222,128,.28);border-radius:15px;background:rgba(5,40,31,.48)}
            .ec-foto-3907 h3{margin:0 0 5px;font-size:17px;color:#fff}.ec-foto-3907 p{margin:0 0 12px;color:#aebdc2;font-size:12px;line-height:1.4}
            .ec-foto-acoes-3907{display:grid;grid-template-columns:1fr 1fr;gap:9px}.ec-foto-acoes-3907 button,.ec-foto-preview-acoes-3907 button{min-height:46px;border-radius:11px;border:1px solid rgba(74,222,128,.3);background:#0d6435;color:#fff;font:inherit;font-weight:700}
            .ec-foto-preview-3907{display:none;margin-top:12px}.ec-foto-preview-3907.ativo{display:block}.ec-foto-preview-3907 img{display:block;width:100%;max-height:280px;object-fit:contain;border-radius:12px;background:#06131b;border:1px solid rgba(148,163,184,.22)}
            .ec-foto-preview-acoes-3907{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:9px}.ec-foto-preview-acoes-3907 .remover{background:rgba(127,29,29,.72);border-color:rgba(248,113,113,.32)}
            .ec-nota-rapida-3907{margin-right:5px;min-width:36px;min-height:36px;border-radius:8px;border:1px solid rgba(74,222,128,.3);background:#0d6435;color:#fff}
            .ec-nota-modal-3907{position:fixed;inset:0;z-index:2147483000;display:none;flex-direction:column;background:rgba(2,8,12,.96);padding:max(14px,env(safe-area-inset-top)) 12px max(14px,env(safe-area-inset-bottom));color:#fff}.ec-nota-modal-3907.ativo{display:flex}
            .ec-nota-modal-top-3907{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:4px 4px 12px}.ec-nota-modal-top-3907 button{min-width:44px;min-height:44px;border-radius:11px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);color:#fff;font-size:21px}
            .ec-nota-modal-area-3907{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:auto;border-radius:14px;background:#02090d}.ec-nota-modal-area-3907 img{max-width:100%;max-height:100%;object-fit:contain}
        `;
        document.head.appendChild(style);
    }

    function instalarAreaFoto() {
        const grid = document.querySelector("#ecModal .ec3904-form-grid");
        if (!grid || $("ecFotoBloco3907")) return;

        const bloco = document.createElement("section");
        bloco.id = "ecFotoBloco3907";
        bloco.className = "ec-foto-3907";
        bloco.innerHTML = `
            <h3>📄 Nota de entrada <small style="font-size:11px;color:#91a3aa">(opcional)</small></h3>
            <p>Tire uma foto ou escolha na galeria. Se esta entrada estiver ligada a um lote do Estoque, a mesma nota aparecerá nos dois lugares.</p>
            <div class="ec-foto-acoes-3907">
                <button id="ecFotoCameraBtn3907" type="button">📷 Tirar foto</button>
                <button id="ecFotoGaleriaBtn3907" type="button">🖼️ Galeria</button>
            </div>
            <input id="ecFotoCamera3907" type="file" accept="image/*" capture="environment" hidden>
            <input id="ecFotoGaleria3907" type="file" accept="image/*" hidden>
            <div id="ecFotoPreview3907" class="ec-foto-preview-3907">
                <img id="ecFotoImg3907" alt="Nota de entrada">
                <div class="ec-foto-preview-acoes-3907">
                    <button id="ecFotoVer3907" type="button">📄 Ver nota</button>
                    <button id="ecFotoRemover3907" class="remover" type="button">🗑 Remover</button>
                </div>
            </div>
        `;
        grid.appendChild(bloco);

        const camera = $("ecFotoCamera3907");
        const galeria = $("ecFotoGaleria3907");
        $("ecFotoCameraBtn3907").addEventListener("click", () => { camera.value = ""; camera.click(); });
        $("ecFotoGaleriaBtn3907").addEventListener("click", () => { galeria.value = ""; galeria.click(); });
        camera.addEventListener("change", () => camera.files && camera.files[0] && receberArquivo(camera.files[0]));
        galeria.addEventListener("change", () => galeria.files && galeria.files[0] && receberArquivo(galeria.files[0]));
        $("ecFotoRemover3907").addEventListener("click", () => { fotoAtual3907 = ""; atualizarPreview(); });
        $("ecFotoVer3907").addEventListener("click", () => abrirVisualizador(fotoAtual3907));
    }

    async function receberArquivo(arquivo) {
        try {
            fotoAtual3907 = await comprimirImagem(arquivo);
            atualizarPreview();
        } catch (erro) {
            alert(erro && erro.message ? erro.message : "Não foi possível adicionar a foto.");
        }
    }

    function atualizarPreview() {
        const bloco = $("ecFotoPreview3907");
        const img = $("ecFotoImg3907");
        if (!bloco || !img) return;
        if (fotoAtual3907) {
            img.src = fotoAtual3907;
            bloco.classList.add("ativo");
        } else {
            img.removeAttribute("src");
            bloco.classList.remove("ativo");
        }
    }

    function criarVisualizador() {
        if ($("ecNotaModal3907")) return;
        const modal = document.createElement("div");
        modal.id = "ecNotaModal3907";
        modal.className = "ec-nota-modal-3907";
        modal.innerHTML = `
            <div class="ec-nota-modal-top-3907"><strong>Nota de entrada</strong><button id="ecNotaFechar3907" type="button">✕</button></div>
            <div class="ec-nota-modal-area-3907"><img id="ecNotaImagem3907" alt="Nota de entrada"></div>
        `;
        document.body.appendChild(modal);
        $("ecNotaFechar3907").addEventListener("click", fecharVisualizador);
        modal.addEventListener("click", e => { if (e.target === modal) fecharVisualizador(); });
    }

    function abrirVisualizador(foto) {
        if (!foto) return;
        criarVisualizador();
        $("ecNotaImagem3907").src = foto;
        $("ecNotaModal3907").classList.add("ativo");
    }

    function fecharVisualizador() {
        const modal = $("ecNotaModal3907");
        if (modal) modal.classList.remove("ativo");
    }

    function registroPorId(id) {
        return carregarBase().find(r => texto(r.id) === texto(id)) || null;
    }

    function prepararNovaEntrada() {
        idEdicao3907 = "";
        fotoAtual3907 = "";
        setTimeout(atualizarPreview, 0);
    }

    function prepararEdicao(id) {
        idEdicao3907 = texto(id);
        const registro = registroPorId(idEdicao3907);
        fotoAtual3907 = fotoDoRegistro(registro);
        setTimeout(atualizarPreview, 0);
    }

    function salvarComFoto(evento) {
        evento.preventDefault();
        evento.stopImmediatePropagation();

        const cultivar = texto($("ecCultivar") && $("ecCultivar").value);
        const lote = texto($("ecLote") && $("ecLote").value);
        if (!cultivar || !lote) {
            alert("Informe cultivar e lote.");
            return;
        }

        const atual = carregarBase();
        const antigo = atual.find(r => texto(r.id) === idEdicao3907);
        const agora = new Date().toISOString();
        const registro = {
            ...(antigo || {}),
            id: idEdicao3907 || ("EC-" + Date.now()),
            dataEntrada: texto($("ecData") && $("ecData").value),
            cultivar,
            lote,
            bags: numero($("ecBags") && $("ecBags").value),
            kg: numero($("ecKg") && $("ecKg").value),
            pms: numero($("ecPms") && $("ecPms").value),
            germinacao: texto($("ecGerminacao") && $("ecGerminacao").value),
            observacao: texto($("ecObservacao") && $("ecObservacao").value),
            atualizadoEm: agora
        };
        if (!registro.criadoEm) registro.criadoEm = agora;

        if (idEdicao3907) {
            const i = atual.findIndex(r => texto(r.id) === idEdicao3907);
            if (i >= 0) atual[i] = registro;
        } else {
            atual.unshift(registro);
        }

        const mapa = carregarMapaNotas();
        if (fotoAtual3907) mapa[registro.id] = fotoAtual3907;
        else delete mapa[registro.id];
        salvarMapaNotas(mapa);

        salvarBase(atual);
        sincronizarComEstoque(registro, fotoAtual3907);

        const modal = $("ecModal");
        if (modal) modal.hidden = true;
        idEdicao3907 = "";
        fotoAtual3907 = "";
        try { window.dispatchEvent(new CustomEvent("seedcontrol:entrada-comercial-atualizada")); } catch (_) {}
    }

    function limparFotoAoExcluir() {
        if (!idEdicao3907) return;
        const mapa = carregarMapaNotas();
        delete mapa[idEdicao3907];
        salvarMapaNotas(mapa);
    }

    function decorarTabela() {
        const corpo = $("ecCorpo");
        if (!corpo) return;
        Array.from(corpo.querySelectorAll("tr[data-id]")).forEach(tr => {
            if (tr.querySelector(".ec-nota-rapida-3907")) return;
            const id = texto(tr.dataset.id);
            const registro = registroPorId(id);
            const foto = fotoDoRegistro(registro);
            if (!foto) return;
            const celula = tr.lastElementChild;
            if (!celula) return;
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "ec-nota-rapida-3907";
            btn.textContent = "📄";
            btn.title = "Ver nota";
            btn.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); abrirVisualizador(fotoDoRegistro(registro)); });
            celula.insertBefore(btn, celula.firstChild);
        });
    }

    function iniciar() {
        instalarEstilo();
        instalarAreaFoto();
        criarVisualizador();

        const novo = $("ecNovo");
        const corpo = $("ecCorpo");
        const salvar = $("ecSalvar");
        const excluir = $("ecExcluir");
        const fechar = $("ecFechar");

        if (novo) novo.addEventListener("click", prepararNovaEntrada, true);
        if (corpo) {
            corpo.addEventListener("click", e => {
                const b = e.target.closest("[data-editar]");
                if (b) prepararEdicao(b.dataset.editar);
            }, true);
            new MutationObserver(() => requestAnimationFrame(decorarTabela)).observe(corpo, { childList:true, subtree:true });
        }
        if (salvar) salvar.addEventListener("click", salvarComFoto, true);
        if (excluir) excluir.addEventListener("click", limparFotoAoExcluir, true);
        if (fechar) fechar.addEventListener("click", () => { idEdicao3907 = ""; fotoAtual3907 = ""; }, true);

        window.addEventListener("seedcontrol:entrada-comercial-atualizada", () => requestAnimationFrame(decorarTabela));
        decorarTabela();
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once:true });
    else iniciar();
})();
