// seedcontrol-detalhes-dashboard-v3915
(function(){
  "use strict";

  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const tipo = String(params.get("tipo") || "estoque").toLowerCase();
  const tiposValidos = new Set(["estoque","kg","sacas","cultivares","lotes","fazendas"]);
  const modo = tiposValidos.has(tipo) ? tipo : "estoque";

  function numero(v){
    if (v === null || v === undefined || v === "") return 0;
    if (typeof v === "string") v = v.replace(/\./g, "").replace(",", ".");
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  function texto(v){ return String(v == null ? "" : v).trim(); }
  function fmt(v,max=2){
    return new Intl.NumberFormat("pt-BR",{maximumFractionDigits:max}).format(numero(v));
  }
  function pesoBag(item){
    return numero(item.pesoBagKg || item.pesoPorBag || item.kgPorBag || item.pesoBag || 0);
  }
  function bags(item){ return numero(item.bags != null ? item.bags : item.quantidade); }
  function kg(item){
    const direto = numero(item.kgsMedia || item.kgMedia || item.kg || item.pesoTotalKg || item.pesoTotal || 0);
    if (direto) return direto;
    return bags(item) * pesoBag(item);
  }
  function sacas(item){
    const direto = numero(item.sacas60kg || item.sacas || 0);
    return direto || (kg(item) / 60);
  }
  function nomeFazenda(item){
    const v = texto(item.fazenda);
    return (!v || v === "0" || v === "-") ? "Sem fazenda informada" : v;
  }
  function nomeCultivar(item){ return texto(item.cultivar) || "Sem cultivar"; }
  function loteTexto(item){ return texto(item.lote) || "Sem código"; }
  function chave(s){
    return texto(s).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/\s+/g," ");
  }
  function carregar(){
    try{
      const x = JSON.parse(localStorage.getItem("estoque") || "[]");
      return Array.isArray(x) ? x : [];
    }catch(_){ return []; }
  }
  function dataMillis(item){
    const d = Date.parse(item && item.dataCadastro || "");
    if (Number.isFinite(d)) return d;
    const id = Number(item && item.id);
    return Number.isFinite(id) ? id : 0;
  }

  const estoque = carregar();
  const totalBags = estoque.reduce((s,x)=>s+bags(x),0);
  const totalKg = estoque.reduce((s,x)=>s+kg(x),0);

  const titulos = {
    estoque:["📦 Estoque Total","Estoque completo dividido por cultivar"],
    kg:["⚖️ Kg (Média)","Veja de onde vêm os quilos do estoque"],
    sacas:["🌾 Sacas (60 kg)","Detalhamento das sacas por cultivar e lote"],
    cultivares:["🌱 Cultivares","Quantidade, Kg, lotes e fazendas de cada cultivar"],
    lotes:["📋 Lotes","Todos os lotes e onde estão armazenados"],
    fazendas:["🚜 Fazendas","Quantidade, Kg, cultivares e lotes de cada fazenda"]
  };

  function resumo(){
    $("seedDetBags").textContent = fmt(totalBags,2);
    $("seedDetKg").textContent = `${fmt(totalKg,2)} kg`;
    $("seedDetLotes").textContent = fmt(estoque.length,0);
  }

  function agrupar(campo){
    const mapa = new Map();
    estoque.forEach((item,idx)=>{
      const nome = campo === "fazenda" ? nomeFazenda(item) : nomeCultivar(item);
      const k = chave(nome);
      if (!mapa.has(k)) mapa.set(k,{nome,bags:0,kg:0,sacas:0,lotes:[],cultivares:new Set(),fazendas:new Set(),talhoes:new Set()});
      const g = mapa.get(k);
      g.bags += bags(item);
      g.kg += kg(item);
      g.sacas += sacas(item);
      g.lotes.push({item,idx});
      g.cultivares.add(nomeCultivar(item));
      g.fazendas.add(nomeFazenda(item));
      const t = texto(item.talhao); if (t && t !== "0") g.talhoes.add(t);
    });
    return Array.from(mapa.values());
  }

  function htmlMetricas(b,k,s){
    return `<div class="seed-det-metricas">
      <div class="seed-det-metrica"><small>Bags</small><strong>${fmt(b,2)}</strong></div>
      <div class="seed-det-metrica"><small>Kg</small><strong>${fmt(k,2)}</strong></div>
      <div class="seed-det-metrica"><small>Sacas</small><strong>${fmt(s,2)}</strong></div>
    </div>`;
  }

  function htmlLote(item){
    return `<div class="seed-det-lote">
      <div class="seed-det-lote-titulo">📋 Lote ${escapeHtml(loteTexto(item))} · ${escapeHtml(nomeCultivar(item))}</div>
      <div class="seed-det-lote-info">📦 ${fmt(bags(item),2)} Bags · ⚖️ ${fmt(kg(item),2)} kg · 🌾 ${fmt(sacas(item),2)} sacas<br>🚜 ${escapeHtml(nomeFazenda(item))}${texto(item.talhao) && texto(item.talhao)!=="0" ? ` · 📍 Talhão ${escapeHtml(texto(item.talhao))}` : ""}${texto(item.peneira) ? ` · 🌾 Peneira ${escapeHtml(texto(item.peneira))}` : ""}</div>
    </div>`;
  }

  function escapeHtml(s){
    return texto(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  }

  function renderGrupo(grupo,kind){
    const extra = kind === "fazenda"
      ? `Cultivares: ${escapeHtml(Array.from(grupo.cultivares).join(", "))}`
      : `Fazendas: ${escapeHtml(Array.from(grupo.fazendas).join(", "))}`;
    const lotes = grupo.lotes.slice().sort((a,b)=>dataMillis(b.item)-dataMillis(a.item));
    return `<details class="seed-det-card" data-search="${escapeHtml([grupo.nome,...Array.from(grupo.cultivares),...Array.from(grupo.fazendas),...lotes.map(x=>loteTexto(x.item))].join(" "))}">
      <summary>
        <div class="seed-det-card-top"><h3>${kind === "fazenda" ? "🚜" : "🌱"} ${escapeHtml(grupo.nome)}</h3><span class="seed-det-badge">${grupo.lotes.length} lote${grupo.lotes.length===1?"":"s"}</span></div>
        ${htmlMetricas(grupo.bags,grupo.kg,grupo.sacas)}
        <div class="seed-det-meta">${extra}${grupo.talhoes.size ? `<br>Talhões: ${escapeHtml(Array.from(grupo.talhoes).join(", "))}` : ""}</div>
      </summary>
      <div class="seed-det-conteudo">${lotes.map(x=>htmlLote(x.item)).join("")}</div>
    </details>`;
  }

  function renderLote(item){
    const busca = [loteTexto(item),nomeCultivar(item),nomeFazenda(item),texto(item.talhao),texto(item.peneira)].join(" ");
    return `<details open class="seed-det-card" data-kind="lote" data-search="${escapeHtml(busca)}">
      <summary>
        <div class="seed-det-card-top"><h3>📋 Lote ${escapeHtml(loteTexto(item))}</h3><span class="seed-det-badge">${escapeHtml(texto(item.peneira)||"-")}</span></div>
        ${htmlMetricas(bags(item),kg(item),sacas(item))}
        <div class="seed-det-meta">🌱 ${escapeHtml(nomeCultivar(item))}<br>🚜 ${escapeHtml(nomeFazenda(item))}${texto(item.talhao)&&texto(item.talhao)!=="0"?` · 📍 Talhão ${escapeHtml(texto(item.talhao))}`:""}</div>
      </summary>
      <div class="seed-det-conteudo"><div class="seed-det-lote-info">💧 Umidade: ${texto(item.umidade)?escapeHtml(texto(item.umidade))+"%":"-"} · 🌡️ Temperatura: ${texto(item.temperatura)?escapeHtml(texto(item.temperatura))+" °C":"-"} · ⚖️ PMS: ${texto(item.pms)?escapeHtml(texto(item.pms))+" g":"-"}</div></div>
    </details>`;
  }

  function ordenarGrupos(lista){
    if (modo === "kg") return lista.sort((a,b)=>b.kg-a.kg);
    if (modo === "sacas") return lista.sort((a,b)=>b.sacas-a.sacas);
    return lista.sort((a,b)=>b.bags-a.bags);
  }

  function montar(){
    const [titulo,sub] = titulos[modo];
    $("seedDetTitulo").textContent = titulo;
    $("seedDetSubtitulo").textContent = sub;
    resumo();

    let html = "";
    let tituloLista = "Detalhamento";
    if (modo === "fazendas") {
      const grupos = ordenarGrupos(agrupar("fazenda"));
      html = grupos.map(g=>renderGrupo(g,"fazenda")).join("");
      tituloLista = "Fazendas";
    } else if (modo === "lotes") {
      const itens = estoque.slice().sort((a,b)=>dataMillis(b)-dataMillis(a));
      html = itens.map(renderLote).join("");
      tituloLista = "Lotes cadastrados";
    } else {
      const grupos = ordenarGrupos(agrupar("cultivar"));
      html = grupos.map(g=>renderGrupo(g,"cultivar")).join("");
      tituloLista = modo === "cultivares" ? "Cultivares" : modo === "kg" ? "Kg por cultivar" : modo === "sacas" ? "Sacas por cultivar" : "Estoque por cultivar";
    }
    $("seedDetListaTitulo").textContent = tituloLista;
    $("seedDetLista").innerHTML = html || '<div class="seed-det-vazio">Nenhum lote encontrado.</div>';
    atualizarContagem();
  }

  function atualizarContagem(){
    const cards = Array.from(document.querySelectorAll("#seedDetLista .seed-det-card"));
    const visiveis = cards.filter(c=>c.style.display !== "none").length;
    $("seedDetContagem").textContent = `${visiveis} item${visiveis===1?"":"s"}`;
  }

  function filtrar(){
    const termo = chave($("seedDetBusca").value);
    document.querySelectorAll("#seedDetLista .seed-det-card").forEach(card=>{
      const base = chave(card.getAttribute("data-search") || card.textContent);
      card.style.display = !termo || base.includes(termo) ? "" : "none";
    });
    atualizarContagem();
  }

  function voltar(){
    if (history.length > 1) history.back();
    else location.href = "index.html";
  }

  $("seedDetBusca").addEventListener("input",filtrar);
  $("seedDetVoltar").addEventListener("click",()=>location.href="index.html");
  $("seedDetVoltarTopo").addEventListener("click",voltar);
  montar();
})();
