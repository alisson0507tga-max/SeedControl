// seedcontrol-entrada-comercial-core-v3904
(function () {
    "use strict";

    const CHAVE = "seedcontrol_entrada_comercial_2026";
    const CAMPO_BACKUP = "entradaComercial2026";
    const MARCA = "seedcontrol-entrada-comercial-core-v3904";

    function numero(valor) {
        const n = Number(String(valor == null ? "" : valor).replace(",", "."));
        return Number.isFinite(n) ? n : 0;
    }

    function texto(valor) {
        return String(valor == null ? "" : valor).trim();
    }

    function hojeBR() {
        return new Date().toLocaleDateString("pt-BR");
    }

    function chaveLote(lote) {
        if (!lote || typeof lote !== "object") return "";
        if (texto(lote.id)) return "id:" + texto(lote.id);
        return [lote.cultivar, lote.lote, lote.fazenda, lote.peneira, lote.talhao, lote.bags]
            .map(v => texto(v).toLowerCase())
            .join("|");
    }

    function normalizarRegistro(item) {
        const r = item && typeof item === "object" ? item : {};
        const pms = numero(r.pms);
        const bags = numero(r.bags);
        const pesoBagKg = numero(r.pesoBagKg) || (pms > 0 ? pms * 5 : 0);
        const kg = numero(r.kg) || numero(r.kgsMedia) || (bags * pesoBagKg);
        return {
            id: texto(r.id) || ("EC-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8)),
            origemLoteId: texto(r.origemLoteId),
            origemChave: texto(r.origemChave),
            dataEntrada: texto(r.dataEntrada) || hojeBR(),
            cultivar: texto(r.cultivar),
            lote: texto(r.lote),
            bags,
            kg,
            pms,
            germinacao: texto(r.germinacao),
            observacao: texto(r.observacao),
            criadoEm: texto(r.criadoEm) || new Date().toISOString(),
            atualizadoEm: texto(r.atualizadoEm) || new Date().toISOString()
        };
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

    function carregar() {
        let lista = [];
        try {
            const bruto = localStorage.getItem(CHAVE);
            const parsed = bruto ? JSON.parse(bruto) : null;
            if (Array.isArray(parsed)) lista = parsed;
        } catch (_) {}

        if (!lista.length) {
            const cfg = lerConfiguracoes();
            if (Array.isArray(cfg[CAMPO_BACKUP])) lista = cfg[CAMPO_BACKUP];
        }

        return lista.map(normalizarRegistro);
    }

    function salvar(lista) {
        const normalizada = (Array.isArray(lista) ? lista : []).map(normalizarRegistro);
        localStorage.setItem(CHAVE, JSON.stringify(normalizada));
        const cfg = lerConfiguracoes();
        cfg[CAMPO_BACKUP] = normalizada;
        gravarConfiguracoes(cfg);
        try {
            window.dispatchEvent(new CustomEvent("seedcontrol:entrada-comercial-atualizada", { detail: { total: normalizada.length } }));
        } catch (_) {}
        return normalizada;
    }

    function calcularPesoBagPMS(pms) {
        const valor = numero(pms);
        return valor > 0 ? valor * 5 : 0;
    }

    function estimarBagsPorKg(kg, pms) {
        const pesoBag = calcularPesoBagPMS(pms);
        const pesoTotal = numero(kg);
        return pesoBag > 0 && pesoTotal > 0 ? pesoTotal / pesoBag : 0;
    }

    function registrarDoEstoque(lote) {
        if (!lote || typeof lote !== "object") return null;
        const lista = carregar();
        const origemId = texto(lote.id);
        const origemChave = chaveLote(lote);

        const existente = lista.find(item =>
            (origemId && item.origemLoteId === origemId) ||
            (!origemId && origemChave && item.origemChave === origemChave)
        );
        if (existente) return existente;

        const pms = numero(lote.pms);
        const bags = numero(lote.bags);
        const pesoBagKg = numero(lote.pesoBagKg) || calcularPesoBagPMS(pms);
        const registro = normalizarRegistro({
            origemLoteId: origemId,
            origemChave,
            dataEntrada: hojeBR(),
            cultivar: lote.cultivar,
            lote: lote.lote,
            bags,
            kg: numero(lote.kgsMedia) || numero(lote.kg) || (bags * pesoBagKg),
            pms,
            germinacao: "",
            observacao: ""
        });

        lista.unshift(registro);
        salvar(lista);
        return registro;
    }

    function elementoMetodo() {
        return document.getElementById("metodoPeso") ||
            document.querySelector('[name="metodoPeso"]') ||
            document.querySelector('select[id*="metodo" i], select[name*="metodo" i]');
    }

    function metodoComercial() {
        const el = elementoMetodo();
        if (!el) return false;
        const valor = texto(el.value).toLowerCase();
        return valor.includes("comercial") || valor === "pms" || valor.includes("pms");
    }

    function criarOpcaoCadastro() {
        const salvarBtn = document.getElementById("salvar");
        if (!salvarBtn || document.getElementById("entradaComercialOpcao3904")) return;

        const bloco = document.createElement("div");
        bloco.id = "entradaComercialOpcao3904";
        bloco.style.cssText = "margin:14px 0;padding:13px;border:1px solid rgba(74,222,128,.28);border-radius:13px;background:rgba(7,45,34,.55)";
        bloco.innerHTML = '<label style="display:flex;gap:10px;align-items:flex-start;margin:0;cursor:pointer"><input id="registrarEntradaComercial3904" type="checkbox" style="margin-top:3px"><span><strong>📥 Registrar na Entrada Comercial 2026</strong><small style="display:block;margin-top:4px;color:#aebdc2;line-height:1.35">Use para semente recebida de fora. No modo Comercial/PMS esta opção fica marcada automaticamente.</small></span></label>';
        salvarBtn.parentNode.insertBefore(bloco, salvarBtn);

        const checkbox = document.getElementById("registrarEntradaComercial3904");
        const metodo = elementoMetodo();

        function atualizar() {
            if (metodo) checkbox.checked = metodoComercial();
        }

        if (metodo) metodo.addEventListener("change", atualizar);
        atualizar();
    }

    function descobrirNovoLote(antes, depois) {
        const listaAntes = Array.isArray(antes) ? antes : [];
        const listaDepois = Array.isArray(depois) ? depois : [];
        const chavesAntes = new Set(listaAntes.map(chaveLote));
        const novo = listaDepois.find(item => !chavesAntes.has(chaveLote(item)));
        if (novo) return novo;
        if (listaDepois.length > listaAntes.length) return listaDepois[listaDepois.length - 1] || null;
        return null;
    }

    function instalarCapturaEstoque() {
        if (Storage.prototype.setItem.__seedEntradaComercial3904) return;

        const original = Storage.prototype.setItem;
        function setItemSeedControl(chave, valor) {
            let antes = null;
            const ehEstoque = this === window.localStorage && String(chave) === "estoque";
            if (ehEstoque) {
                try {
                    const bruto = window.localStorage.getItem("estoque");
                    antes = bruto ? JSON.parse(bruto) : [];
                } catch (_) {
                    antes = [];
                }
            }

            const retorno = original.apply(this, arguments);

            if (ehEstoque) {
                try {
                    const checkbox = document.getElementById("registrarEntradaComercial3904");
                    if (checkbox && checkbox.checked) {
                        const depois = JSON.parse(String(valor || "[]"));
                        const novo = descobrirNovoLote(antes, depois);
                        if (novo) registrarDoEstoque(novo);
                    }
                } catch (erro) {
                    console.error("Falha ao registrar Entrada Comercial 3904:", erro);
                }
            }

            return retorno;
        }

        setItemSeedControl.__seedEntradaComercial3904 = true;
        Storage.prototype.setItem = setItemSeedControl;
    }

    window.carregarEntradasComerciais3904 = carregar;
    window.salvarEntradasComerciais3904 = salvar;
    window.registrarEntradaComercial3904 = registrarDoEstoque;
    window.calcularPesoBagComercialPorPMS3904 = calcularPesoBagPMS;
    window.estimarBagsComerciaisPorKg3904 = estimarBagsPorKg;
    window.SEEDCONTROL_ENTRADA_COMERCIAL_3904 = MARCA;

    instalarCapturaEstoque();

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", criarOpcaoCadastro);
    } else {
        criarOpcaoCadastro();
    }
})();
