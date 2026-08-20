from pathlib import Path
import runpy

SAFE = Path("scripts/patch-entrada-comercial-v3903-safe.py")
ANTIGO = Path("scripts/patch-entrada-comercial-v384.py")

if not SAFE.exists():
    raise SystemExit("patch seguro da Entrada Comercial 3903 não encontrado")
if not ANTIGO.exists():
    raise SystemExit("patch comercial antigo não encontrado")

# Valida o patch seguro antes de executar.
fonte_safe = SAFE.read_text(encoding="utf-8")
compile(fonte_safe, str(SAFE), "exec")

# Aplica a Entrada Comercial usando somente a rotina segura.
runpy.run_path(str(SAFE), run_name="__main__")

# O workflow antigo chama patch-entrada-comercial-v384.py logo depois.
# Neutralizamos essa segunda execução para não repetir as âncoras frágeis antigas.
ANTIGO.write_text(
    'print("Entrada Comercial 3903 já aplicada pelo patch seguro.")\n',
    encoding="utf-8",
)

print("Fix 3903 concluído: patch seguro aplicado e patch antigo neutralizado.")
