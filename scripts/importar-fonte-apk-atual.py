from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
APK = Path('/home/ubuntu/upload/SeedControl-v3.8.4-uso-imediato-3934-signed.apk')
EXTRACTED = ROOT / 'source-apk-v3.8.4'
PUBLIC = EXTRACTED / 'assets' / 'public'
OUTPUT = ROOT / 'SeedControl_v3.8.4_uso_imediato_source.zip'

if not APK.exists():
    raise SystemExit(f'APK não encontrado: {APK}')
if EXTRACTED.exists():
    shutil.rmtree(EXTRACTED)
EXTRACTED.mkdir()
with zipfile.ZipFile(APK) as archive:
    archive.extractall(EXTRACTED)
if not PUBLIC.is_dir():
    raise SystemExit('O APK não contém assets/public; fonte inesperada.')

if OUTPUT.exists():
    OUTPUT.unlink()
with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(PUBLIC.rglob('*')):
        if path.is_file():
            archive.write(path, Path('SeedControl_v3.8.4_uso_imediato') / path.relative_to(PUBLIC))

print(f'Fonte oficial copiada de: {APK}')
print(f'Arquivos públicos: {sum(1 for p in PUBLIC.rglob("*") if p.is_file())}')
print(f'Fonte ZIP: {OUTPUT}')
print('PDFs físicos no APK: nenhum; geração de PDF está incluída nos módulos jsPDF e relatórios.')
