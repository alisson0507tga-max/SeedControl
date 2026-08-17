from pathlib import Path

arquivo = Path("native/www/database.js")

if not arquivo.exists():
    raise SystemExit("database.js não encontrado em native/www")

texto = arquivo.read_text(encoding="utf-8")

if "function existeLoteDuplicado(" not in texto:
    marcador_servico = "function cadastrarLote(novoLote, opcoes = {}) {"

    if marcador_servico not in texto:
        raise SystemExit("Função cadastrarLote não encontrada em database.js")

    helper = r'''function chaveCadastroLote(lote) {

    return [
        normalizarTexto(lote && lote.cultivar),
        String(Number(lote && lote.lote) || ""),
        normalizarTexto(lote && lote.fazenda),
        normalizarTexto(lote && lote.peneira),
        normalizarTexto(lote && lote.talhao)
    ].join("|");

}

function existeLoteDuplicado(estoque, candidato, idIgnorar = null) {

    const chaveCandidato = chaveCadastroLote(candidato);
    const base = Array.isArray(estoque) ? estoque : [];

    return base.some(item => {

        if (!item) return false;

        if (
            idIgnorar !== null &&
            Number(item.id) === Number(idIgnorar)
        ) {
            return false;
        }

        return chaveCadastroLote(item) === chaveCandidato;

    });

}

'''

    texto = texto.replace(
        marcador_servico,
        helper + marcador_servico,
        1
    )

marcador_cadastro = "    const estoque = carregarEstoque();\n\n    const loteSalvo = {"

if "Este lote já está cadastrado" not in texto:
    if marcador_cadastro not in texto:
        raise SystemExit("Ponto de inserção do cadastro não encontrado")

    validacao_cadastro = '''    const estoque = carregarEstoque();\n\n    if (existeLoteDuplicado(estoque, novoLote)) {\n\n        return {\n            ok: false,\n            mensagem: "Este lote já está cadastrado com a mesma cultivar, fazenda, peneira e talhão."\n        };\n\n    }\n\n    const loteSalvo = {'''

    texto = texto.replace(
        marcador_cadastro,
        validacao_cadastro,
        1
    )

marcador_edicao = '''    if (indice < 0) {

        return {
            ok: false,
            mensagem: "Lote não encontrado."
        };

    }

    const atualizado = {'''

if "existeLoteDuplicado(estoque, novoLote, idOriginal)" not in texto:
    if marcador_edicao not in texto:
        raise SystemExit("Ponto de inserção da edição não encontrado")

    validacao_edicao = '''    if (indice < 0) {

        return {
            ok: false,
            mensagem: "Lote não encontrado."
        };

    }

    if (existeLoteDuplicado(estoque, novoLote, idOriginal)) {

        return {
            ok: false,
            mensagem: "Já existe outro lote cadastrado com a mesma cultivar, fazenda, peneira e talhão."
        };

    }

    const atualizado = {'''

    texto = texto.replace(
        marcador_edicao,
        validacao_edicao,
        1
    )

arquivo.write_text(texto, encoding="utf-8")
print("Validação de duplicidade aplicada em database.js")
