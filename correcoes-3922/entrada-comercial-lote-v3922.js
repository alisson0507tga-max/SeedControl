// seedcontrol-entrada-comercial-lote-v3922
(function () {
  "use strict";

  const carregarBase = window.carregarEntradasComerciais3904;
  const salvarBase = window.salvarEntradasComerciais3904;
  let salvandoReparo = false;

  if (typeof carregarBase !== "function" || typeof salvarBase !== "function") {
    console.error("SeedControl 3922: Entrada Comercial 3904 não disponível.");
    return;
  }

  function texto(v) {
    return String(v == null ? "" : v).trim();
  }

  function norm(v) {
    return texto(v)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function numero(v) {
    if (v == null || v === "") return 0;
    const n = Number(String(v).replace(/\./g, "").replace(",", "."));
    return Number.isFinite(n) ? n : 0;
  }

  function quaseIgual(a, b, tolerancia) {
    return Math.abs(numero(a) - numero(b)) <= (tolerancia == null ? 0.01 : tolerancia);
  }

  function loteValido(v) {
    const t = texto(v);
    return !!t && t !== "0" && t !== "-";
  }

  function carregarEstoque3922() {
    try {
      if (typeof window.carregarEstoque === "function") {
        const dados = window.carregarEstoque();
        if (Array.isArray(dados)) return dados;
      }
    } catch (_) {}

    try {
      const dados = JSON.parse(localStorage.getItem("estoque") || "[]");
      return Array.isArray(dados) ? dados : [];
    } catch (_) {
      return [];
    }
  }

  function chaveEstoque(item) {
    if (!item || typeof item !== "object") return "";
    const id = texto(item.id);
    if (id) return "id:" + id;
    return [item.cultivar, item.lote, item.fazenda, item.peneira, item.talhao, item.bags]
      .map(v => texto(v).toLowerCase())
      .join("|");
  }

  function bagsEstoque(item) {
    return numero(item && (item.bags != null ? item.bags : item.quantidade));
  }

  function kgEstoque(item) {
    if (!item) return 0;
    const direto = numero(item.kgsMedia || item.kgMedia || item.kg || item.pesoTotalKg || item.pesoTotal || 0);
    if (direto) return direto;
    const pesoBag = numero(item.pesoBagKg || item.pesoPorBag || item.kgPorBag || item.pesoBag || 0) || numero(item.pms) * 5;
    return bagsEstoque(item) * pesoBag;
  }

  function candidatosUnicos(lista, predicado) {
    const encontrados = lista.filter(item => loteValido(item && item.lote) && predicado(item));
    return encontrados.length === 1 ? encontrados[0] : null;
  }

  function acharLote3922(registro, estoque) {
    if (!registro || typeof registro !== "object") return null;
    const lista = Array.isArray(estoque) ? estoque : carregarEstoque3922();

    const origemId = texto(registro.origemLoteId);
    if (origemId) {
      const porId = lista.find(item => texto(item && item.id) === origemId && loteValido(item && item.lote));
      if (porId) return porId;
    }

    const origemChave = texto(registro.origemChave);
    if (origemChave) {
      const porChave = lista.find(item => chaveEstoque(item) === origemChave && loteValido(item && item.lote));
      if (porChave) return porChave;
    }

    const cultivar = norm(registro.cultivar);
    if (!cultivar) return null;

    const bags = numero(registro.bags);
    const pms = numero(registro.pms);
    const kg = numero(registro.kg);

    let achado = candidatosUnicos(lista, item =>
      norm(item.cultivar) === cultivar &&
      quaseIgual(bagsEstoque(item), bags, 0.001) &&
      (pms <= 0 || quaseIgual(item.pms, pms, 0.01)) &&
      (kg <= 0 || quaseIgual(kgEstoque(item), kg, Math.max(0.1, kg * 0.00001)))
    );
    if (achado) return achado;

    achado = candidatosUnicos(lista, item =>
      norm(item.cultivar) === cultivar &&
      quaseIgual(bagsEstoque(item), bags, 0.001) &&
      (pms <= 0 || quaseIgual(item.pms, pms, 0.01))
    );
    if (achado) return achado;

    return candidatosUnicos(lista, item =>
      norm(item.cultivar) === cultivar &&
      quaseIgual(bagsEstoque(item), bags, 0.001)
    );
  }

  function repararLista3922(lista, persistir) {
    const estoque = carregarEstoque3922();
    let alterou = false;

    const reparada = (Array.isArray(lista) ? lista : []).map(registro => {
      if (!registro || typeof registro !== "object" || loteValido(registro.lote)) return registro;

      const loteEstoque = acharLote3922(registro, estoque);
      const codigo = texto(loteEstoque && loteEstoque.lote);
      if (!loteValido(codigo)) return registro;

      alterou = true;
      return {
        ...registro,
        lote: codigo,
        origemLoteId: texto(registro.origemLoteId) || texto(loteEstoque.id),
        origemChave: texto(registro.origemChave) || chaveEstoque(loteEstoque),
        atualizadoEm: new Date().toISOString()
      };
    });

    if (alterou && persistir && !salvandoReparo) {
      salvandoReparo = true;
      try {
        salvarBase(reparada);
        console.info("SeedControl 3922: lote ausente da Entrada Comercial recuperado do Estoque.");
      } catch (erro) {
        console.error("SeedControl 3922: falha ao persistir lote recuperado.", erro);
      } finally {
        salvandoReparo = false;
      }
    }

    return reparada;
  }

  window.carregarEntradasComerciais3904 = function () {
    return repararLista3922(carregarBase(), true);
  };

  window.salvarEntradasComerciais3904 = function (lista) {
    return salvarBase(repararLista3922(lista, false));
  };

  window.seedResolverLoteEntradaComercial3922 = function (registro) {
    const lote = acharLote3922(registro, carregarEstoque3922());
    return loteValido(registro && registro.lote) ? texto(registro.lote) : texto(lote && lote.lote);
  };

  // Executa uma vez já na abertura. A UI carregada depois deste script passa a receber os dados reparados.
  try { window.carregarEntradasComerciais3904(); } catch (_) {}
})();
