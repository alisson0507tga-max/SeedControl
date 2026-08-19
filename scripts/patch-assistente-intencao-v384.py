from pathlib import Path

JS = Path('native/www/assistente-v384.js')
if not JS.exists():
    raise SystemExit('assistente-v384.js não encontrado.')

texto = JS.read_text(encoding='utf-8')

antigo = 'if (/(quant.*bags|bags.*total|estoque total|quanto.*estoque|quanto.*tenho)/.test(n)) {'
novo = 'if (/(quant(?:o|os|a|as)?.*(?:bags?|estoque)|(?:bags?|estoque).*total|quanto.*estoque)/.test(n)) {'

if antigo not in texto:
    raise SystemExit('Regra antiga de estoque total não encontrada no Assistente.')

texto = texto.replace(antigo, novo, 1)

# Marca para validação da correção.
texto = texto.replace(
    '// seedcontrol-assistente-conversa-v384',
    '// seedcontrol-assistente-conversa-v384\n// seedcontrol-assistente-intencao-v384',
    1
)

JS.write_text(texto, encoding='utf-8')

final = JS.read_text(encoding='utf-8')
if 'quanto.*tenho' in final:
    raise SystemExit('Regra ampla quanto.*tenho ainda existe.')
if 'seedcontrol-assistente-intencao-v384' not in final:
    raise SystemExit('Marca da correção de intenção não encontrada.')

print('Interpretação do Assistente corrigida: consultas genéricas não viram estoque total.')
