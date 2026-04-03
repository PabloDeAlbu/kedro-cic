from importlib.util import module_from_spec, spec_from_file_location
import json
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


def test_openalex_load_work_drops_residual_primary_location_source_column():
    nodes = _load_nodes_module()
    df = pd.DataFrame(
        [
            {
                "id": "https://openalex.org/W1",
                "source_system": "openalex",
                "entity_type": "work",
                "extract_datetime": "2026-03-08 12:20:35",
                "extract_date": "2026-03-08",
                "institution_ror": "https://ror.org/01tjs6929",
                "extract_filters": json.dumps(
                    {
                        "institutions.ror": "https://ror.org/01tjs6929",
                        "per_page": 200,
                        "type": "article",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "extract_filter_label": "institutions.ror:https://ror.org/01tjs6929",
                "endpoint": "works",
                "api_path": "/works",
                "_filter_param": "institutions.ror",
                "_filter_value": "https://ror.org/01tjs6929",
                "_extract_datetime": "2026-03-08 12:20:35",
                "title": "Test work",
                "display_name": "Test work",
                "publication_year": 2024,
                "publication_date": "2024-01-01",
                "ids": {
                    "doi": "https://doi.org/10.1234/example",
                    "openalex": "https://openalex.org/W1",
                },
                "language": "en",
                "primary_location": {
                    "id": "doi:10.1234/example",
                    "is_accepted": True,
                    "is_oa": False,
                    "is_published": True,
                    "landing_page_url": "https://doi.org/10.1234/example",
                    "license": None,
                    "license_id": None,
                    "pdf_url": None,
                    "raw_source_name": "Example Journal",
                    "raw_type": "journal-article",
                    "source": None,
                    "version": "publishedVersion",
                },
                "type": "article",
                "type_crossref": None,
                "open_access": {
                    "any_repository_has_fulltext": False,
                    "is_oa": False,
                    "oa_status": "closed",
                    "oa_url": None,
                },
                "countries_distinct_count": 1,
                "institutions_distinct_count": 1,
                "apc_list": None,
                "apc_paid": None,
                "fwci": 1.0,
                "has_fulltext": False,
                "fulltext_origin": None,
                "cited_by_count": 0,
                "citation_normalized_percentile": {
                    "is_in_top_10_percent": False,
                    "is_in_top_1_percent": False,
                    "value": 0.0,
                },
                "cited_by_percentile_year": {"max": 0, "min": 0},
                "biblio": {
                    "first_page": "1",
                    "issue": "1",
                    "last_page": "2",
                    "volume": "1",
                },
                "is_retracted": False,
                "is_paratext": False,
                "primary_topic": {
                    "display_name": "Topic",
                    "id": "https://openalex.org/T1",
                    "score": 0.5,
                    "domain": {
                        "display_name": "Domain",
                        "id": "https://openalex.org/domains/1",
                    },
                    "field": {
                        "display_name": "Field",
                        "id": "https://openalex.org/fields/1",
                    },
                    "subfield": {
                        "display_name": "Subfield",
                        "id": "https://openalex.org/subfields/1",
                    },
                },
                "locations_count": 1,
                "best_oa_location": None,
                "referenced_works_count": 0,
                "cited_by_api_url": None,
                "updated_date": "2026-03-08T12:20:35",
                "created_date": "2016-06-24T00:00:00",
            }
        ]
    )

    result = nodes.openalex_load_work(df)

    assert "primary_location.source" not in result.columns
    assert result.loc[0, "source_system"] == "openalex"
    assert result.loc[0, "entity_type"] == "work"
    assert result.loc[0, "institution_ror"] == "https://ror.org/01tjs6929"
    assert result.loc[0, "extract_filters"] == json.dumps(
        {
            "institutions.ror": "https://ror.org/01tjs6929",
            "per_page": 200,
            "type": "article",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    assert pd.notna(result.loc[0, "extract_datetime"])
    assert pd.notna(result.loc[0, "_load_datetime"])
