#!/usr/bin/env python3
"""Remove as colunas Germinação e Observação da entrada comercial.

Os campos continuam disponíveis no cadastro; apenas a tabela e as exportações
Excel/PDF deixam de exibi-los.
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path


MARKER = "COLUNAS_GERMINACAO_OBSERVACAO_REMOVIDAS_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Padrão não encontrado em {label}: {old[:100]!r}")
    return text.replace(old, new, 1)


def patch_entrada_js(text: str) -> str:
    label = "entrada-comercial-v3904.js"
    if MARKER in text:
        return text
    text = text.replace("// seedcontrol-entrada-comercial-ui-v3904", f"// {MARKER}\n// seedcontrol-entrada-comercial-ui-v3904", 1)
    text = replace_once(text, 'colspan="9"', 'colspan="7"', label)
    text = replace_once(
        text,
        'corpo.innerHTML = regs.map(r => `<tr data-id="${esc(r.id)}"><td>${esc(r.dataEntrada)}</td><td>${esc(r.cultivar)}</td><td>${esc(r.lote)}</td><td>${fmt(r.bags,2)}</td><td>${fmt(r.kg,3)}</td><td>${fmt(r.pms,2)}</td><td>${esc(r.germinacao || "-")}</td><td>${esc(r.observacao || "")}</td><td><button class="ec3904-editar" data-editar="${esc(r.id)}">✏️</button></td></tr>`).join("");',
        'corpo.innerHTML = regs.map(r => `<tr data-id="${esc(r.id)}"><td>${esc(r.dataEntrada)}</td><td>${esc(r.cultivar)}</td><td>${esc(r.lote)}</td><td>${fmt(r.bags,2)}</td><td>${fmt(r.kg,3)}</td><td>${fmt(r.pms,2)}</td><td><button class="ec3904-editar" data-editar="${esc(r.id)}">✏️</button></td></tr>`).join("");',
        label,
    )
    text = replace_once(text, '["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)","GERMINAÇÃO (nota)","Observação"]', '["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)"]', label)
    text = replace_once(text, 'n(r.pms),r.germinacao || "",r.observacao || ""]', 'n(r.pms)]', label)
    text = replace_once(text, 'e:{r:0,c:7}', 'e:{r:0,c:5}', label)
    text = replace_once(text, '[{wch:14},{wch:25},{wch:22},{wch:10},{wch:13},{wch:11},{wch:18},{wch:31}]', '[{wch:14},{wch:25},{wch:22},{wch:10},{wch:13},{wch:11}]', label)
    text = replace_once(text, 'for (let c=0;c<8;c++)', 'for (let c=0;c<6;c++)', label)
    text = replace_once(text, 'for (let c=0;c<8;c++)', 'for (let c=0;c<6;c++)', label)
    text = replace_once(text, 'for (let c=0;c<8;c++)', 'for (let c=0;c<6;c++)', label)
    text = replace_once(text, '["","","TOTAL",totalBags,totalKg,"","",""]', '["","","TOTAL",totalBags,totalKg,""]', label)
    return text


def patch_planilhas_fieis(text: str) -> str:
    label = "planilhas-fieis-v3914.js"
    if MARKER in text:
        return text.replace('["","","TOTAL",tb,tk,"","",""]', '["","","TOTAL",tb,tk,""]', 1).replace('for(let c=0;c<8;c++)cell(lr,c)', 'for(let c=0;c<6;c++)cell(lr,c)', 1)
    text = text.replace("// seedcontrol-planilhas-fieis-v3914", f"// {MARKER}\n// seedcontrol-planilhas-fieis-v3914", 1)
    text = replace_once(text, 'r.pms),r.germinacao||"",r.observacao||""]', 'r.pms)]', label)
    text = replace_once(text, '["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)","GERMINAÇÃO (nota)","Observação"]', '["DATA(entrada)","CULTIVAR","LOTE","BAGS","Kg","PMS(g)"]', label)
    text = replace_once(text, 'e:{r:0,c:7}', 'e:{r:0,c:5}', label)
    text = replace_once(text, '[{wch:15},{wch:28},{wch:23},{wch:10},{wch:13},{wch:11},{wch:18},{wch:32}]', '[{wch:15},{wch:28},{wch:23},{wch:10},{wch:13},{wch:11}]', label)
    text = replace_once(text, 'for(let c=0;c<8;c++)', 'for(let c=0;c<6;c++)', label)
    text = replace_once(text, 'for(let c=0;c<8;c++)', 'for(let c=0;c<6;c++)', label)
    text = replace_once(text, 'for(let c=0;c<8;c++)', 'for(let c=0;c<6;c++)', label)
    text = replace_once(text, '["","","TOTAL",tb,tk,"","",""]', '["","","TOTAL",tb,tk,""]', label)
    text = replace_once(text, 'for(let c=0;c<8;c++)cell(lr,c)', 'for(let c=0;c<6;c++)cell(lr,c)', label)
    text = replace_once(text, 'head:[["DATA ENTRADA","CULTIVAR","LOTE","BAGS","Kg","PMS(g)","GERMINAÇÃO","Observação"]]', 'head:[["DATA ENTRADA","CULTIVAR","LOTE","BAGS","Kg","PMS(g)"]]', label)
    return text


def patch_entrada_html(text: str) -> str:
    label = "entrada-comercial.html"
    if MARKER in text:
        return text
    text = text.replace("<head>", f"<head>\n<!-- {MARKER} -->", 1)
    text = replace_once(text, 'colspan="9">ENTRADA DE SEMENTES SOJA', 'colspan="7">ENTRADA DE SEMENTES SOJA', label)
    text = replace_once(text, '<th>DATA<br>ENTRADA</th><th>CULTIVAR</th><th>LOTE</th><th>BAGS</th><th>Kg</th><th>PMS(g)</th><th>GERMINAÇÃO<br>(nota)</th><th>OBSERVAÇÃO</th><th>AÇÃO</th>', '<th>DATA<br>ENTRADA</th><th>CULTIVAR</th><th>LOTE</th><th>BAGS</th><th>Kg</th><th>PMS(g)</th><th>AÇÃO</th>', label)
    text = replace_once(text, '<td colspan="9">Carregando...', '<td colspan="7">Carregando...', label)
    return text


def patch_css(text: str) -> str:
    # Ajusta apenas a largura fixa da tabela e remove as regras das antigas colunas 7/8.
    if MARKER in text:
        return text
    text = text.replace(".ec3904-tabela{width:1120px!important;min-width:1120px!important;", ".ec3904-tabela{width:900px!important;min-width:900px!important;", 1)
    text = text.replace(".ec3904-tabela th:nth-child(7),.ec3904-tabela td:nth-child(7){width:130px}.ec3904-tabela th:nth-child(8),.ec3904-tabela td:nth-child(8){width:260px}.ec3904-tabela th:nth-child(9),.ec3904-tabela td:nth-child(9){width:80px}", ".ec3904-tabela th:nth-child(7),.ec3904-tabela td:nth-child(7){width:80px}", 1)
    return f"/* {MARKER} */\n" + text


def patch_directory(project: Path) -> None:
    files = {
        "entrada-comercial-v3904.js": patch_entrada_js,
        "planilhas-fieis-v3914.js": patch_planilhas_fieis,
        "entrada-comercial.html": patch_entrada_html,
        "style.css": patch_css,
    }
    for name, fn in files.items():
        path = project / name
        if not path.exists():
            raise RuntimeError(f"Arquivo esperado não encontrado: {path}")
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")


def patch_zip(path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="seedcontrol-patch-") as tmp:
        work = Path(tmp) / "source"
        with zipfile.ZipFile(path) as archive:
            archive.extractall(work)
        projects = [p for p in work.iterdir() if p.is_dir()]
        if len(projects) != 1:
            raise RuntimeError(f"Estrutura inesperada no ZIP: {path}")
        patch_directory(projects[0])
        new_path = path.with_suffix(path.suffix + ".tmp")
        with zipfile.ZipFile(new_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(work.rglob("*")):
                if item.is_file():
                    archive.write(item, item.relative_to(work))
        new_path.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    if bool(args.directory) == bool(args.zip):
        parser.error("informe exatamente um de --directory ou --zip")
    if args.directory:
        patch_directory(args.directory)
    else:
        patch_zip(args.zip)
    print(f"Patch aplicado: {args.directory or args.zip}")


if __name__ == "__main__":
    main()
