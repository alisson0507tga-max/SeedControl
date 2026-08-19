from pathlib import Path
import re

ROOT = Path('native/www')
HTML = ROOT / 'movimentacao.html'

if not HTML.exists():
    raise SystemExit('movimentacao.html não encontrado.')

texto = HTML.read_text(encoding='utf-8')

# O patch do relatório de saídas originalmente procura esta âncora literal.
# Patches visuais anteriores podem ter acrescentado classes/atributos no label,
# portanto normalizamos somente o label imediatamente associado ao textarea #obs.
ancora = '<label><b>Observação</b></label>'

if ancora not in texto:
    padrao = re.compile(
        r'<label\b[^>]*>\s*(?:<b\b[^>]*>)?\s*Observa(?:ç|c)[aã]o\s*(?:</b>)?\s*</label>\s*(?=<textarea\b[^>]*\bid=["\']obs["\'])',
        re.I | re.S,
    )
    texto, qtd = padrao.subn(ancora + '\n\n', texto, count=1)

    if qtd == 0:
        # Fallback robusto: se o label foi removido/reorganizado, ancora direto
        # no textarea de observação, sem alterar o próprio campo.
        padrao_textarea = re.compile(
            r'(?=<textarea\b[^>]*\bid=["\']obs["\'])',
            re.I,
        )
        texto, qtd = padrao_textarea.subn(ancora + '\n\n', texto, count=1)

    if qtd == 0:
        raise SystemExit('Campo textarea #obs não encontrado em movimentacao.html')

HTML.write_text(texto, encoding='utf-8')

final = HTML.read_text(encoding='utf-8')
if ancora not in final:
    raise SystemExit('Falha ao preparar âncora compatível de Observação.')
if not re.search(r'<textarea\b[^>]*\bid=["\']obs["\']', final, re.I):
    raise SystemExit('textarea #obs ausente após compatibilidade.')

print('Compatibilidade do Relatório de Saídas preparada: âncora de Observação normalizada via textarea #obs.')
