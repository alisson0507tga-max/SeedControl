from pathlib import Path

ROOT = Path('native/www')
HTML = ROOT / 'assistente.html'
JS = ROOT / 'assistente-v384.js'
CSS = ROOT / 'assistente-v384.css'

# A tela pode ou não existir na base antiga. Nesta versão ela passa a ser
# criada integralmente pelo patch para termos comportamento previsível no APK.
html = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#071713">
    <title>Assistente SeedControl</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="app-v384.css">
    <link rel="stylesheet" href="assistente-v384.css">
</head>
<body class="seed-v384-page seed-v384-assistente assistente-v384-body">

<header class="assistente-v384-topo">
    <button class="assistente-v384-voltar" type="button" id="btnVoltarAssistente" aria-label="Voltar">←</button>
    <div class="assistente-v384-identidade">
        <div class="assistente-v384-avatar" aria-hidden="true">🌱</div>
        <div>
            <h1>Assistente SeedControl</h1>
            <p>Converse por texto ou voz</p>
        </div>
    </div>
    <button class="assistente-v384-limpar" type="button" id="btnLimparConversa" aria-label="Limpar conversa">⌫</button>
</header>

<main class="assistente-v384-main">
    <section class="assistente-v384-status" aria-live="polite">
        <span class="assistente-v384-status-dot"></span>
        <span id="assistenteStatus">Pronto para conversar</span>
    </section>

    <section id="assistenteMensagens" class="assistente-v384-mensagens" aria-live="polite" aria-label="Conversa com o Assistente SeedControl"></section>

    <section id="assistenteSugestoes" class="assistente-v384-sugestoes" aria-label="Sugestões">
        <button type="button" data-pergunta="Quantas bags eu tenho no total?">📦 Estoque total</button>
        <button type="button" data-pergunta="Onde está o lote 105?">📍 Localizar lote</button>
        <button type="button" data-pergunta="Quais lotes têm umidade acima de 12%?">💧 Umidade</button>
        <button type="button" data-pergunta="O que você consegue fazer?">✨ Ajuda</button>
    </section>
</main>

<footer class="assistente-v384-composer">
    <div class="assistente-v384-input-wrap">
        <textarea id="assistenteEntrada" rows="1" maxlength="700" placeholder="Fale ou escreva para o SeedControl..." aria-label="Mensagem"></textarea>
        <button type="button" id="btnMicrofoneAssistente" class="assistente-v384-mic" aria-label="Falar com o Assistente">🎤</button>
        <button type="button" id="btnEnviarAssistente" class="assistente-v384-enviar" aria-label="Enviar mensagem">➤</button>
    </div>
    <small>Alterações no estoque sempre pedem confirmação.</small>
</footer>

<script src="database.js"></script>
<script src="assistente-v384.js"></script>
</body>
</html>
'''

css = r'''/* seedcontrol-assistente-conversa-v384 */

.assistente-v384-body {
    min-height: 100vh;
    min-height: 100dvh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background:
        radial-gradient(circle at 100% 0%, rgba(34, 197, 94, .09), transparent 28%),
        linear-gradient(180deg, #06111a 0%, #071722 48%, #06141d 100%) !important;
}

.assistente-v384-topo {
    flex: 0 0 auto;
    width: 100%;
    min-height: 78px;
    padding: calc(12px + env(safe-area-inset-top)) 14px 12px !important;
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr) 44px;
    align-items: center;
    gap: 10px;
    background:
        radial-gradient(circle at 88% 12%, rgba(34, 197, 94, .19), transparent 31%),
        linear-gradient(110deg, #071814 0%, #063322 58%, #06251d 100%) !important;
    border-bottom: 1px solid rgba(74, 222, 128, .22) !important;
    box-shadow: 0 8px 26px rgba(0, 0, 0, .26) !important;
    z-index: 4;
}

.assistente-v384-identidade {
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.assistente-v384-avatar {
    width: 42px;
    height: 42px;
    flex: 0 0 42px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    border: 1px solid rgba(74, 222, 128, .32);
    background: rgba(19, 95, 53, .46);
    font-size: 23px;
}

.assistente-v384-identidade h1 {
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #fff !important;
    font-size: 18px !important;
    line-height: 1.15;
}

.assistente-v384-identidade p {
    margin: 3px 0 0 !important;
    color: #aebdc2 !important;
    font-size: 12px;
}

.assistente-v384-voltar,
.assistente-v384-limpar {
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: grid !important;
    place-items: center;
    border: 1px solid rgba(148, 163, 184, .20) !important;
    border-radius: 13px !important;
    background: rgba(5, 25, 31, .58) !important;
    color: #edf7f0 !important;
    font-size: 22px;
    box-shadow: none !important;
}

.assistente-v384-main {
    flex: 1 1 auto;
    min-height: 0;
    width: 100% !important;
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 10px 12px 8px !important;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.assistente-v384-status {
    flex: 0 0 auto;
    align-self: center;
    max-width: 94%;
    margin-bottom: 8px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    gap: 7px;
    border: 1px solid rgba(148, 163, 184, .15);
    border-radius: 999px;
    background: rgba(7, 28, 35, .64);
    color: #aebdc2;
    font-size: 11px;
}

.assistente-v384-status-dot {
    width: 7px;
    height: 7px;
    flex: 0 0 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 10px rgba(74, 222, 128, .55);
}

.assistente-v384-status.ouvindo .assistente-v384-status-dot {
    animation: seed-pulso-mic 1s infinite;
}

@keyframes seed-pulso-mic {
    0%, 100% { transform: scale(1); opacity: .75; }
    50% { transform: scale(1.55); opacity: 1; }
}

.assistente-v384-mensagens {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    padding: 4px 2px 12px;
    scrollbar-width: thin;
}

.assistente-v384-msg {
    width: fit-content;
    max-width: 88%;
    margin: 8px 0;
    padding: 11px 13px;
    border-radius: 16px;
    line-height: 1.46;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    font-size: 14px;
    box-shadow: 0 5px 16px rgba(0, 0, 0, .14);
}

.assistente-v384-msg.assistente {
    margin-right: auto;
    border: 1px solid rgba(148, 163, 184, .17);
    border-bottom-left-radius: 5px;
    background: linear-gradient(145deg, rgba(22, 42, 52, .98), rgba(11, 30, 39, .98));
    color: #e7eef0;
}

.assistente-v384-msg.usuario {
    margin-left: auto;
    border: 1px solid rgba(74, 222, 128, .26);
    border-bottom-right-radius: 5px;
    background: linear-gradient(145deg, rgba(19, 108, 57, .86), rgba(12, 78, 46, .94));
    color: #f4fff7;
}

.assistente-v384-msg .hora {
    display: block;
    margin-top: 5px;
    opacity: .56;
    font-size: 9px;
    text-align: right;
}

.assistente-v384-msg .confirmacao-acoes {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 7px;
    margin-top: 10px;
}

.assistente-v384-msg .confirmacao-acoes button {
    min-height: 42px !important;
    margin: 0 !important;
    padding: 8px !important;
    border-radius: 11px !important;
    font-size: 12px;
}

.assistente-v384-msg .confirmacao-acoes .cancelar {
    border-color: rgba(148, 163, 184, .24) !important;
    background: rgba(44, 58, 65, .78) !important;
}

.assistente-v384-sugestoes {
    flex: 0 0 auto;
    width: 100%;
    padding: 4px 0 3px;
    display: flex;
    gap: 7px;
    overflow-x: auto;
    scrollbar-width: none;
}

.assistente-v384-sugestoes::-webkit-scrollbar { display: none; }

.assistente-v384-sugestoes button {
    flex: 0 0 auto;
    min-height: 38px !important;
    margin: 0 !important;
    padding: 7px 11px !important;
    border: 1px solid rgba(74, 222, 128, .20) !important;
    border-radius: 999px !important;
    background: rgba(12, 54, 39, .62) !important;
    color: #cdebd5 !important;
    font-size: 11px;
    font-weight: 650;
    box-shadow: none !important;
    white-space: nowrap;
}

.assistente-v384-composer {
    flex: 0 0 auto;
    width: 100%;
    padding: 9px 12px calc(9px + env(safe-area-inset-bottom));
    background: rgba(5, 20, 28, .96);
    border-top: 1px solid rgba(148, 163, 184, .14);
    box-shadow: 0 -8px 24px rgba(0, 0, 0, .16);
}

.assistente-v384-input-wrap {
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    padding: 6px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 44px 44px;
    align-items: end;
    gap: 5px;
    border: 1px solid rgba(148, 163, 184, .23);
    border-radius: 18px;
    background: rgba(10, 30, 39, .96);
}

.assistente-v384-input-wrap textarea {
    width: 100%;
    max-height: 116px;
    min-height: 42px !important;
    margin: 0 !important;
    padding: 10px 9px !important;
    resize: none;
    border: 0 !important;
    border-radius: 12px !important;
    outline: none;
    background: transparent !important;
    color: #f8fafc !important;
    font: inherit;
    font-size: 14px;
    line-height: 1.4;
    box-shadow: none !important;
}

.assistente-v384-input-wrap textarea:focus {
    box-shadow: none !important;
}

.assistente-v384-mic,
.assistente-v384-enviar {
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: grid !important;
    place-items: center;
    border-radius: 13px !important;
    box-shadow: none !important;
    font-size: 18px;
}

.assistente-v384-mic {
    border-color: rgba(148, 163, 184, .18) !important;
    background: rgba(31, 50, 59, .82) !important;
}

.assistente-v384-mic.ouvindo {
    border-color: rgba(248, 113, 113, .55) !important;
    background: #a33131 !important;
    animation: seed-pulso-mic 1s infinite;
}

.assistente-v384-enviar {
    border-color: rgba(74, 222, 128, .40) !important;
    background: linear-gradient(145deg, #17863a, #20aa49) !important;
}

.assistente-v384-composer > small {
    display: block;
    max-width: 760px;
    margin: 5px auto 0;
    color: #73858e;
    text-align: center;
    font-size: 9px;
}

@media (min-width: 700px) {
    .assistente-v384-msg { max-width: 72%; }
}
'''

js = r'''// seedcontrol-assistente-conversa-v384
(function () {
    "use strict";

    const CHAVE_CONVERSA = "seedcontrol_assistente_conversa_v384";
    const LIMITE_MENSAGENS = 60;

    let mensagens = [];
    let movimentoPendente = null;
    let ouvindo = false;

    const $ = (id) => document.getElementById(id);

    function normalizar(valor) {
        return String(valor == null ? "" : valor)
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    function numero(valor) {
        const n = Number(String(valor == null ? "" : valor).replace(",", "."));
        return Number.isFinite(n) ? n : 0;
    }

    function estoqueAtual() {
        try {
            if (typeof carregarEstoque === "function") return carregarEstoque();
            const bruto = JSON.parse(localStorage.getItem("estoque") || "[]");
            return Array.isArray(bruto) ? bruto : [];
        } catch (_) {
            return [];
        }
    }

    function salvarBase(estoque) {
        if (typeof salvarEstoque === "function") {
            salvarEstoque(estoque);
            return;
        }
        localStorage.setItem("estoque", JSON.stringify(estoque));
    }

    function salvarHistoricoMovimento(item, tipo, qtd, antes, depois) {
        try {
            const historico = typeof carregarHistorico === "function"
                ? carregarHistorico()
                : JSON.parse(localStorage.getItem("historico") || "[]");

            const lista = Array.isArray(historico) ? historico : [];
            lista.unshift({
                id: Date.now(),
                data: new Date().toLocaleString("pt-BR"),
                tipo,
                quantidade: qtd,
                cultivar: item.cultivar || "",
                lote: item.lote || "",
                fazenda: item.fazenda || "",
                talhao: item.talhao || "",
                peneira: item.peneira || "",
                bagsAntes: antes,
                bagsDepois: depois,
                origem: "Assistente SeedControl"
            });

            if (typeof salvarHistorico === "function") salvarHistorico(lista);
            else localStorage.setItem("historico", JSON.stringify(lista));
        } catch (_) {}
    }

    function horario() {
        return new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    }

    function salvarConversa() {
        try {
            localStorage.setItem(CHAVE_CONVERSA, JSON.stringify(mensagens.slice(-LIMITE_MENSAGENS)));
        } catch (_) {}
    }

    function escapar(texto) {
        return String(texto)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function rolarFim() {
        const caixa = $("assistenteMensagens");
        if (!caixa) return;
        requestAnimationFrame(() => {
            caixa.scrollTop = caixa.scrollHeight;
        });
    }

    function criarBolha(tipo, texto, opcoes) {
        const caixa = $("assistenteMensagens");
        if (!caixa) return;

        const div = document.createElement("div");
        div.className = "assistente-v384-msg " + (tipo === "usuario" ? "usuario" : "assistente");
        div.innerHTML = `<div>${escapar(texto).replace(/\n/g, "<br>")}</div><span class="hora">${horario()}</span>`;

        if (opcoes && opcoes.confirmacao) {
            const acoes = document.createElement("div");
            acoes.className = "confirmacao-acoes";
            acoes.innerHTML = `
                <button type="button" data-confirmar-movimento="1">✓ Confirmar</button>
                <button type="button" class="cancelar" data-cancelar-movimento="1">Cancelar</button>
            `;
            div.appendChild(acoes);
        }

        caixa.appendChild(div);
        rolarFim();
    }

    function adicionar(tipo, texto, opcoes) {
        const msg = { tipo, texto: String(texto), data: Date.now() };
        mensagens.push(msg);
        mensagens = mensagens.slice(-LIMITE_MENSAGENS);
        salvarConversa();
        criarBolha(tipo, texto, opcoes);
    }

    function restaurarConversa() {
        try {
            const lidas = JSON.parse(localStorage.getItem(CHAVE_CONVERSA) || "[]");
            mensagens = Array.isArray(lidas) ? lidas.slice(-LIMITE_MENSAGENS) : [];
        } catch (_) {
            mensagens = [];
        }

        const caixa = $("assistenteMensagens");
        if (caixa) caixa.innerHTML = "";

        mensagens.forEach((m) => criarBolha(m.tipo, m.texto));

        if (!mensagens.length) {
            adicionar(
                "assistente",
                "Olá! Eu sou o Assistente SeedControl. Você pode falar ou escrever comigo.\n\nExemplos:\n• Quantas bags da Guepardo eu tenho?\n• Onde está o lote 105?\n• Quais lotes têm umidade acima de 12%?\n• Saiu 10 bags do lote 25."
            );
        }
    }

    function setStatus(texto, estaOuvindo) {
        const status = $("assistenteStatus");
        const bloco = status && status.parentElement;
        if (status) status.textContent = texto;
        if (bloco) bloco.classList.toggle("ouvindo", !!estaOuvindo);
    }

    function formatarNumero(n, casas) {
        return Number(n || 0).toLocaleString("pt-BR", {
            minimumFractionDigits: casas || 0,
            maximumFractionDigits: casas == null ? 2 : casas
        });
    }

    function cultivarMencionada(frase, estoque) {
        const n = normalizar(frase);
        const nomes = [...new Set(estoque.map((x) => String(x.cultivar || "").trim()).filter(Boolean))];
        return nomes
            .sort((a, b) => b.length - a.length)
            .find((nome) => n.includes(normalizar(nome))) || "";
    }

    function fazendaMencionada(frase, estoque) {
        const n = normalizar(frase);
        const nomes = [...new Set(estoque.map((x) => String(x.fazenda || "").trim()).filter(Boolean))];
        return nomes
            .sort((a, b) => b.length - a.length)
            .find((nome) => n.includes(normalizar(nome))) || "";
    }

    function extrairLote(frase) {
        const m = normalizar(frase).match(/\blote\s*(?:n[ºo°.]?\s*)?(\d+)\b/);
        return m ? Number(m[1]) : null;
    }

    function descreverLote(item) {
        const partes = [
            `Lote ${item.lote}`,
            item.cultivar ? `cultivar ${item.cultivar}` : "",
            `${formatarNumero(item.bags, 0)} bags`,
            item.fazenda ? `fazenda ${item.fazenda}` : "",
            item.talhao ? `talhão ${item.talhao}` : "",
            item.peneira ? `peneira ${item.peneira}` : ""
        ].filter(Boolean);
        return partes.join(" • ");
    }

    function ajuda() {
        return "Hoje eu consigo consultar o estoque e entender vários pedidos em português.\n\nVocê pode perguntar por cultivar, lote, fazenda e umidade. Também pode dizer algo como ‘saiu 10 bags do lote 25’ ou ‘entrou 5 bags no lote 25’. Antes de alterar o estoque eu sempre mostro o que vou fazer e peço confirmação.";
    }

    function interpretarConsulta(frase) {
        const estoque = estoqueAtual();
        const n = normalizar(frase);

        if (!estoque.length && !/(ajuda|consegue|pode fazer|ola|oi|bom dia|boa tarde|boa noite)/.test(n)) {
            return "Ainda não encontrei lotes cadastrados no estoque deste aparelho.";
        }

        if (/^(oi|ola|opa|bom dia|boa tarde|boa noite)\b/.test(n)) {
            return "Olá! Pode falar comigo normalmente. Se quiser, pergunte sobre um lote, cultivar, fazenda ou quantidade de bags.";
        }

        if (/(o que.*consegue|o que.*faz|ajuda|comandos|como usar)/.test(n)) {
            return ajuda();
        }

        const loteNumero = extrairLote(frase);
        if (loteNumero != null && /(onde|local|esta|dados|inform|quant|bags|lote)/.test(n)) {
            const encontrados = estoque.filter((x) => Number(x.lote) === loteNumero);
            if (!encontrados.length) return `Não encontrei o lote ${loteNumero}.`;
            if (encontrados.length === 1) return descreverLote(encontrados[0]) + ".";
            return `Encontrei ${encontrados.length} registros com o lote ${loteNumero}:\n` + encontrados.map((x) => "• " + descreverLote(x)).join("\n");
        }

        const cultivar = cultivarMencionada(frase, estoque);
        if (cultivar && /(quant|bags|estoque|tenho|total)/.test(n)) {
            const itens = estoque.filter((x) => normalizar(x.cultivar) === normalizar(cultivar));
            const bags = itens.reduce((s, x) => s + numero(x.bags), 0);
            return `${cultivar}: ${formatarNumero(bags, 0)} bags em ${itens.length} lote${itens.length === 1 ? "" : "s"}.`;
        }

        const fazenda = fazendaMencionada(frase, estoque);
        if (fazenda && /(quant|bags|estoque|tenho|total|fazenda)/.test(n)) {
            const itens = estoque.filter((x) => normalizar(x.fazenda) === normalizar(fazenda));
            const bags = itens.reduce((s, x) => s + numero(x.bags), 0);
            return `Na fazenda ${fazenda} há ${formatarNumero(bags, 0)} bags em ${itens.length} lote${itens.length === 1 ? "" : "s"}.`;
        }

        const umidade = n.match(/umidade.*?(?:acima de|maior que|>|mais de)\s*(\d+(?:[.,]\d+)?)/);
        if (umidade) {
            const limite = numero(umidade[1]);
            const itens = estoque.filter((x) => numero(x.umidade) > limite);
            if (!itens.length) return `Não encontrei lotes com umidade acima de ${formatarNumero(limite, 1)}%.`;
            return `${itens.length} lote${itens.length === 1 ? "" : "s"} com umidade acima de ${formatarNumero(limite, 1)}%:\n` +
                itens.slice(0, 20).map((x) => `• Lote ${x.lote} • ${x.cultivar || "Sem cultivar"} • ${formatarNumero(x.umidade, 1)}%`).join("\n") +
                (itens.length > 20 ? `\n… e mais ${itens.length - 20}.` : "");
        }

        if (/(quant.*bags|bags.*total|estoque total|quanto.*estoque|quanto.*tenho)/.test(n)) {
            const bags = estoque.reduce((s, x) => s + numero(x.bags), 0);
            const cultivares = new Set(estoque.map((x) => normalizar(x.cultivar)).filter(Boolean)).size;
            return `O estoque tem ${formatarNumero(bags, 0)} bags, distribuídas em ${estoque.length} lotes e ${cultivares} cultivares.`;
        }

        if (/(quant.*lote|total.*lote)/.test(n)) {
            return `Há ${estoque.length} lotes cadastrados no estoque.`;
        }

        return "Ainda não entendi esse pedido com segurança. Tente citar o lote, a cultivar ou a fazenda. Exemplo: “Quantas bags da Guepardo eu tenho?”";
    }

    function detectarMovimento(frase) {
        const n = normalizar(frase);
        let tipo = null;

        if (/\b(saiu|saida|retirou|retirar|baixar|baixa|descontar)\b/.test(n)) tipo = "saida";
        if (/\b(entrou|entrada|recebeu|receber|adicionar|acrescentar)\b/.test(n)) tipo = "entrada";
        if (!tipo) return null;

        const lote = extrairLote(frase);
        const qtdMatch = n.match(/(?:saiu|saida|retirou|retirar|baixar|baixa|descontar|entrou|entrada|recebeu|receber|adicionar|acrescentar)\D{0,20}(\d+(?:[.,]\d+)?)\s*(?:bags?|bag)?/)
            || n.match(/(\d+(?:[.,]\d+)?)\s*bags?/);
        const qtd = qtdMatch ? numero(qtdMatch[1]) : 0;

        if (!lote || qtd <= 0) return { erro: "Para movimentar, preciso da quantidade de bags e do número do lote. Exemplo: “Saiu 10 bags do lote 25”." };

        const estoque = estoqueAtual();
        let candidatos = estoque.filter((x) => Number(x.lote) === lote);
        const cultivar = cultivarMencionada(frase, candidatos.length ? candidatos : estoque);
        const fazenda = fazendaMencionada(frase, candidatos.length ? candidatos : estoque);

        if (cultivar) candidatos = candidatos.filter((x) => normalizar(x.cultivar) === normalizar(cultivar));
        if (fazenda) candidatos = candidatos.filter((x) => normalizar(x.fazenda) === normalizar(fazenda));

        if (!candidatos.length) return { erro: `Não encontrei o lote ${lote} com essas informações.` };
        if (candidatos.length > 1) {
            return {
                erro: `Encontrei mais de um registro para o lote ${lote}. Diga também a cultivar ou a fazenda para eu saber qual movimentar.\n` +
                    candidatos.map((x) => "• " + descreverLote(x)).join("\n")
            };
        }

        const item = candidatos[0];
        const atual = numero(item.bags);
        const depois = tipo === "saida" ? atual - qtd : atual + qtd;
        if (tipo === "saida" && depois < 0) {
            return { erro: `Esse lote tem ${formatarNumero(atual, 0)} bags. Não posso retirar ${formatarNumero(qtd, 0)} porque o estoque ficaria negativo.` };
        }

        return { tipo, qtd, item, atual, depois };
    }

    function pedirConfirmacao(mov) {
        movimentoPendente = {
            tipo: mov.tipo,
            qtd: mov.qtd,
            lote: Number(mov.item.lote),
            id: mov.item.id == null ? null : mov.item.id,
            cultivar: mov.item.cultivar || "",
            fazenda: mov.item.fazenda || "",
            atual: mov.atual,
            depois: mov.depois
        };

        const verbo = mov.tipo === "saida" ? "RETIRAR" : "ADICIONAR";
        const texto = `${verbo} ${formatarNumero(mov.qtd, 0)} bags do lote ${mov.item.lote} (${mov.item.cultivar || "sem cultivar"})?\nEstoque: ${formatarNumero(mov.atual, 0)} → ${formatarNumero(mov.depois, 0)} bags.`;
        adicionar("assistente", texto, { confirmacao: true });
    }

    function confirmarMovimento() {
        if (!movimentoPendente) {
            adicionar("assistente", "Não há nenhuma movimentação aguardando confirmação.");
            return;
        }

        const pend = movimentoPendente;
        const estoque = estoqueAtual();
        let indice = -1;

        if (pend.id != null) indice = estoque.findIndex((x) => String(x.id) === String(pend.id));
        if (indice < 0) {
            indice = estoque.findIndex((x) =>
                Number(x.lote) === pend.lote &&
                normalizar(x.cultivar) === normalizar(pend.cultivar) &&
                normalizar(x.fazenda) === normalizar(pend.fazenda)
            );
        }

        if (indice < 0) {
            movimentoPendente = null;
            adicionar("assistente", "O lote mudou ou não existe mais. Não fiz nenhuma alteração.");
            return;
        }

        const item = estoque[indice];
        const antes = numero(item.bags);
        const depois = pend.tipo === "saida" ? antes - pend.qtd : antes + pend.qtd;

        if (pend.tipo === "saida" && depois < 0) {
            movimentoPendente = null;
            adicionar("assistente", "O estoque desse lote mudou e agora a saída deixaria o valor negativo. Não fiz a alteração.");
            return;
        }

        item.bags = depois;
        salvarBase(estoque);
        salvarHistoricoMovimento(item, pend.tipo, pend.qtd, antes, depois);
        movimentoPendente = null;

        adicionar(
            "assistente",
            `Pronto. ${pend.tipo === "saida" ? "Saída" : "Entrada"} registrada: ${formatarNumero(pend.qtd, 0)} bags no lote ${item.lote}. Saldo atual: ${formatarNumero(depois, 0)} bags.`
        );
    }

    function cancelarMovimento() {
        if (!movimentoPendente) return;
        movimentoPendente = null;
        adicionar("assistente", "Movimentação cancelada. Nenhum dado foi alterado.");
    }

    async function processar(texto) {
        const frase = String(texto || "").trim();
        if (!frase) return;

        adicionar("usuario", frase);
        setStatus("Consultando dados do SeedControl…", false);

        await new Promise((r) => setTimeout(r, 90));

        const n = normalizar(frase);
        if (movimentoPendente && /^(confirmar|confirma|sim|pode|pode fazer|ok|certo)$/i.test(n)) {
            confirmarMovimento();
            setStatus("Pronto para conversar", false);
            return;
        }
        if (movimentoPendente && /^(cancelar|cancela|nao|não|deixa|parar)$/i.test(n)) {
            cancelarMovimento();
            setStatus("Pronto para conversar", false);
            return;
        }

        const mov = detectarMovimento(frase);
        if (mov) {
            if (mov.erro) adicionar("assistente", mov.erro);
            else pedirConfirmacao(mov);
        } else {
            adicionar("assistente", interpretarConsulta(frase));
        }

        setStatus("Pronto para conversar", false);
    }

    function autoAltura() {
        const entrada = $("assistenteEntrada");
        if (!entrada) return;
        entrada.style.height = "auto";
        entrada.style.height = Math.min(116, entrada.scrollHeight) + "px";
    }

    async function enviarEntrada() {
        const entrada = $("assistenteEntrada");
        if (!entrada) return;
        const texto = entrada.value.trim();
        if (!texto) return;
        entrada.value = "";
        autoAltura();
        await processar(texto);
    }

    function pluginVoz() {
        return window.Capacitor && window.Capacitor.Plugins
            ? window.Capacitor.Plugins.SpeechRecognition
            : null;
    }

    async function ouvirComPlugin() {
        const speech = pluginVoz();
        if (!speech) return false;

        try {
            const permissao = await speech.requestPermissions();
            if (permissao && permissao.speechRecognition === "denied") {
                throw new Error("Permissão do microfone negada.");
            }

            const disp = await speech.available();
            if (!disp || disp.available !== true) {
                throw new Error("Reconhecimento de voz não disponível neste aparelho.");
            }

            setStatus("Ouvindo… fale normalmente", true);
            ouvindo = true;
            $("btnMicrofoneAssistente")?.classList.add("ouvindo");

            const resultado = await speech.start({
                language: "pt-BR",
                maxResults: 3,
                partialResults: false,
                popup: false
            });

            const texto = resultado && Array.isArray(resultado.matches)
                ? String(resultado.matches[0] || "").trim()
                : "";

            if (texto) {
                const entrada = $("assistenteEntrada");
                if (entrada) {
                    entrada.value = texto;
                    autoAltura();
                }
                await enviarEntrada();
            } else {
                setStatus("Não consegui entender. Toque no microfone e tente novamente.", false);
            }
            return true;
        } catch (erro) {
            console.warn("SpeechRecognition:", erro);
            setStatus(erro && erro.message ? erro.message : "Não foi possível usar o microfone.", false);
            return true;
        } finally {
            ouvindo = false;
            $("btnMicrofoneAssistente")?.classList.remove("ouvindo");
        }
    }

    async function ouvirComWebSpeech() {
        const Classe = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!Classe) return false;

        return new Promise((resolve) => {
            const rec = new Classe();
            rec.lang = "pt-BR";
            rec.interimResults = false;
            rec.maxAlternatives = 3;

            ouvindo = true;
            $("btnMicrofoneAssistente")?.classList.add("ouvindo");
            setStatus("Ouvindo… fale normalmente", true);

            rec.onresult = async (evento) => {
                const texto = evento.results && evento.results[0] && evento.results[0][0]
                    ? String(evento.results[0][0].transcript || "").trim()
                    : "";
                if (texto) {
                    const entrada = $("assistenteEntrada");
                    if (entrada) entrada.value = texto;
                    await enviarEntrada();
                }
            };

            rec.onerror = () => setStatus("Não foi possível reconhecer a fala.", false);
            rec.onend = () => {
                ouvindo = false;
                $("btnMicrofoneAssistente")?.classList.remove("ouvindo");
                resolve(true);
            };
            rec.start();
        });
    }

    async function iniciarVoz() {
        if (ouvindo) return;
        const nativo = await ouvirComPlugin();
        if (nativo) return;
        const web = await ouvirComWebSpeech();
        if (web) return;
        setStatus("Reconhecimento de voz indisponível nesta versão do aparelho.", false);
    }

    function instalarEventos() {
        $("btnVoltarAssistente")?.addEventListener("click", () => {
            window.location.href = "index.html";
        });

        $("btnLimparConversa")?.addEventListener("click", () => {
            if (!confirm("Limpar a conversa do Assistente?")) return;
            mensagens = [];
            movimentoPendente = null;
            localStorage.removeItem(CHAVE_CONVERSA);
            restaurarConversa();
        });

        $("btnEnviarAssistente")?.addEventListener("click", enviarEntrada);
        $("btnMicrofoneAssistente")?.addEventListener("click", iniciarVoz);

        const entrada = $("assistenteEntrada");
        entrada?.addEventListener("input", autoAltura);
        entrada?.addEventListener("keydown", (evento) => {
            if (evento.key === "Enter" && !evento.shiftKey) {
                evento.preventDefault();
                enviarEntrada();
            }
        });

        $("assistenteSugestoes")?.addEventListener("click", (evento) => {
            const botao = evento.target.closest("[data-pergunta]");
            if (botao) processar(botao.dataset.pergunta || "");
        });

        $("assistenteMensagens")?.addEventListener("click", (evento) => {
            if (evento.target.closest("[data-confirmar-movimento]")) confirmarMovimento();
            if (evento.target.closest("[data-cancelar-movimento]")) cancelarMovimento();
        });
    }

    function iniciar() {
        instalarEventos();
        restaurarConversa();
        autoAltura();
        setStatus("Pronto para conversar", false);
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
    else iniciar();
})();
'''

HTML.write_text(html, encoding='utf-8')
CSS.write_text(css, encoding='utf-8')
JS.write_text(js, encoding='utf-8')

for trecho, conteudo, nome in [
    ('assistente-v384.css', html, 'assistente.html'),
    ('assistente-v384.js', html, 'assistente.html'),
    ('btnMicrofoneAssistente', html, 'assistente.html'),
    ('seedcontrol-assistente-conversa-v384', js, 'assistente-v384.js'),
    ('SpeechRecognition', js, 'assistente-v384.js'),
    ('confirmarMovimento', js, 'assistente-v384.js'),
    ('salvarBase', js, 'assistente-v384.js'),
    ('seedcontrol-assistente-conversa-v384', css, 'assistente-v384.css'),
]:
    if trecho not in conteudo:
        raise SystemExit(f'Validação falhou em {nome}: {trecho}')

print('Assistente SeedControl v3.8.4 criado com conversa, voz, consultas locais e confirmação de movimentações.')
