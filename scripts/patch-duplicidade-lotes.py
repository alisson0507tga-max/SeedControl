from pathlib import Path
import re

HELPER = r'''// seedcontrol-duplicidade-helper
function seedControlNormalizarDuplicidade(valor) {
    return String(valor == null ? "" : valor).trim().toLowerCase();
}

function seedControlChaveDuplicidade(lote) {
    return [
        seedControlNormalizarDuplicidade(lote && lote.cultivar),
        String(Number(lote && lote.lote) || ""),
        seedControlNormalizarDuplicidade(lote && lote.fazenda),
        seedControlNormalizarDuplicidade(lote && lote.peneira),
        seedControlNormalizarDuplicidade(lote && lote.talhao)
    ].join("|");
}

function seedControlExisteLoteDuplicado(base, candidato, idIgnorar = null) {
    const chave = seedControlChaveDuplicidade(candidato);
    const lista = Array.isArray(base) ? base : [];

    return lista.some(item => {
        if (!item) return false;

        if (
            idIgnorar !== null &&
            idIgnorar !== undefined &&
            Number(item.id) === Number(idIgnorar)
        ) {
            return false;
        }

        return seedControlChaveDuplicidade(item) === chave;
    });
}

'''


def inserir_antes_regex(texto, padrao, bloco, descricao):
    achado = re.search(padrao, texto, flags=re.MULTILINE)
    if not achado:
        raise SystemExit(descricao)
    return texto[:achado.start()] + bloco + texto[achado.start():]


# =====================================
# CADASTRO
# =====================================

cadastro = Path("native/www/cadastro.js")
if not cadastro.exists():
    raise SystemExit("cadastro.js não encontrado em native/www")

texto = cadastro.read_text(encoding="utf-8")

if "// seedcontrol-duplicidade-helper" not in texto:
    texto = HELPER + texto

if "// seedcontrol-duplicidade-cadastro" not in texto:
    validacao = r'''    // seedcontrol-duplicidade-cadastro
    const estoqueDuplicidade = carregarEstoque();

    if (seedControlExisteLoteDuplicado(estoqueDuplicidade, novoLote)) {
        alert("Este lote já está cadastrado com a mesma cultivar, fazenda, peneira e talhão.");
        return;
    }

'''

    if re.search(r"^\s*(?:const|let|var)\s+resultado\s*=\s*cadastrarLote\s*\(", texto, flags=re.MULTILINE):
        texto = inserir_antes_regex(
            texto,
            r"^\s*(?:const|let|var)\s+resultado\s*=\s*cadastrarLote\s*\(",
            validacao,
            "Chamada cadastrarLote não encontrada em cadastro.js"
        )
    elif re.search(r"^\s*estoque\.push\s*\(\s*novoLote\s*\)\s*;", texto, flags=re.MULTILINE):
        texto = inserir_antes_regex(
            texto,
            r"^\s*estoque\.push\s*\(\s*novoLote\s*\)\s*;",
            validacao,
            "Ponto de salvamento do lote não encontrado em cadastro.js"
        )
    else:
        raise SystemExit("Não foi possível localizar o salvamento em cadastro.js")

cadastro.write_text(texto, encoding="utf-8")
print("Bloqueio de duplicidade aplicado em cadastro.js")


# =====================================
# EDIÇÃO
# =====================================

editar = Path("native/www/editar.js")
if editar.exists():
    texto = editar.read_text(encoding="utf-8")

    if "// seedcontrol-duplicidade-helper" not in texto:
        texto = HELPER + texto

    if "// seedcontrol-duplicidade-edicao" not in texto:
        usa_novo_lote = bool(re.search(r"\bnovoLote\s*=\s*\{", texto))
        candidato = "novoLote" if usa_novo_lote else "registro"

        validacao = f'''    // seedcontrol-duplicidade-edicao\n    const idDuplicidadeAtual =\n        typeof idOriginal !== "undefined"\n            ? idOriginal\n            : (\n                typeof id !== "undefined"\n                    ? id\n                    : (\n                        typeof registro !== "undefined" && registro\n                            ? registro.id\n                            : null\n                    )\n            );\n\n    const estoqueDuplicidadeEdicao = carregarEstoque();\n\n    if (seedControlExisteLoteDuplicado(estoqueDuplicidadeEdicao, {candidato}, idDuplicidadeAtual)) {{\n        alert("Já existe outro lote cadastrado com a mesma cultivar, fazenda, peneira e talhão.");\n        return;\n    }}\n\n'''

        if usa_novo_lote and re.search(r"^\s*(?:const|let|var)\s+resultado\s*=\s*atualizarLote\s*\(", texto, flags=re.MULTILINE):
            texto = inserir_antes_regex(
                texto,
                r"^\s*(?:const|let|var)\s+resultado\s*=\s*atualizarLote\s*\(",
                validacao,
                "Chamada atualizarLote não encontrada em editar.js"
            )
        elif re.search(r"^\s*salvarEstoque\s*\(\s*estoque", texto, flags=re.MULTILINE):
            texto = inserir_antes_regex(
                texto,
                r"^\s*salvarEstoque\s*\(\s*estoque",
                validacao,
                "Ponto de salvamento não encontrado em editar.js"
            )
        else:
            print("Aviso: padrão de edição não reconhecido; cadastro continuará protegido.")

    editar.write_text(texto, encoding="utf-8")
    print("Proteção de duplicidade revisada em editar.js")

print("Validação de duplicidade concluída.")
