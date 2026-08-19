from pathlib import Path
import json

ROOT = Path("native/www")
DADOS = Path("assets/soja2026-v3830.json")
JS = ROOT / "dados-soja2026-v3830.js"

if not ROOT.exists():
    raise SystemExit("native/www não encontrado.")
if not DADOS.exists():
    raise SystemExit("assets/soja2026-v3830.json não encontrado.")

registros = json.loads(DADOS.read_text(encoding="utf-8"))
if not isinstance(registros, list) or len(registros) != 36:
    raise SystemExit("A base Soja 2026 precisa conter exatamente 36 lotes.")

dados_js = json.dumps(registros, ensure_ascii=False, separators=(",", ":"))

js = """// seedcontrol-dados-soja2026-v3830
(function () {
    "use strict";

    const MARCA = "seedcontrol_soja2026_v3830_importado";
    const REGISTROS = __DADOS__;

    function normalizar(valor) {
        return String(valor == null ? "" : valor)
            .normalize("NFD")
            .replace(/[\\u0300-\\u036f]/g, "")
            .toLowerCase()
            .trim()
            .replace(/\\s+/g, " ");
    }

    function chave(item) {
        return [
            normalizar(item.cultivar),
            normalizar(item.peneira),
            String(Number(item.lote) || 0),
            normalizar(item.fazenda),
            normalizar(item.talhao)
        ].join("|");
    }

    function carregar() {
        try {
            const dados = JSON.parse(localStorage.getItem("estoque") || "[]");
            return Array.isArray(dados) ? dados : [];
        } catch (_) {
            return [];
        }
    }

    function importar() {
        if (localStorage.getItem(MARCA) === "1") return;

        const estoque = carregar();
        const existentes = new Set(estoque.map(chave));
        const ids = new Set(
            estoque
                .map(item => Number(item && item.id))
                .filter(Number.isFinite)
        );

        let adicionados = 0;

        REGISTROS.forEach(function (origem, indice) {
            if (existentes.has(chave(origem))) return;

            let id = 2026081900000 + indice + 1;
            while (ids.has(id)) id++;

            const novo = Object.assign({
                id: id,
                dataCadastro: "2026-08-19T11:44:00-04:00",
                origem: "Soja 2026"
            }, origem);

            estoque.push(novo);
            existentes.add(chave(novo));
            ids.add(id);
            adicionados++;
        });

        if (adicionados > 0) {
            localStorage.setItem("estoque", JSON.stringify(estoque));
            try {
                window.dispatchEvent(
                    new CustomEvent("seedcontrol:atualizado", {
                        detail: {
                            origem: "Soja 2026",
                            adicionados: adicionados
                        }
                    })
                );
            } catch (_) {}
        }

        localStorage.setItem(MARCA, "1");
        localStorage.setItem(
            "seedcontrol_soja2026_v3830_adicionados",
            String(adicionados)
        );
    }

    importar();
})();
""".replace("__DADOS__", dados_js)

JS.write_text(js, encoding="utf-8")

injetados = 0
for pagina in ROOT.glob("*.html"):
    texto = pagina.read_text(encoding="utf-8")

    if "dados-soja2026-v3830.js" in texto:
        continue
    if "</body>" not in texto:
        continue

    texto = texto.replace(
        "</body>",
        '    <script src="dados-soja2026-v3830.js?v=3830"></script>\n</body>',
        1
    )
    pagina.write_text(texto, encoding="utf-8")
    injetados += 1

if injetados == 0:
    raise SystemExit("Nenhuma página recebeu o importador Soja 2026.")

final = JS.read_text(encoding="utf-8")
for marca in (
    "seedcontrol-dados-soja2026-v3830",
    "seedcontrol_soja2026_v3830_importado",
    "77i79 RSF(VORAZ)",
    "81SC118 i2x(mutum)",
    '"lote":36',
    '"bags":14',
    '"pesoBagKg":1050'
):
    if marca not in final:
        raise SystemExit(f"Validação dos dados falhou: {marca}")

print(
    "Dados Soja 2026 preparados: 36 lotes, sem duplicar e sem apagar estoque atual."
)
