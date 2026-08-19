from pathlib import Path

JS = Path('native/www/assistente-v384.js')
if not JS.exists():
    raise SystemExit('assistente-v384.js não encontrado.')

texto = JS.read_text(encoding='utf-8')
if 'seedcontrol-assistente-intencao-v384' not in texto:
    raise SystemExit('A correção de intenção precisa ser aplicada antes do entendimento amplo.')

inicio = texto.find('    function interpretarConsulta(frase) {')
fim = texto.find('    function detectarMovimento(frase) {', inicio)
if inicio < 0 or fim < 0:
    raise SystemExit('Não foi possível localizar interpretarConsulta/detectarMovimento.')

bloco_consulta = r'''    // seedcontrol-assistente-entendimento-amplo-v384
    function distanciaEdicao(a, b) {
        a = normalizar(a);
        b = normalizar(b);
        if (a === b) return 0;
        if (!a.length) return b.length;
        if (!b.length) return a.length;

        const anterior = Array.from({ length: b.length + 1 }, (_, i) => i);
        const atual = new Array(b.length + 1);

        for (let i = 1; i <= a.length; i++) {
            atual[0] = i;
            for (let j = 1; j <= b.length; j++) {
                const custo = a[i - 1] === b[j - 1] ? 0 : 1;
                atual[j] = Math.min(
                    atual[j - 1] + 1,
                    anterior[j] + 1,
                    anterior[j - 1] + custo
                );
            }
            for (let j = 0; j <= b.length; j++) anterior[j] = atual[j];
        }
        return anterior[b.length];
    }

    function palavras(frase) {
        return normalizar(frase)
            .replace(/[^a-z0-9\s]/g, ' ')
            .split(/\s+/)
            .filter(Boolean);
    }

    function entidadeMencionadaAmpla(frase, estoque, campo) {
        const n = normalizar(frase);
        const tokens = palavras(frase);
        const nomes = [...new Set(
            estoque.map((x) => String(x && x[campo] || '').trim()).filter(Boolean)
        )].sort((a, b) => b.length - a.length);

        const direta = nomes.find((nome) => n.includes(normalizar(nome)));
        if (direta) return direta;

        let melhor = '';
        let melhorDist = 99;

        for (const nome of nomes) {
            const alvo = normalizar(nome);
            if (alvo.length < 5 || alvo.includes(' ')) continue;

            for (const token of tokens) {
                if (token.length < 4) continue;
                const dist = distanciaEdicao(token, alvo);
                const limite = alvo.length >= 9 ? 2 : 1;
                if (dist <= limite && dist < melhorDist) {
                    melhor = nome;
                    melhorDist = dist;
                }
            }
        }

        return melhor;
    }

    function cultivarMencionadaAmpla(frase, estoque) {
        return entidadeMencionadaAmpla(frase, estoque, 'cultivar');
    }

    function fazendaMencionadaAmpla(frase, estoque) {
        return entidadeMencionadaAmpla(frase, estoque, 'fazenda');
    }

    function numeroPorExtensoPt(trecho) {
        const t = palavras(trecho);
        if (!t.length) return null;

        const unidades = {
            zero: 0, um: 1, uma: 1, dois: 2, duas: 2, tres: 3, quatro: 4,
            cinco: 5, seis: 6, sete: 7, oito: 8, nove: 9, dez: 10,
            onze: 11, doze: 12, treze: 13, quatorze: 14, catorze: 14,
            quinze: 15, dezesseis: 16, dezassete: 17, dezessete: 17,
            dezoito: 18, dezenove: 19
        };
        const dezenas = {
            vinte: 20, trinta: 30, quarenta: 40, cinquenta: 50,
            sessenta: 60, setenta: 70, oitenta: 80, noventa: 90
        };
        const centenas = {
            cem: 100, cento: 100, duzentos: 200, trezentos: 300,
            quatrocentos: 400, quinhentos: 500, seiscentos: 600,
            setecentos: 700, oitocentos: 800, novecentos: 900
        };

        let total = 0;
        let encontrou = false;
        for (const token of t) {
            if (token === 'e') continue;
            if (Object.prototype.hasOwnProperty.call(unidades, token)) {
                total += unidades[token];
                encontrou = true;
                continue;
            }
            if (Object.prototype.hasOwnProperty.call(dezenas, token)) {
                total += dezenas[token];
                encontrou = true;
                continue;
            }
            if (Object.prototype.hasOwnProperty.call(centenas, token)) {
                total += centenas[token];
                encontrou = true;
                continue;
            }
            if (encontrou) break;
        }
        return encontrou ? total : null;
    }

    function extrairLoteAmplo(frase) {
        const direto = extrairLote(frase);
        if (direto != null) return direto;

        const n = normalizar(frase);
        const m = n.match(/\blote\s+(?:numero\s+)?([a-z\s-]{1,45})/);
        if (!m) return null;
        return numeroPorExtensoPt(m[1]);
    }

    function extrairQuantidadeAmpla(frase) {
        const n = normalizar(frase);
        const numerico = n.match(/(\d+(?:[.,]\d+)?)\s*(?:bags?|bagui?s?|begs?|beques?)/)
            || n.match(/(?:saiu|saida|retirou|retirar|tirou|tirar|baixou|baixar|descontou|descontar|entrou|entrada|recebeu|recebi|chegou|chegaram|adicionar|acrescentar|somar|colocar|coloca|poe|veio)\D{0,22}(\d+(?:[.,]\d+)?)/);
        if (numerico) return numero(numerico[1]);

        const antesBag = n.match(/([a-z\s-]{1,45})\s+(?:bags?|bagui?s?|begs?|beques?)\b/);
        if (antesBag) {
            const palavrasTrecho = palavras(antesBag[1]);
            const ultimas = palavrasTrecho.slice(-5).join(' ');
            const extenso = numeroPorExtensoPt(ultimas);
            if (extenso != null) return extenso;
        }

        return 0;
    }

    function mensagensUsuarioAnteriores(fraseAtual) {
        const atual = normalizar(fraseAtual);
        const lista = [];
        let pulouAtual = false;

        for (let i = mensagens.length - 1; i >= 0 && lista.length < 8; i--) {
            const m = mensagens[i];
            if (!m || m.tipo !== 'usuario') continue;
            const t = String(m.texto || '');
            if (!pulouAtual && normalizar(t) === atual) {
                pulouAtual = true;
                continue;
            }
            lista.push(t);
        }
        return lista;
    }

    function contextoAnterior(frase, estoque) {
        const anteriores = mensagensUsuarioAnteriores(frase);
        const contexto = {
            lote: null,
            cultivar: '',
            fazenda: '',
            quantidade: false,
            localizacao: false,
            umidade: false
        };

        for (const anterior of anteriores) {
            const n = normalizar(anterior);
            if (contexto.lote == null) contexto.lote = extrairLoteAmplo(anterior);
            if (!contexto.cultivar) contexto.cultivar = cultivarMencionadaAmpla(anterior, estoque);
            if (!contexto.fazenda) contexto.fazenda = fazendaMencionadaAmpla(anterior, estoque);
            if (!contexto.quantidade && /(quant|quanto|total|bags?|estoque|saldo|sobrou|sobra|restou|resta|tem|tenho|disponivel)/.test(n)) contexto.quantidade = true;
            if (!contexto.localizacao && /(onde|local|fica|esta|localiza)/.test(n)) contexto.localizacao = true;
            if (!contexto.umidade && /umidade/.test(n)) contexto.umidade = true;

            if (contexto.lote != null && contexto.cultivar && contexto.fazenda && contexto.quantidade) break;
        }
        return contexto;
    }

    function temUnidadeForaDoSeedControl(n) {
        return /\b(megas?|megabytes?|gigas?|gigabytes?|mb|gb|reais?|dinheiro|pix|km|quilometros?|litros?|horas?|minutos?|celular|internet|dados moveis)\b/.test(n);
    }

    function parecePerguntaQuantidade(n) {
        if (temUnidadeForaDoSeedControl(n)) return false;
        if (/(bags?|bagui?s?|begs?|beques?|estoque|saldo|sobra|sobrou|resta|restou|disponivel|quantidade)/.test(n)) return true;
        if (/(quanto|quantos|qual.*total|me fala.*total|tem quanto|quanto tem)/.test(n) && !/[a-z]+bytes?/.test(n)) return true;
        return false;
    }

    function fraseDeContinuacao(n) {
        return /^(e\b|e da\b|e do\b|e na\b|e no\b|e esse\b|e essa\b|e dele\b|e dela\b|e agora\b|quanto dele\b|quanto dela\b)/.test(n)
            || /\b(desse|dessa|deste|desta|dele|dela|o mesmo|a mesma)\b/.test(n);
    }

    function interpretarConsulta(frase) {
        const estoque = estoqueAtual();
        const n = normalizar(frase);
        const contexto = contextoAnterior(frase, estoque);

        if (!estoque.length && !/(ajuda|consegue|pode fazer|ola|oi|bom dia|boa tarde|boa noite)/.test(n)) {
            return 'Ainda não encontrei lotes cadastrados no estoque deste aparelho.';
        }

        if (/^(oi|ola|opa|e ai|bom dia|boa tarde|boa noite)\b/.test(n)) {
            return 'Olá! Pode falar comigo normalmente. Eu entendo perguntas sobre estoque, bags, cultivares, lotes, fazendas e umidade, e também lembro o assunto das mensagens anteriores.';
        }

        if (/(o que.*consegue|o que.*faz|ajuda|comandos|como usar|como funciona|entende o que)/.test(n)) {
            return 'Posso consultar estoque total, bags por cultivar ou fazenda, localizar lotes, listar cultivares e fazendas, verificar umidade e preparar entradas ou saídas de bags. Você também pode continuar o assunto: “quanto tem da Guepardo?” e depois só perguntar “e da Voraz?”. Alterações sempre pedem confirmação.';
        }

        const continuar = fraseDeContinuacao(n);
        let loteNumero = extrairLoteAmplo(frase);
        let cultivar = cultivarMencionadaAmpla(frase, estoque);
        let fazenda = fazendaMencionadaAmpla(frase, estoque);

        if (continuar) {
            if (loteNumero == null) loteNumero = contexto.lote;
            if (!cultivar) cultivar = contexto.cultivar;
            if (!fazenda) fazenda = contexto.fazenda;
        }

        const querQuantidade = parecePerguntaQuantidade(n) || (continuar && contexto.quantidade);
        const querLocalizacao = /(onde|local|fica|esta|localiza|encontra|qual fazenda|qual talhao)/.test(n) || (continuar && contexto.localizacao);

        if (loteNumero != null && (querLocalizacao || querQuantidade || /\blote\b/.test(n) || continuar)) {
            const encontrados = estoque.filter((x) => Number(x.lote) === loteNumero);
            if (!encontrados.length) return `Não encontrei o lote ${loteNumero}.`;
            if (encontrados.length === 1) return descreverLote(encontrados[0]) + '.';
            return `Encontrei ${encontrados.length} registros com o lote ${loteNumero}:\n` + encontrados.map((x) => '• ' + descreverLote(x)).join('\n');
        }

        if (cultivar && querQuantidade) {
            const itens = estoque.filter((x) => normalizar(x.cultivar) === normalizar(cultivar));
            const bags = itens.reduce((s, x) => s + numero(x.bags), 0);
            return `${cultivar}: ${formatarNumero(bags, 0)} bags em ${itens.length} lote${itens.length === 1 ? '' : 's'}.`;
        }

        if (fazenda && querQuantidade) {
            const itens = estoque.filter((x) => normalizar(x.fazenda) === normalizar(fazenda));
            const bags = itens.reduce((s, x) => s + numero(x.bags), 0);
            return `Na fazenda ${fazenda} há ${formatarNumero(bags, 0)} bags em ${itens.length} lote${itens.length === 1 ? '' : 's'}.`;
        }

        if (cultivar && querLocalizacao) {
            const itens = estoque.filter((x) => normalizar(x.cultivar) === normalizar(cultivar));
            if (!itens.length) return `Não encontrei a cultivar ${cultivar}.`;
            return `${cultivar} aparece em ${itens.length} lote${itens.length === 1 ? '' : 's'}:\n` + itens.slice(0, 20).map((x) => '• ' + descreverLote(x)).join('\n');
        }

        const umidadeNum = n.match(/umidade.*?(?:acima de|maior que|>|mais de)\s*(\d+(?:[.,]\d+)?)/);
        let limiteUmidade = umidadeNum ? numero(umidadeNum[1]) : null;
        if (limiteUmidade == null && /umidade/.test(n)) {
            const trecho = n.match(/(?:acima de|maior que|mais de)\s+([a-z\s-]{1,35})/);
            if (trecho) limiteUmidade = numeroPorExtensoPt(trecho[1]);
        }
        if (limiteUmidade != null) {
            const itens = estoque.filter((x) => numero(x.umidade) > limiteUmidade);
            if (!itens.length) return `Não encontrei lotes com umidade acima de ${formatarNumero(limiteUmidade, 1)}%.`;
            return `${itens.length} lote${itens.length === 1 ? '' : 's'} com umidade acima de ${formatarNumero(limiteUmidade, 1)}%:\n` +
                itens.slice(0, 20).map((x) => `• Lote ${x.lote} • ${x.cultivar || 'Sem cultivar'} • ${formatarNumero(x.umidade, 1)}%`).join('\n') +
                (itens.length > 20 ? `\n… e mais ${itens.length - 20}.` : '');
        }

        if (/(quais|lista|mostrar|mostra).*(cultivar|variedade)|cultivares.*tenho/.test(n)) {
            const mapa = new Map();
            estoque.forEach((x) => {
                const nome = String(x.cultivar || 'Sem cultivar').trim() || 'Sem cultivar';
                mapa.set(nome, (mapa.get(nome) || 0) + numero(x.bags));
            });
            return `${mapa.size} cultivares:\n` + [...mapa.entries()].sort((a,b) => b[1] - a[1]).map(([nome, bags]) => `• ${nome}: ${formatarNumero(bags, 0)} bags`).join('\n');
        }

        if (/(quais|lista|mostrar|mostra).*(fazenda)|fazendas.*tenho/.test(n)) {
            const mapa = new Map();
            estoque.forEach((x) => {
                const nome = String(x.fazenda || 'Sem fazenda').trim() || 'Sem fazenda';
                mapa.set(nome, (mapa.get(nome) || 0) + numero(x.bags));
            });
            return `${mapa.size} fazendas:\n` + [...mapa.entries()].sort((a,b) => b[1] - a[1]).map(([nome, bags]) => `• ${nome}: ${formatarNumero(bags, 0)} bags`).join('\n');
        }

        if (/(quant.*lote|total.*lote|lotes.*tenho)/.test(n)) {
            return `Há ${estoque.length} lotes cadastrados no estoque.`;
        }

        if (querQuantidade) {
            const bags = estoque.reduce((s, x) => s + numero(x.bags), 0);
            const cultivares = new Set(estoque.map((x) => normalizar(x.cultivar)).filter(Boolean)).size;
            return `O estoque tem ${formatarNumero(bags, 0)} bags, distribuídas em ${estoque.length} lotes e ${cultivares} cultivares.`;
        }

        return 'Ainda não entendi esse pedido com segurança. Pode falar de outro jeito ou citar o lote, cultivar, fazenda, bags, estoque ou umidade.';
    }

'''

texto = texto[:inicio] + bloco_consulta + texto[fim:]

inicio_mov = texto.find('    function detectarMovimento(frase) {')
fim_mov = texto.find('    function pedirConfirmacao(mov) {', inicio_mov)
if inicio_mov < 0 or fim_mov < 0:
    raise SystemExit('Não foi possível localizar detectarMovimento/pedirConfirmacao.')

bloco_mov = r'''    function detectarMovimento(frase) {
        const n = normalizar(frase);
        const estoque = estoqueAtual();
        const contexto = contextoAnterior(frase, estoque);
        let tipo = null;

        const saida = /\b(saiu|saida|retirou|retirar|tirou|tirar|baixou|baixar|baixa|descontou|descontar|despachou|despachei|mandou|mandei|enviou|enviei|carregou|carreguei)\b/;
        const entrada = /\b(entrou|entrada|recebeu|recebi|chegou|chegaram|adicionar|adiciona|acrescentar|somar|soma|colocar|coloca|poe|veio|vieram)\b/;

        if (saida.test(n)) tipo = 'saida';
        if (entrada.test(n)) tipo = 'entrada';
        if (!tipo) return null;

        let lote = extrairLoteAmplo(frase);
        let qtd = extrairQuantidadeAmpla(frase);
        let cultivar = cultivarMencionadaAmpla(frase, estoque);
        let fazenda = fazendaMencionadaAmpla(frase, estoque);

        const referenciaContextual = /\b(dele|dela|desse|dessa|deste|desta|mesmo|mesma)\b/.test(n) || !/\blote\b/.test(n);
        if (referenciaContextual) {
            if (lote == null) lote = contexto.lote;
            if (!cultivar) cultivar = contexto.cultivar;
            if (!fazenda) fazenda = contexto.fazenda;
        }

        if (qtd <= 0) {
            return { erro: 'Para movimentar, preciso da quantidade de bags. Exemplo: “Saiu 10 bags do lote 25”.' };
        }

        let candidatos = estoque.slice();
        if (lote != null) candidatos = candidatos.filter((x) => Number(x.lote) === lote);
        if (cultivar) candidatos = candidatos.filter((x) => normalizar(x.cultivar) === normalizar(cultivar));
        if (fazenda) candidatos = candidatos.filter((x) => normalizar(x.fazenda) === normalizar(fazenda));

        if (lote == null && !cultivar && !fazenda) {
            return { erro: 'Entendi a movimentação e a quantidade, mas preciso saber de qual lote, cultivar ou fazenda você está falando.' };
        }

        if (!candidatos.length) {
            const alvo = lote != null ? `lote ${lote}` : (cultivar || fazenda || 'registro informado');
            return { erro: `Não encontrei ${alvo} com essas informações.` };
        }

        if (candidatos.length > 1) {
            return {
                erro: `Encontrei mais de um registro possível. Diga também o lote, cultivar ou fazenda para eu saber qual movimentar.\n` +
                    candidatos.slice(0, 10).map((x) => '• ' + descreverLote(x)).join('\n')
            };
        }

        const item = candidatos[0];
        const atual = numero(item.bags);
        const depois = tipo === 'saida' ? atual - qtd : atual + qtd;

        if (tipo === 'saida' && depois < 0) {
            return { erro: `Esse lote tem ${formatarNumero(atual, 0)} bags. Não posso retirar ${formatarNumero(qtd, 0)} porque o estoque ficaria negativo.` };
        }

        return { tipo, qtd, item, atual, depois };
    }

'''

texto = texto[:inicio_mov] + bloco_mov + texto[fim_mov:]

JS.write_text(texto, encoding='utf-8')

final = JS.read_text(encoding='utf-8')
for marca in (
    'seedcontrol-assistente-entendimento-amplo-v384',
    'contextoAnterior',
    'numeroPorExtensoPt',
    'cultivarMencionadaAmpla',
    'extrairQuantidadeAmpla'
):
    if marca not in final:
        raise SystemExit(f'Marca esperada não encontrada: {marca}')

print('Assistente offline ampliado com contexto, sinônimos, números por extenso e tolerância a variações.')
