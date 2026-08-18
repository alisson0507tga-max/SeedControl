from pathlib import Path

ROOT = Path('native/www')
HTML = ROOT / 'cadastro.html'
JS = ROOT / 'cadastro.js'
CSS = ROOT / 'cadastro-v384.css'
EXTRA = ROOT / 'cadastro-v384.js'

for arquivo in (HTML, JS):
    if not arquivo.exists():
        raise SystemExit(f'Arquivo não encontrado: {arquivo}')

html = HTML.read_text(encoding='utf-8')

if 'cadastro-v384.css' not in html:
    if '</head>' not in html:
        raise SystemExit('Não foi possível localizar </head> em cadastro.html')
    html = html.replace(
        '</head>',
        '    <link rel="stylesheet" href="cadastro-v384.css">\n</head>',
        1
    )

if 'cadastro-v384.js' not in html:
    if '</body>' not in html:
        raise SystemExit('Não foi possível localizar </body> em cadastro.html')
    html = html.replace(
        '</body>',
        '    <script src="cadastro-v384.js"></script>\n</body>',
        1
    )

HTML.write_text(html, encoding='utf-8')

css = r'''/* seedcontrol-cadastro-ui-v384 */

body.cadastro-v384 {
    min-height: 100vh;
    margin: 0;
    background:
        radial-gradient(circle at 100% 0%, rgba(34, 197, 94, .08), transparent 28%),
        linear-gradient(180deg, #06111a 0%, #071722 48%, #06141d 100%);
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

body.cadastro-v384 .topo {
    position: relative;
    overflow: hidden;
    padding: 24px 20px 22px;
    background:
        radial-gradient(circle at 90% 10%, rgba(34, 197, 94, .18), transparent 32%),
        linear-gradient(110deg, #071814 0%, #063322 58%, #06251d 100%);
    border-bottom: 1px solid rgba(74, 222, 128, .24);
    box-shadow: 0 10px 28px rgba(0, 0, 0, .26);
}

body.cadastro-v384 .topo::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(74, 222, 128, .76), transparent);
}

body.cadastro-v384 .topo h1 {
    margin: 0;
    color: #fff;
    font-size: clamp(30px, 8vw, 38px);
    line-height: 1.05;
    letter-spacing: -.6px;
}

body.cadastro-v384 .topo p {
    margin: 7px 0 0;
    color: #b7c5c9;
    font-size: 15px;
}

body.cadastro-v384 .container {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    padding: 18px 16px calc(28px + env(safe-area-inset-bottom));
}

body.cadastro-v384 .container > .card {
    margin: 0 0 15px;
    padding: 18px !important;
    border: 1px solid rgba(148, 163, 184, .18);
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(20, 38, 49, .98), rgba(10, 28, 39, .98));
    box-shadow: 0 10px 26px rgba(0, 0, 0, .22);
}

body.cadastro-v384 .card label {
    display: block;
    margin: 14px 0 7px;
    color: #e7eef0;
    font-size: 14px;
    font-weight: 700;
}

body.cadastro-v384 .card input:not([type="checkbox"]):not([type="file"]),
body.cadastro-v384 .card select,
body.cadastro-v384 .card textarea {
    width: 100%;
    min-height: 50px;
    margin: 0;
    padding: 0 14px;
    border: 1px solid rgba(148, 163, 184, .26) !important;
    border-radius: 13px !important;
    outline: none;
    background: rgba(6, 20, 29, .92) !important;
    color: #f8fafc !important;
    font-size: 15px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .02);
}

body.cadastro-v384 .card textarea {
    min-height: 90px;
    padding-top: 12px;
    padding-bottom: 12px;
}

body.cadastro-v384 .card input::placeholder,
body.cadastro-v384 .card textarea::placeholder {
    color: #7f9099 !important;
}

body.cadastro-v384 .card input:focus,
body.cadastro-v384 .card select:focus,
body.cadastro-v384 .card textarea:focus {
    border-color: rgba(74, 222, 128, .68) !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, .10) !important;
}

body.cadastro-v384 #salvar {
    width: 100%;
    min-height: 54px;
    margin-top: 18px;
    border: 1px solid rgba(103, 232, 85, .55);
    border-radius: 14px;
    background: linear-gradient(100deg, #147d36, #20a848 58%, #178d3b) !important;
    color: #fff;
    font-size: 16px;
    font-weight: 700;
    box-shadow: 0 7px 20px rgba(18, 112, 49, .18);
}

body.cadastro-v384 .container > button:not(#salvar) {
    min-height: 54px;
    border: 1px solid rgba(74, 222, 128, .40);
    border-radius: 14px;
    background: rgba(16, 74, 45, .58) !important;
    color: #e9fff0;
    box-shadow: none;
}

.nota-entrada-v384 {
    margin-top: 18px;
    padding: 15px;
    border: 1px solid rgba(74, 222, 128, .25);
    border-radius: 16px;
    background: linear-gradient(145deg, rgba(9, 48, 37, .56), rgba(7, 27, 35, .78));
}

.nota-entrada-v384 .nota-titulo {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-bottom: 5px;
    color: #fff;
    font-size: 18px;
    font-weight: 750;
}

.nota-entrada-v384 .nota-subtitulo {
    margin: 0 0 13px;
    color: #aebdc2;
    font-size: 12px;
    line-height: 1.45;
}

.nota-acoes-v384 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 9px;
}

.nota-acoes-v384 button {
    min-width: 0;
    min-height: 48px;
    margin: 0 !important;
    padding: 9px 8px;
    border: 1px solid rgba(74, 222, 128, .28);
    border-radius: 12px;
    background: rgba(15, 88, 50, .62) !important;
    color: #f5fff7;
    font-size: 13px;
    font-weight: 700;
    box-shadow: none !important;
}

.nota-preview-v384 {
    display: none;
    margin-top: 12px;
}

.nota-preview-v384.ativo {
    display: block;
}

.nota-preview-v384 img {
    display: block;
    width: 100%;
    max-height: 300px;
    object-fit: contain;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, .22);
    background: #06131b;
}

.nota-preview-acoes-v384 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 9px;
}

.nota-preview-acoes-v384 span {
    color: #74df89;
    font-size: 12px;
}

.nota-preview-acoes-v384 button {
    min-height: 40px;
    margin: 0 !important;
    padding: 7px 12px;
    border: 1px solid rgba(248, 113, 113, .30);
    border-radius: 10px;
    background: rgba(127, 29, 29, .58) !important;
    color: #fee2e2;
    font-size: 12px;
    box-shadow: none !important;
}

@media (max-width: 390px) {
    body.cadastro-v384 .container {
        padding-left: 12px;
        padding-right: 12px;
    }

    body.cadastro-v384 .container > .card {
        padding: 15px !important;
    }
}
'''

CSS.write_text(css, encoding='utf-8')

extra = r'''// seedcontrol-cadastro-nota-v384
(function () {
    "use strict";

    let fotoNotaAtual = "";

    function valor(id) {
        const el = document.getElementById(id);
        return el ? String(el.value || "").trim() : "";
    }

    function normalizar(v) {
        return String(v == null ? "" : v).trim().toLowerCase();
    }

    function mesmoLote(item) {
        if (!item) return false;

        return (
            normalizar(item.cultivar) === normalizar(valor("cultivar")) &&
            String(Number(item.lote) || "") === String(Number(valor("lote")) || "") &&
            normalizar(item.fazenda) === normalizar(valor("fazenda")) &&
            normalizar(item.peneira) === normalizar(valor("peneira")) &&
            normalizar(item.talhao) === normalizar(valor("talhao"))
        );
    }

    function comprimirImagem(arquivo) {
        return new Promise(function (resolve, reject) {
            if (!arquivo || !arquivo.type || !arquivo.type.startsWith("image/")) {
                reject(new Error("Selecione uma imagem válida."));
                return;
            }

            const leitor = new FileReader();

            leitor.onerror = function () {
                reject(new Error("Não foi possível ler a foto."));
            };

            leitor.onload = function () {
                const imagem = new Image();

                imagem.onerror = function () {
                    reject(new Error("Não foi possível abrir a foto."));
                };

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
                    if (resultado.length > 650000) {
                        resultado = canvas.toDataURL("image/jpeg", 0.48);
                    }

                    resolve(resultado);
                };

                imagem.src = String(leitor.result || "");
            };

            leitor.readAsDataURL(arquivo);
        });
    }

    function atualizarPreview() {
        const bloco = document.getElementById("notaPreviewV384");
        const img = document.getElementById("notaPreviewImgV384");
        if (!bloco || !img) return;

        if (fotoNotaAtual) {
            img.src = fotoNotaAtual;
            bloco.classList.add("ativo");
        } else {
            img.removeAttribute("src");
            bloco.classList.remove("ativo");
        }
    }

    async function receberArquivo(arquivo) {
        try {
            fotoNotaAtual = await comprimirImagem(arquivo);
            atualizarPreview();
        } catch (erro) {
            alert(erro && erro.message ? erro.message : "Não foi possível adicionar a foto.");
        }
    }

    function criarAreaNota() {
        const salvar = document.getElementById("salvar");
        if (!salvar || document.getElementById("notaEntradaV384")) return;

        const bloco = document.createElement("section");
        bloco.id = "notaEntradaV384";
        bloco.className = "nota-entrada-v384";
        bloco.innerHTML = `
            <div class="nota-titulo">📄 Nota de entrada <small style="font-size:11px;color:#91a3aa;font-weight:600">(opcional)</small></div>
            <p class="nota-subtitulo">Anexe a foto da nota recebida com a semente. A imagem será vinculada a este lote e incluída no backup.</p>
            <div class="nota-acoes-v384">
                <button type="button" id="btnNotaCameraV384">📷 Tirar foto</button>
                <button type="button" id="btnNotaGaleriaV384">🖼️ Galeria</button>
            </div>
            <input id="notaCameraV384" type="file" accept="image/*" capture="environment" hidden>
            <input id="notaGaleriaV384" type="file" accept="image/*" hidden>
            <div class="nota-preview-v384" id="notaPreviewV384">
                <img id="notaPreviewImgV384" alt="Prévia da nota de entrada">
                <div class="nota-preview-acoes-v384">
                    <span>✓ Foto anexada</span>
                    <button type="button" id="btnNotaRemoverV384">Remover</button>
                </div>
            </div>
        `;

        salvar.parentNode.insertBefore(bloco, salvar);

        const camera = document.getElementById("notaCameraV384");
        const galeria = document.getElementById("notaGaleriaV384");

        document.getElementById("btnNotaCameraV384").addEventListener("click", function () {
            camera.value = "";
            camera.click();
        });

        document.getElementById("btnNotaGaleriaV384").addEventListener("click", function () {
            galeria.value = "";
            galeria.click();
        });

        camera.addEventListener("change", function () {
            if (camera.files && camera.files[0]) receberArquivo(camera.files[0]);
        });

        galeria.addEventListener("change", function () {
            if (galeria.files && galeria.files[0]) receberArquivo(galeria.files[0]);
        });

        document.getElementById("btnNotaRemoverV384").addEventListener("click", function () {
            fotoNotaAtual = "";
            atualizarPreview();
        });
    }

    function protegerPersistenciaDaNota() {
        if (typeof window.salvarEstoque !== "function") return;
        if (window.salvarEstoque.__seedcontrolNotaV384) return;

        const original = window.salvarEstoque;

        function salvarComNota(lista) {
            if (fotoNotaAtual && Array.isArray(lista)) {
                for (let i = lista.length - 1; i >= 0; i -= 1) {
                    if (mesmoLote(lista[i])) {
                        lista[i].notaEntradaFoto = fotoNotaAtual;
                        lista[i].notaEntradaTipo = "image/jpeg";
                        lista[i].notaEntradaAtualizadaEm = new Date().toISOString();
                        break;
                    }
                }
            }

            return original(lista);
        }

        salvarComNota.__seedcontrolNotaV384 = true;
        window.salvarEstoque = salvarComNota;
    }

    function iniciar() {
        document.body.classList.add("cadastro-v384");
        criarAreaNota();
        protegerPersistenciaDaNota();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar);
    } else {
        iniciar();
    }
})();
'''

EXTRA.write_text(extra, encoding='utf-8')

html_final = HTML.read_text(encoding='utf-8')
css_final = CSS.read_text(encoding='utf-8')
extra_final = EXTRA.read_text(encoding='utf-8')

checks = [
    ('cadastro-v384.css', html_final),
    ('cadastro-v384.js', html_final),
    ('seedcontrol-cadastro-ui-v384', css_final),
    ('notaEntradaV384', extra_final),
    ('Tirar foto', extra_final),
    ('Galeria', extra_final),
    ('notaEntradaFoto', extra_final),
    ('window.salvarEstoque = salvarComNota', extra_final),
]

for trecho, conteudo in checks:
    if trecho not in conteudo:
        raise SystemExit(f'Validação do Novo Lote falhou: {trecho}')

print('Novo Lote v3.8.4 modernizado com foto opcional da nota de entrada.')
