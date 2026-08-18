from pathlib import Path

CSS = Path('native/www/estoque-v384.css')

if not CSS.exists():
    raise SystemExit('estoque-v384.css não encontrado.')

css = CSS.read_text(encoding='utf-8')

marcador = '/* seedcontrol-estoque-refino-v384 */'

if marcador not in css:
    css += r'''

/* seedcontrol-estoque-refino-v384 */

/* Remove somente o destaque visual de nível de estoque.
   A lógica e os dados continuam existindo no app. */
.estoque-body #lista .card-registro {
    border-left: 1px solid rgba(148, 163, 184, .18) !important;
    padding: 13px !important;
    column-gap: 10px;
    border-radius: 16px;
}

.estoque-body #lista .card-registro > p:first-of-type {
    display: none !important;
}

/* Card do lote mais compacto. */
.estoque-body #lista .card-registro > h2 {
    margin: 0 0 7px;
    font-size: 20px;
}

.estoque-body #lista .card-registro > p {
    margin: 3px 0;
    padding: 5px 7px;
    border-radius: 9px;
    font-size: 12.5px;
    line-height: 1.25;
}

.estoque-body #lista .card-registro strong {
    margin-bottom: 1px;
    font-size: 10.5px;
}

/* Ações mais discretas e padronizadas. */
.estoque-body #lista .btn-movimentar {
    min-height: 46px;
    margin: 9px 0 0 !important;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 700;
    box-shadow: none;
}

.estoque-body #lista .acoes-registro {
    gap: 7px;
    margin-top: 7px;
}

.estoque-body #lista .acoes-registro button {
    min-height: 43px;
    padding: 8px 6px;
    border: 1px solid rgba(255, 255, 255, .08);
    border-radius: 11px;
    font-size: 12.5px;
    font-weight: 650;
    box-shadow: none !important;
}

.estoque-body #lista .btn-editar {
    background: linear-gradient(145deg, #256aa3, #1e5d91) !important;
}

.estoque-body #lista .btn-qr {
    background: linear-gradient(145deg, #6547a7, #533991) !important;
}

.estoque-body #lista .btn-excluir {
    background: linear-gradient(145deg, #ad3e3e, #943535) !important;
}

@media (max-width: 390px) {
    .estoque-body #lista .card-registro {
        padding: 11px !important;
        column-gap: 8px;
    }

    .estoque-body #lista .card-registro > p {
        padding: 5px 6px;
        font-size: 12px;
    }

    .estoque-body #lista .acoes-registro button {
        font-size: 12px;
        padding-left: 4px;
        padding-right: 4px;
    }
}
'''

CSS.write_text(css, encoding='utf-8')

final = CSS.read_text(encoding='utf-8')

validacoes = [
    marcador,
    'border-left: 1px solid rgba(148, 163, 184, .18) !important;',
    'display: none !important;',
    'min-height: 43px;',
]

for trecho in validacoes:
    if trecho not in final:
        raise SystemExit(f'Validação do refino do Estoque falhou: {trecho}')

print('Estoque refinado: alerta visual removido, card compactado e ações padronizadas.')
