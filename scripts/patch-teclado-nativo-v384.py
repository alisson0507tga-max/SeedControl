from pathlib import Path
import re

ROOT = Path('native/www')
if not ROOT.exists():
    raise SystemExit('native/www não encontrado.')

MARCA = '<!-- seedcontrol-teclado-nativo-v3826 -->'

# 1) Remove scripts que desenham faixas próprias de sugestão/colar.
# Mantemos o CSS final de 3825 porque ele também corrige o espaço do rodapé.
for pagina in ROOT.glob('*.html'):
    texto = pagina.read_text(encoding='utf-8')

    texto = re.sub(
        r'\s*<script[^>]+src=["\'][^"\']*seed-teclado-final-v3825\.js[^"\']*["\'][^>]*></script>',
        '',
        texto,
        flags=re.I
    )

    # Remove também o antigo script JS de sugestões; nesta build os atributos
    # são gravados diretamente no HTML antes de o IME abrir.
    texto = re.sub(
        r'\s*<script[^>]+src=["\'][^"\']*teclado-sugestoes-v384\.js[^"\']*["\'][^>]*></script>',
        '',
        texto,
        flags=re.I
    )

    if MARCA not in texto and '</body>' in texto:
        texto = texto.replace('</body>', f'    {MARCA}\n</body>', 1)

    pagina.write_text(texto, encoding='utf-8')


def preparar_tag(tag: str) -> str:
    baixo = tag.lower()

    # Ignora campos que não devem receber teclado de texto/sugestões.
    m_tipo = re.search(r'\btype\s*=\s*["\']([^"\']+)["\']', tag, flags=re.I)
    tipo = (m_tipo.group(1).lower() if m_tipo else 'text')
    if tipo in {'number', 'date', 'time', 'datetime-local', 'month', 'week', 'file', 'checkbox', 'radio', 'hidden', 'range', 'color', 'button', 'submit', 'reset'}:
        return tag

    attrs = {
        'autocomplete': 'on',
        'autocorrect': 'on',
        'spellcheck': 'true',
        'autocapitalize': 'sentences',
    }

    novo = tag
    for nome, valor in attrs.items():
        if re.search(rf'\b{re.escape(nome)}\s*=', novo, flags=re.I):
            novo = re.sub(
                rf'\b{re.escape(nome)}\s*=\s*["\'][^"\']*["\']',
                f'{nome}="{valor}"',
                novo,
                count=1,
                flags=re.I
            )
        else:
            novo = novo[:-1] + f' {nome}="{valor}">' if novo.endswith('>') else novo

    return novo


# 2) Grava os atributos de texto DIRETAMENTE no HTML antes de o teclado abrir.
# Isso evita depender de focusin/JS tardio, que pode acontecer depois de o IME
# já ter criado a conexão de entrada.
for nome in ('assistente-chat-v384.html', 'assistente.html', 'cadastro.html'):
    pagina = ROOT / nome
    if not pagina.exists():
        continue

    texto = pagina.read_text(encoding='utf-8')
    texto = re.sub(r'<input\b[^>]*>', lambda m: preparar_tag(m.group(0)), texto, flags=re.I)
    texto = re.sub(r'<textarea\b[^>]*>', lambda m: preparar_tag(m.group(0)), texto, flags=re.I)

    # Campo do Assistente: garante semântica explícita de mensagem de texto.
    if 'assistenteEntrada' in texto:
        texto = re.sub(
            r'(<textarea\b[^>]*\bid=["\']assistenteEntrada["\'][^>]*)(>)',
            lambda m: (
                m.group(1)
                if re.search(r'\binputmode\s*=', m.group(1), flags=re.I)
                else m.group(1) + ' inputmode="text"'
            ) + (
                ''
                if re.search(r'\benterkeyhint\s*=', m.group(1), flags=re.I)
                else ' enterkeyhint="send"'
            ) + m.group(2),
            texto,
            count=1,
            flags=re.I
        )

    pagina.write_text(texto, encoding='utf-8')

# 3) Validações.
assistente = ROOT / 'assistente-chat-v384.html'
cadastro = ROOT / 'cadastro.html'
if not assistente.exists() or not cadastro.exists():
    raise SystemExit('Assistente ou cadastro não encontrado.')

assist = assistente.read_text(encoding='utf-8')
cad = cadastro.read_text(encoding='utf-8')

for html, nome in ((assist, 'Assistente'), (cad, 'Cadastro')):
    if 'seed-teclado-final-v3825.js' in html:
        raise SystemExit(f'Barra custom 3825 ainda carregada em {nome}.')
    if 'teclado-sugestoes-v384.js' in html:
        raise SystemExit(f'Script antigo de sugestões ainda carregado em {nome}.')

for marca in ('autocomplete="on"', 'autocorrect="on"', 'spellcheck="true"'):
    if marca not in assist:
        raise SystemExit(f'Atributo ausente no Assistente: {marca}')
    if marca not in cad:
        raise SystemExit(f'Atributo ausente no Cadastro: {marca}')

if 'id="assistenteEntrada"' not in assist or 'inputmode="text"' not in assist:
    raise SystemExit('Campo do Assistente não preparado como texto nativo.')

print('Teclado nativo preparado: barra custom removida e campos textuais configurados antes do foco.')
