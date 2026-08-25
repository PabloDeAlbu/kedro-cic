import ast
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
NOTEBOOK_ROOT = PROJECT_ROOT / "notebooks/sources/oai"

ACTIVE_NOTEBOOKS = {
    "01_extract/oai_extract_get_oai_response.ipynb",
    "01_extract/oai_extract_identifiers.ipynb",
    "01_extract/oai_extract_records.ipynb",
    "01_extract/oai_extract_records_by_identifiers.ipynb",
    "01_extract/oai_reconcile_records.ipynb",
    "02_load/oai_load_identifiers.ipynb",
    "02_load/oai_load_records.ipynb",
}


def _functions(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text())
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def _notebook_functions(path: Path) -> tuple[dict[str, str], dict]:
    notebook = json.loads(path.read_text())
    source = "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    tree = ast.parse(source)
    functions = {
        node.name: ast.dump(node, include_attributes=False)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    return functions, notebook


def test_only_active_oai_notebooks_are_versioned() -> None:
    notebooks = {
        str(path.relative_to(NOTEBOOK_ROOT))
        for path in NOTEBOOK_ROOT.glob("**/*.ipynb")
        if ".ipynb_checkpoints" not in path.parts
    }
    assert notebooks == ACTIVE_NOTEBOOKS


def test_oai_notebooks_are_clean_and_aligned_with_nodes() -> None:
    expected = {
        **_functions(PROJECT_ROOT / "src/kedro_cic/pipelines/oai_extract/nodes.py"),
        **_functions(PROJECT_ROOT / "src/kedro_cic/pipelines/oai_load/nodes.py"),
    }

    for relative_path in ACTIVE_NOTEBOOKS:
        functions, notebook = _notebook_functions(NOTEBOOK_ROOT / relative_path)
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell["execution_count"] is None
                assert cell["outputs"] == []
        for name, definition in functions.items():
            assert name in expected
            assert definition == expected[name]
