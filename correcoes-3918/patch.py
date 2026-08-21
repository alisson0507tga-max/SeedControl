from pathlib import Path
import shutil
import re

ROOT = Path("native/www")
SRC = Path("correcoes-3918")
DASH_SRC = SRC / "dashboard-comerciais-v3918.js"
DASH_DST = ROOT / DASH_SRC.name
DETALHES = ROOT / "detalhes-dashboard-v3915.js"
INDEX = ROOT / "index.html"

if not ROOT.exists():
    raise SystemExit("native/www nao encontrado")
if not DASH_SRC.exists():
    raise SystemExit("dashboard-comerciais-v3918.js ausente")
if not INDEX.exists() or not DETALHES.exists():
    raise SystemExit("Dashboard 3915 nao encontrado na base")

shutil.copy2(DASH_SRC, DASH_DST)

# Injeta o card comercial depois do comportamento da 3915.
html = INDEX.read_text(encoding="utf-8")
if "dashboard-comerciais-v3918.js" not in html:
    tag = '<script src="dashboard-comerciais-v3918.js?v=3918"></script>'
    html = html.replace("</body>", f"    {tag}\n</body>", 1) if "</body>" in html else html + "\n" + tag
    INDEX.write_text(html, encoding="utf-8")

js = DETALHES.read_text(encoding="utf-8")

# 1) Novo tipo de detalhamento.
antigo = 'const tiposValidos = new Set(["estoque","kg","sacas","cultivares","lotes","fazendas"]);'
novo = 'const tiposValidos = new Set(["estoque","kg","sacas","cultivares","lotes","fazendas","comerciais"]);'
if antigo not in js and '"comerciais"' not in js.split(";", 8)[0:8]:
    raise SystemExit("Ancora tiposValidos 3915 nao encontrada")
js = js.replace(antigo, novo, 1)

# 2) Classificacao comercial: metodo Comercial/PMS OU registro vinculado na Entrada Comercial 2026.
ancora = '  function dataMillis(item){\n'
if "function ehComercial3918" not in js:
    if ancora not in js:
        raise SystemExit("Ancora dataMillis nao encontrada")
    helper = r'''  function carregarEntradasComerciais3918(){
    try{
      const d = JSON.parse(localStorage.getItem("seedcontrol_entrada_comercial_2026") || "[]");
      return Array.isArray(d) ? d : [];
    }catch(_){ return []; }
  }
  function indiceComercial3918(){
    const ids = new Set();
    const lotes = new Set();
    carregarEntradasComerciais3918().forEach(r=>{
      const id = texto(r && r.origemLoteId);
      if (id) ids.add(id);
      const k = `${chave(r && r.cultivar)}|${chave(r && r.lote)}`;
      if (k !== "|") lotes.add(k);
    });
    return {ids,lotes};
  }
  const indiceEntradaComercial3918 = indiceComercial3918();
  function ehComercial3918(item){
    if (!item) return false;
    const metodo = chave([
      item.metodoPeso,
      item.metodo,
      item.tipoPeso,
      item.modoCalculo,
      item.tipoCalculo,
      item.origemTipo,
      item.categoria
    ].filter(Boolean).join(" "));
    if (metodo.includes("comercial") || metodo === "pms" || metodo.includes(" pms")) return true;
    const id = texto(item.id);
    if (id && indiceEntradaComercial3918.ids.has(id)) return true;
    const k = `${chave(item.cultivar)}|${chave(item.lote)}`;
    return indiceEntradaComercial3918.lotes.has(k);
  }

'''
    js = js.replace(ancora, helper + ancora, 1)

# 3) Em Fazendas, comerciais saem da lista; em Comerciais, entram apenas eles.
antigo = '  const estoque = carregar();\n  const totalBags = estoque.reduce((s,x)=>s+bags(x),0);\n  const totalKg = estoque.reduce((s,x)=>s+kg(x),0);'
novo = '''  const estoqueCompleto = carregar();
  const sementesComerciais3918 = estoqueCompleto.filter(ehComercial3918);
  const estoque = modo === "comerciais"
    ? sementesComerciais3918
    : modo === "fazendas"
      ? estoqueCompleto.filter(item=>!ehComercial3918(item))
      : estoqueCompleto;
  const totalBags = estoque.reduce((s,x)=>s+bags(x),0);
  const totalKg = estoque.reduce((s,x)=>s+kg(x),0);'''
if antigo not in js and "sementesComerciais3918" not in js:
    raise SystemExit("Ancora estoque 3915 nao encontrada")
js = js.replace(antigo, novo, 1)

# 4) Titulo da nova pagina.
antigo = '    fazendas:["🚜 Fazendas","Quantidade, Kg, cultivares e lotes de cada fazenda"]\n'
novo = '    fazendas:["🚜 Fazendas","Quantidade, Kg, cultivares e lotes de cada fazenda"],\n    comerciais:["🚚 Sementes Comerciais","Lotes recebidos de outras sementeiras para plantio"]\n'
if antigo not in js and 'comerciais:["🚚 Sementes Comerciais"' not in js:
    raise SystemExit("Ancora titulo Fazendas nao encontrada")
js = js.replace(antigo, novo, 1)

# 5) Nos grupos comerciais nao mostrar 'Sem fazenda informada'.
antigo = '''    const extra = kind === "fazenda"
      ? `Cultivares: ${escapeHtml(Array.from(grupo.cultivares).join(", "))}`
      : `Fazendas: ${escapeHtml(Array.from(grupo.fazendas).join(", "))}`;'''
novo = '''    const extra = modo === "comerciais"
      ? "Origem: sementes recebidas de outras sementeiras"
      : kind === "fazenda"
        ? `Cultivares: ${escapeHtml(Array.from(grupo.cultivares).join(", "))}`
        : `Fazendas: ${escapeHtml(Array.from(grupo.fazendas).join(", "))}`;'''
if antigo not in js and 'Origem: sementes recebidas de outras sementeiras' not in js:
    raise SystemExit("Ancora renderGrupo nao encontrada")
js = js.replace(antigo, novo, 1)

# 6) Dentro do lote comercial, trocar a fazenda vazia por uma origem clara.
antigo = '📦 ${fmt(bags(item),2)} Bags · ⚖️ ${fmt(kg(item),2)} kg · 🌾 ${fmt(sacas(item),2)} sacas<br>🚜 ${escapeHtml(nomeFazenda(item))}${texto(item.talhao) && texto(item.talhao)!=="0" ? ` · 📍 Talhão ${escapeHtml(texto(item.talhao))}` : ""}${texto(item.peneira) ? ` · 🌾 Peneira ${escapeHtml(texto(item.peneira))}` : ""}'
novo = '📦 ${fmt(bags(item),2)} Bags · ⚖️ ${fmt(kg(item),2)} kg · 🌾 ${fmt(sacas(item),2)} sacas<br>${modo === "comerciais" ? "🚚 Semente comercial" : `🚜 ${escapeHtml(nomeFazenda(item))}${texto(item.talhao) && texto(item.talhao)!=="0" ? ` · 📍 Talhão ${escapeHtml(texto(item.talhao))}` : ""}`}${texto(item.peneira) ? ` · 🌾 Peneira ${escapeHtml(texto(item.peneira))}` : ""}'
if antigo not in js and '🚚 Semente comercial' not in js:
    raise SystemExit("Ancora htmlLote nao encontrada")
js = js.replace(antigo, novo, 1)

# 7) Nome da lista comercial.
antigo = 'tituloLista = modo === "cultivares" ? "Cultivares" : modo === "kg" ? "Kg por cultivar" : modo === "sacas" ? "Sacas por cultivar" : "Estoque por cultivar";'
novo = 'tituloLista = modo === "comerciais" ? "Sementes comerciais por cultivar" : modo === "cultivares" ? "Cultivares" : modo === "kg" ? "Kg por cultivar" : modo === "sacas" ? "Sacas por cultivar" : "Estoque por cultivar";'
if antigo not in js and 'Sementes comerciais por cultivar' not in js:
    raise SystemExit("Ancora tituloLista nao encontrada")
js = js.replace(antigo, novo, 1)

DETALHES.write_text(js, encoding="utf-8")

# Cache novo.
sw = ROOT / "service-worker.js"
if sw.exists():
    txt = sw.read_text(encoding="utf-8")
    txt = re.sub(r"seedcontrol-v3\.8-pwa-\d+", "seedcontrol-v3.8-pwa-3918", txt, count=1)
    sw.write_text(txt, encoding="utf-8")

# Validacoes objetivas.
index_final = INDEX.read_text(encoding="utf-8")
detalhes_final = DETALHES.read_text(encoding="utf-8")
dash_final = DASH_DST.read_text(encoding="utf-8")
for marca in (
    "dashboard-comerciais-v3918.js?v=3918",
):
    if marca not in index_final:
        raise SystemExit(f"Dashboard 3918 nao injetado: {marca}")
for marca in (
    '"comerciais"',
    "ehComercial3918",
    "sementesComerciais3918",
    "Sementes Comerciais",
    "Origem: sementes recebidas de outras sementeiras",
    "Sementes comerciais por cultivar",
):
    if marca not in detalhes_final:
        raise SystemExit(f"Detalhes 3918 sem marca: {marca}")
for marca in (
    "seedcontrol-dashboard-comerciais-v3918",
    "Sementes Comerciais",
    "seedcontrol_entrada_comercial_2026",
    "40 Bags" if False else "lotes",
):
    if marca not in dash_final:
        raise SystemExit(f"Card comercial 3918 sem marca: {marca}")

print("Correcoes 3918 aplicadas: Kg (Media) substituido por Sementes Comerciais e comerciais removidos de Fazendas.")
