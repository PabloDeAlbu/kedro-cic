from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd


def _load_nodes_module():
    nodes_path = Path(__file__).resolve().parents[3] / "src" / "kedro_cic" / "pipelines" / "openalex_load" / "nodes.py"
    spec = spec_from_file_location("openalex_load_nodes", nodes_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_openalex_load_author_expands_parsed_longest_name():
    nodes = _load_nodes_module()
    df = pd.DataFrame(
        [
            {
                "id": "https://openalex.org/A1",
                "orcid": "https://orcid.org/0000-0000-0000-0001",
                "display_name": "Ada Lovelace",
                "display_name_alternatives": ["A. Lovelace"],
                "works_count": 10,
                "cited_by_count": 20,
                "summary_stats": {"h_index": 3},
                "ids": {"openalex": "https://openalex.org/A1"},
                "affiliations": [],
                "last_known_institutions": [],
                "topics": [],
                "topic_share": [],
                "x_concepts": [],
                "counts_by_year": [],
                "longest_name": "Augusta Ada Lovelace",
                "parsed_longest_name": {
                    "first": "augusta",
                    "last": "lovelace",
                    "middle": "ada",
                    "nickname": "",
                    "suffix": "",
                },
                "block_key": "a lovelace",
                "works_api_url": "https://api.openalex.org/works?filter=author.id:A1",
                "updated_date": "2026-03-08T12:20:35",
                "created_date": "2016-06-24T00:00:00",
            }
        ]
    )

    result = nodes.openalex_load_author(df)

    assert "parsed_longest_name" not in result.columns
    assert result.loc[0, "parsed_longest_name.first"] == "augusta"
    assert result.loc[0, "parsed_longest_name.last"] == "lovelace"
    assert result.loc[0, "parsed_longest_name.middle"] == "ada"
