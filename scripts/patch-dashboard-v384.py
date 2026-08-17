from pathlib import Path

ROOT = Path("native/www")
INDEX = ROOT / "index.html"
CSS = ROOT / "dashboard-v384.css"
SW = ROOT / "service-worker.js"

if not INDEX.exists():
    raise SystemExit("index.html não encontrado em native/www")

index_html = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#071713">
    <title>SeedControl</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="dashboard-v384.css">
    <link rel="manifest" href="manifest.json">
</head>
<body class="dashboard-body">

<header class="dashboard-topo">
    <div class="dashboard-brand">
        <div class="dashboard-brand-icon" aria-hidden="true">🌱</div>
        <div class="dashboard-brand-copy">
            <h1><span>Seed</span><strong>Control</strong></h1>
            <p>Controle Inteligente de Sementes</p>
        </div>
    </div>
</header>

<main class="container dashboard-container">

    <!-- Mantido apenas para compatibilidade com app.js; não é exibido. -->
    <div id="alertasEstoque" hidden aria-hidden="true"></div>

    <section id="dashboard" class="dashboard-metricas" aria-label="Resumo do estoque">
        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">📦</div>
            <div class="metric-copy">
                <h2>Estoque Total</h2>
                <h1 id="estoqueTotal">0 Bags</h1>
            </div>
        </article>

        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">⚖️</div>
            <div class="metric-copy">
                <h2>Kg (Média)</h2>
                <h1 id="estoqueKgTotal">0 kg</h1>
            </div>
        </article>

        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">🌾</div>
            <div class="metric-copy">
                <h2>Sacas (60 kg)</h2>
                <h1 id="estoqueSacasTotal">0</h1>
            </div>
        </article>

        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">🌱</div>
            <div class="metric-copy">
                <h2>Cultivares</h2>
                <h1 id="cultivares">0</h1>
            </div>
        </article>

        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">📋</div>
            <div class="metric-copy">
                <h2>Lotes</h2>
                <h1 id="lotes">0</h1>
            </div>
        </article>

        <article class="metric-card">
            <div class="metric-icon" aria-hidden="true">🚜</div>
            <div class="metric-copy">
                <h2>Fazendas</h2>
                <h1 id="fazendas">0</h1>
            </div>
        </article>
    </section>

    <section class="assistant-card" aria-label="Assistente SeedControl">
        <div class="assistant-avatar" aria-hidden="true">🤖</div>
        <div class="assistant-content">
            <h2>Assistente SeedControl</h2>
            <p>Consulte estoque, lotes, cultivares, fazendas, Bags, Kg e Sacas por mensagem.</p>
            <button class="assistant-cta" type="button" onclick="window.location.href='assistente.html'">
                <span aria-hidden="true">💬</span>
                <span>Conversar com o Assistente</span>
                <span class="action-arrow" aria-hidden="true">›</span>
            </button>
        </div>
    </section>

    <section class="quick-section" aria-label="Ações rápidas">
        <h2 class="section-title">Ações rápidas</h2>

        <div class="quick-grid">
            <button class="quick-action" type="button" onclick="window.location.href='estoque.html'">
                <span class="quick-icon" aria-hidden="true">📦</span>
                <span>Estoque</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='cadastro.html'">
                <span class="quick-icon" aria-hidden="true">🌱</span>
                <span>Novo Lote</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='planilha.html'">
                <span class="quick-icon" aria-hidden="true">📑</span>
                <span>Planilha de Lotes</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='assistente.html'">
                <span class="quick-icon" aria-hidden="true">🤖</span>
                <span>Assistente SeedControl</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='qrcode.html'">
                <span class="quick-icon" aria-hidden="true">▦</span>
                <span>Ler QR Code</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='historico.html'">
                <span class="quick-icon" aria-hidden="true">📋</span>
                <span>Histórico</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='relatorios.html'">
                <span class="quick-icon" aria-hidden="true">📊</span>
                <span>Relatórios</span>
            </button>

            <button class="quick-action" type="button" onclick="window.location.href='configuracoes.html'">
                <span class="quick-icon" aria-hidden="true">⚙️</span>
                <span>Configurações</span>
            </button>
        </div>
    </section>

</main>

<script src="database.js"></script>
<script src="app.js"></script>
<script>
if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker.register("./service-worker.js").catch(function (erro) {
            console.error("Erro ao registrar Service Worker:", erro);
        });
    });
}
</script>
</body>
</html>
'''

dashboard_css = r'''/* SeedControl v3.8.4 - Dashboard aprovado */

.dashboard-body {
    min-height: 100vh;
    background:
        radial-gradient(circle at 90% 0%, rgba(34, 197, 94, .10), transparent 32%),
        linear-gradient(180deg, #06111a 0%, #071722 46%, #06141d 100%);
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
}

.dashboard-topo {
    position: relative;
    overflow: hidden;
    padding: 24px 22px 22px;
    background:
        radial-gradient(circle at 92% 18%, rgba(34, 197, 94, .17), transparent 28%),
        linear-gradient(110deg, #071814 0%, #063322 58%, #06251d 100%);
    border-bottom: 1px solid rgba(74, 222, 128, .24);
    box-shadow: 0 12px 28px rgba(0, 0, 0, .28);
}

.dashboard-topo::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: -1px;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(74, 222, 128, .82), transparent);
}

.dashboard-brand {
    width: 100%;
    max-width: 720px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 14px;
}

.dashboard-brand-icon {
    flex: 0 0 auto;
    width: 58px;
    height: 58px;
    display: grid;
    place-items: center;
    font-size: 42px;
    filter: drop-shadow(0 6px 10px rgba(0, 0, 0, .28));
}

.dashboard-brand-copy {
    min-width: 0;
}

.dashboard-brand-copy h1 {
    margin: 0;
    font-size: clamp(29px, 8vw, 38px);
    line-height: 1;
    letter-spacing: -.8px;
    font-weight: 800;
}

.dashboard-brand-copy h1 span {
    color: #f8fafc;
}

.dashboard-brand-copy h1 strong {
    color: #67d23f;
    font-weight: 800;
}

.dashboard-brand-copy p {
    margin: 8px 0 0;
    color: #b8c5ca;
    font-size: clamp(14px, 4vw, 18px);
    line-height: 1.25;
}

.dashboard-container {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    padding: 18px 16px calc(24px + env(safe-area-inset-bottom));
}

.dashboard-container #alertasEstoque,
.dashboard-container #alertasEstoque[hidden] {
    display: none !important;
}

.dashboard-container #dashboard.dashboard-metricas {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin: 0 0 16px;
}

.metric-card {
    min-width: 0;
    min-height: 116px;
    padding: 16px 14px;
    display: flex;
    align-items: center;
    gap: 13px;
    border-radius: 17px;
    border: 1px solid rgba(148, 163, 184, .25);
    background:
        linear-gradient(145deg, rgba(20, 38, 49, .96), rgba(11, 29, 40, .96));
    box-shadow:
        0 9px 22px rgba(0, 0, 0, .22),
        inset 0 1px 0 rgba(255, 255, 255, .025);
}

.metric-icon {
    flex: 0 0 52px;
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1px solid rgba(74, 222, 128, .44);
    background:
        radial-gradient(circle at 35% 28%, rgba(74, 222, 128, .20), rgba(16, 67, 43, .68));
    font-size: 27px;
    box-shadow: inset 0 0 16px rgba(34, 197, 94, .11);
}

.metric-copy {
    min-width: 0;
    flex: 1;
}

.dashboard-container #dashboard .metric-card h2 {
    width: auto;
    margin: 0 0 8px;
    color: #f8fafc;
    font-size: clamp(14px, 4vw, 17px);
    line-height: 1.15;
    font-weight: 700;
    text-align: left;
    overflow-wrap: normal;
}

.dashboard-container #dashboard .metric-card h1 {
    width: auto;
    margin: 0;
    color: #45d15e;
    font-size: clamp(24px, 7vw, 32px);
    line-height: 1.05;
    font-weight: 500;
    text-align: left;
    letter-spacing: -.4px;
    overflow-wrap: anywhere;
}

.assistant-card {
    position: relative;
    overflow: hidden;
    display: grid;
    grid-template-columns: 76px minmax(0, 1fr);
    gap: 14px;
    padding: 18px;
    margin: 0 0 18px;
    border-radius: 18px;
    border: 1px solid rgba(74, 222, 128, .40);
    background:
        radial-gradient(circle at 8% 100%, rgba(34, 197, 94, .13), transparent 35%),
        linear-gradient(135deg, rgba(15, 42, 43, .98), rgba(15, 29, 39, .98));
    box-shadow: 0 10px 26px rgba(0, 0, 0, .24);
}

.assistant-card::after {
    content: "💬";
    position: absolute;
    right: 20px;
    top: 14px;
    font-size: 54px;
    opacity: .06;
    transform: rotate(-8deg);
}

.assistant-avatar {
    width: 70px;
    height: 70px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1px solid rgba(74, 222, 128, .62);
    background: linear-gradient(145deg, rgba(38, 104, 64, .65), rgba(9, 46, 36, .84));
    font-size: 42px;
    box-shadow: inset 0 0 18px rgba(34, 197, 94, .13);
}

.assistant-content {
    min-width: 0;
}

.assistant-content h2 {
    position: relative;
    z-index: 1;
    margin: 1px 0 6px;
    color: #ffffff;
    font-size: 21px;
    line-height: 1.15;
}

.assistant-content p {
    position: relative;
    z-index: 1;
    margin: 0 0 13px;
    color: #c1cbd0;
    font-size: 14px;
    line-height: 1.45;
}

.dashboard-body button.assistant-cta {
    position: relative;
    z-index: 1;
    width: 100%;
    min-height: 48px;
    padding: 11px 14px;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    align-items: center;
    gap: 9px;
    border: 1px solid rgba(103, 232, 85, .74);
    border-radius: 13px;
    background: linear-gradient(100deg, #137e36, #20a848 58%, #1c8f3c);
    color: white;
    font-size: 15px;
    line-height: 1.2;
    font-weight: 750;
    box-shadow: 0 7px 18px rgba(18, 112, 49, .20);
}

.action-arrow {
    font-size: 29px;
    line-height: .8;
    font-weight: 400;
}

.quick-section {
    margin-top: 2px;
}

.section-title {
    margin: 0 0 11px 4px;
    color: #bac5ca;
    font-size: 16px;
    font-weight: 500;
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 9px;
}

.dashboard-body button.quick-action {
    min-width: 0;
    min-height: 114px;
    padding: 12px 6px 11px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 9px;
    border-radius: 15px;
    border: 1px solid rgba(148, 163, 184, .28);
    background: linear-gradient(145deg, rgba(20, 38, 49, .96), rgba(10, 28, 38, .96));
    color: #f8fafc;
    font-size: clamp(11px, 3.1vw, 14px);
    line-height: 1.18;
    font-weight: 650;
    text-align: center;
    overflow-wrap: anywhere;
    box-shadow: 0 8px 20px rgba(0, 0, 0, .19);
}

.dashboard-body button.quick-action:active {
    transform: translateY(1px) scale(.98);
    border-color: rgba(74, 222, 128, .62);
    background: linear-gradient(145deg, rgba(20, 58, 45, .98), rgba(11, 36, 37, .98));
}

.quick-icon {
    width: 47px;
    height: 47px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    border: 1px solid rgba(74, 222, 128, .28);
    background: linear-gradient(145deg, rgba(24, 97, 50, .58), rgba(13, 52, 38, .72));
    font-size: 28px;
    line-height: 1;
}

@media (max-width: 390px) {
    .dashboard-topo {
        padding: 20px 16px 18px;
    }

    .dashboard-brand-icon {
        width: 50px;
        height: 50px;
        font-size: 36px;
    }

    .dashboard-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .metric-card {
        min-height: 106px;
        padding: 13px 10px;
        gap: 9px;
    }

    .metric-icon {
        flex-basis: 43px;
        width: 43px;
        height: 43px;
        font-size: 23px;
    }

    .assistant-card {
        grid-template-columns: 58px minmax(0, 1fr);
        padding: 15px;
        gap: 11px;
    }

    .assistant-avatar {
        width: 56px;
        height: 56px;
        font-size: 34px;
    }

    .assistant-content h2 {
        font-size: 19px;
    }

    .quick-grid {
        gap: 7px;
    }

    .dashboard-body button.quick-action {
        min-height: 105px;
        padding-left: 4px;
        padding-right: 4px;
    }

    .quick-icon {
        width: 42px;
        height: 42px;
        font-size: 24px;
    }
}

@media (max-width: 345px) {
    .quick-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .dashboard-body button.quick-action {
        min-height: 98px;
        font-size: 14px;
    }
}
'''

INDEX.write_text(index_html, encoding="utf-8")
CSS.write_text(dashboard_css, encoding="utf-8")

if SW.exists():
    sw = SW.read_text(encoding="utf-8")
    sw = sw.replace('"seedcontrol-v3.8-pwa-11"', '"seedcontrol-v3.8-pwa-12"')
    if '"./dashboard-v384.css"' not in sw:
        sw = sw.replace('"./style.css",', '"./style.css",\n\n    "./dashboard-v384.css",', 1)
    SW.write_text(sw, encoding="utf-8")

print("Dashboard v3.8.4 aplicado sem alterar as demais telas.")
