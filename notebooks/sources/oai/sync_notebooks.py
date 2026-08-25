"""Regenerate the active OAI development notebooks from pipeline nodes."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXTRACT_NODES = ROOT / "src/kedro_cic/pipelines/oai_extract/nodes.py"


def _cell(cell_type: str, source: str) -> dict:
    cell = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(True)}
    if cell_type == "code":
        cell.update(execution_count=None, outputs=[])
    return cell


def _symbols(path: Path, names: list[str]) -> list[str]:
    """Read exact top-level definitions or assignments in source order."""
    source = path.read_text()
    tree = ast.parse(source)
    selected = []
    for node in tree.body:
        node_names = []
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            node_names = [node.name]
        elif isinstance(node, ast.Assign):
            node_names = [
                target.id for target in node.targets if isinstance(target, ast.Name)
            ]
        if set(node_names) & set(names):
            selected.append(ast.get_source_segment(source, node))
    missing = set(names) - {
        name
        for definition in selected
        for name in names
        if f"def {name}(" in definition or definition.startswith(f"{name} =")
    }
    if missing:
        raise ValueError(f"Definitions not found in {path}: {sorted(missing)}")
    return selected


def _write_notebook(path: Path, title: str, description: str, cells: list[dict]) -> None:
    notebook = {
        "cells": [
            _cell("markdown", f"# {title}\n\n{description}\n"),
            *cells,
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")


def _definition_cells(names: list[str]) -> list[dict]:
    return [_cell("code", definition + "\n") for definition in _symbols(EXTRACT_NODES, names)]


def main() -> None:
    extract_dir = ROOT / "notebooks/sources/oai/01_extract"
    imports = _cell(
        "code",
        "import inspect\n"
        "import os\n"
        "import time\n"
        "import xml.etree.ElementTree as ET\n"
        "from urllib.parse import urlencode\n\n"
        "import certifi\n"
        "import pandas as pd\n"
        "import requests\n"
        "from requests.packages.urllib3.exceptions import InsecureRequestWarning\n",
    )
    parameters = _cell(
        "code",
        "options = catalog.load(\"params:oai_extract_options\").copy()\n"
        "options[\"env\"] = \"dev\"\n"
        "if options.get(\"date_windows\"):\n"
        "    options[\"date_windows\"] = options[\"date_windows\"][:1]\n"
        "options\n",
    )

    _write_notebook(
        extract_dir / "oai_extract_get_oai_response.ipynb",
        "Cliente HTTP OAI",
        "Prueba aislada de la función HTTP compartida. La celda de la función se copia exactamente desde `nodes.py` y puede editarse antes de trasladar un cambio al pipeline.",
        [
            imports,
            *_definition_cells(["get_oai_response"]),
            parameters,
            _cell(
                "code",
                "url = f\"{options['base_url'].rstrip('/')}/{options['context']}?verb=Identify\"\n"
                "response = get_oai_response(url)\n"
                "assert response is not None and response.ok\n"
                "response.text[:1000]\n",
            ),
        ],
    )

    _write_notebook(
        extract_dir / "oai_extract_identifiers.ipynb",
        "Manifiesto OAI",
        "Ejecuta `ListIdentifiers` en modo acotado, conserva eliminados y permite verificar el contrato del manifiesto sin escribir datasets.",
        [
            imports,
            *_definition_cells(
                ["get_oai_response", "log_oai_progress", "oai_extract_identifiers"]
            ),
            parameters,
            _cell(
                "code",
                "call_options = {name: options[name] for name in inspect.signature(oai_extract_identifiers).parameters if name in options}\n"
                "df_identifiers, df_identifiers_preview = oai_extract_identifiers(**call_options)\n"
                "assert df_identifiers[\"record_id\"].notna().all()\n"
                "assert not df_identifiers[\"record_id\"].duplicated().any()\n"
                "assert df_identifiers[\"_source_key\"].notna().all()\n"
                "{\"rows\": len(df_identifiers), \"deleted\": int(df_identifiers[\"is_deleted\"].fillna(False).sum()), \"sources\": df_identifiers[\"_source_key\"].value_counts().to_dict()}\n",
            ),
            _cell("code", "df_identifiers_preview\n"),
        ],
    )

    record_symbols = [
        "get_oai_response",
        "log_oai_progress",
        "OAI_NAMESPACES",
        "OAI_RECORD_COLUMNS",
        "OAI_PROVENANCE_COLUMNS",
        "add_oai_provenance",
        "parse_oai_record",
        "oai_extract_records",
    ]
    _write_notebook(
        extract_dir / "oai_extract_records.ipynb",
        "Cosecha masiva de registros OAI",
        "Ejecuta `ListRecords` en modo acotado y permite inspeccionar registros y errores de página antes de guardar el snapshot.",
        [
            imports,
            *_definition_cells(record_symbols),
            parameters,
            _cell(
                "code",
                "call_options = {name: options[name] for name in inspect.signature(oai_extract_records).parameters if name in options}\n"
                "df_records, df_page_errors, df_records_preview = oai_extract_records(**call_options)\n"
                "assert df_records[\"record_id\"].notna().all()\n"
                "assert not df_records[\"record_id\"].duplicated().any()\n"
                "{\"records\": len(df_records), \"page_errors\": len(df_page_errors), \"sources\": df_records[\"_source_key\"].value_counts().to_dict()}\n",
            ),
            _cell("code", "display(df_records_preview)\ndisplay(df_page_errors)\n"),
        ],
    )

    recovery_symbols = [
        "get_oai_response",
        "OAI_NAMESPACES",
        "OAI_RECORD_COLUMNS",
        "OAI_PROVENANCE_COLUMNS",
        "add_oai_provenance",
        "parse_oai_record",
        "oai_extract_records_by_identifiers",
    ]
    _write_notebook(
        extract_dir / "oai_extract_records_by_identifiers.ipynb",
        "Recuperación individual de registros OAI",
        "Ejecuta `GetRecord` sobre los faltantes en modo acotado y audita cada error sin escribir datasets.",
        [
            imports,
            *_definition_cells(recovery_symbols),
            parameters,
            _cell(
                "code",
                "df_missing = catalog.load(\"raw/oai/missing_record_identifiers#parquet\")\n"
                "df_missing.head()\n",
            ),
            _cell(
                "code",
                "call_options = {name: options[name] for name in inspect.signature(oai_extract_records_by_identifiers).parameters if name in options}\n"
                "df_recovered, df_record_errors, df_recovered_preview = oai_extract_records_by_identifiers(df_ids=df_missing, **call_options)\n"
                "assert not df_recovered[\"record_id\"].duplicated().any()\n"
                "{\"requested\": min(len(df_missing), options[\"dev_identifier_limit\"]), \"recovered\": len(df_recovered), \"errors\": len(df_record_errors)}\n",
            ),
            _cell("code", "display(df_recovered_preview)\ndisplay(df_record_errors)\n"),
        ],
    )

    _write_notebook(
        extract_dir / "oai_reconcile_records.ipynb",
        "Reconciliación de la cosecha OAI",
        "Compara manifiesto y registros activos, y prueba la consolidación de la cosecha masiva con las recuperaciones individuales.",
        [
            imports,
            *_definition_cells(
                ["oai_find_missing_record_identifiers", "oai_merge_harvested_records"]
            ),
            _cell(
                "code",
                "df_identifiers = catalog.load(\"raw/oai/identifiers#parquet\")\n"
                "df_records = catalog.load(\"raw/oai/records#parquet\")\n"
                "df_recovered = catalog.load(\"raw/oai/records_recovered#parquet\")\n",
            ),
            _cell(
                "code",
                "df_missing = oai_find_missing_record_identifiers(df_identifiers, df_records)\n"
                "df_consolidated, df_consolidated_preview = oai_merge_harvested_records(df_records, df_recovered)\n"
                "assert not df_consolidated[\"record_id\"].duplicated().any()\n"
                "{\"missing_against_current_snapshot\": len(df_missing), \"consolidated_records\": len(df_consolidated)}\n",
            ),
            _cell("code", "display(df_missing.head(20))\ndisplay(df_consolidated_preview)\n"),
        ],
    )


if __name__ == "__main__":
    main()
