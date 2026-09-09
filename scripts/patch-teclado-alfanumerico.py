from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZIP = ROOT / "SeedControl_v3.8_revisado_apk (2).zip"
WORK = ROOT / "build_teclado_alfanumerico"
OUTPUT_ZIP = ROOT / "SeedControl_v3.8_teclado_alfanumerico.zip"

if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir()

with zipfile.ZipFile(SOURCE_ZIP) as archive:
    archive.extractall(WORK)

project_dirs = list(WORK.glob("*/"))
if len(project_dirs) != 1:
    raise SystemExit(f"Projeto inesperado no ZIP: {project_dirs}")
project = project_dirs[0]

policy = r'''/* SeedControl: teclado alfanumerico padrao em todos os campos editaveis. */
(function aplicarTecladoAlfanumericoPadrao() {
    function ajustarCampos() {
        document.querySelectorAll("input, textarea").forEach(function (campo) {
            if (campo.tagName === "INPUT" && campo.type === "file") return;
            if (campo.tagName === "INPUT" && ["button", "submit", "reset", "checkbox", "radio", "range", "color"].includes(campo.type)) return;
            if (campo.tagName === "INPUT") campo.type = "text";
            campo.setAttribute("inputmode", "text");
            campo.removeAttribute("pattern");
        });
    }
    ajustarCampos();
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", ajustarCampos, { once: true });
    }
})();
'''

html_files = sorted(project.glob("*.html"))
if not html_files:
    raise SystemExit("Nenhuma tela HTML encontrada")

for html_path in html_files:
    text = html_path.read_text(encoding="utf-8")
    if "aplicarTecladoAlfanumericoPadrao" in text:
        continue
    marker = "</body>"
    if marker not in text:
        raise SystemExit(f"Marcador </body> nao encontrado em {html_path.name}")
    text = text.replace(marker, f"<script>{policy}</script>\n\n{marker}", 1)
    html_path.write_text(text, encoding="utf-8")

if OUTPUT_ZIP.exists():
    OUTPUT_ZIP.unlink()
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(WORK.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(WORK))

print(f"Telas atualizadas: {len(html_files)}")
print(f"ZIP gerado: {OUTPUT_ZIP}")
print("Politica: inputmode=text e type=text para campos editaveis; uploads preservados.")
