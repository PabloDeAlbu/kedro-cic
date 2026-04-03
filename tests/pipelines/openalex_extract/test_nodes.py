from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import pandas as pd


def _load_nodes_module():
    nodes_path = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "kedro_cic"
        / "pipelines"
        / "openalex_extract"
        / "nodes.py"
    )
    spec = spec_from_file_location("openalex_extract_nodes", nodes_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_add_openalex_extract_metadata_adds_traceability_fields():
    nodes = _load_nodes_module()
    df = pd.DataFrame([{"id": "https://openalex.org/W1"}])

    result = nodes._add_openalex_extract_metadata(
        df,
        institution_ror="https://ror.org/01tjs6929",
        filter_field="institutions.ror",
        entity="works",
        effective_filters={
            "institutions.ror": "https://ror.org/01tjs6929",
            "from_publication_date": "2024-01-01",
            "per_page": 200,
        },
    )

    assert result.loc[0, "source_system"] == "openalex"
    assert result.loc[0, "entity_type"] == "work"
    assert result.loc[0, "institution_ror"] == "https://ror.org/01tjs6929"
    assert result.loc[0, "endpoint"] == "works"
    assert result.loc[0, "api_path"] == "/works"
    assert result.loc[0, "_filter_param"] == "institutions.ror"
    assert result.loc[0, "_filter_value"] == "https://ror.org/01tjs6929"
    assert result.loc[0, "extract_filters"] == json.dumps(
        {
            "from_publication_date": "2024-01-01",
            "institutions.ror": "https://ror.org/01tjs6929",
            "per_page": 200,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert pd.notna(result.loc[0, "extract_datetime"])
    assert pd.notna(result.loc[0, "_extract_datetime"])
    assert pd.notna(result.loc[0, "extract_date"])
