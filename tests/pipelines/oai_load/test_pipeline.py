import pandas as pd
from kedro_cic.pipelines.oai_load.nodes import oai_load_identifiers, oai_load_records


def _raw_records() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "record_id": ["oai:repositorio.uca.edu.ar:1"],
            "col_id": ["col_1"],
            "title": ["Título"],
            "date_issued": ["2025"],
            "creators": [["Autora", "Autor"]],
            "description": [["Resumen"]],
            "types": [["article"]],
            "identifiers": [["https://repositorio.uca.edu.ar/handle/1"]],
            "languages": [["spa"]],
            "subjects": [[]],
            "publishers": [["UCA"]],
            "relations": [[]],
            "rights": [["openAccess"]],
            "formats": [["application/pdf"]],
            "set_id": [["col_1", "com_1"]],
            "_extract_datetime": [pd.Timestamp("2026-08-24T12:00:00Z")],
            "_context": ["request"],
            "_source_key": ["uca"],
            "_repository_identifier": ["repositorio.uca.edu.ar"],
            "_institution_ror": ["https://ror.org/0422kzb24"],
            "_base_url": ["https://repositorio.uca.edu.ar/oai"],
            "_metadata_prefix": ["oai_dc"],
        }
    )


def test_load_records_matches_extract_contract_and_explodes_values() -> None:
    outputs = oai_load_records(_raw_records(), env="dev")
    records, creators, descriptions = outputs[:3]
    subjects = outputs[6]
    sets = outputs[-1]

    assert len(records) == 1
    assert records.loc[0, "_source_key"] == "uca"
    assert records.loc[0, "_institution_ror"] == "https://ror.org/0422kzb24"
    assert "extract_datetime" in records.columns
    assert "load_datetime" in records.columns
    assert creators["creators"].tolist() == ["Autora", "Autor"]
    assert descriptions["description"].tolist() == ["Resumen"]
    assert subjects.empty
    assert sets["set_id"].tolist() == ["col_1", "com_1"]


def test_load_identifiers_preserves_manifest_and_provenance() -> None:
    raw = pd.DataFrame(
        {
            "record_id": ["oai:example:1", "oai:example:2"],
            "datestamp": ["2026-08-24", "2026-08-25"],
            "set_id": [["col_1"], []],
            "is_deleted": [False, True],
            "_extract_datetime": [pd.Timestamp("2026-08-25T10:00:00Z")] * 2,
            "_context": ["request"] * 2,
            "_source_key": ["example"] * 2,
            "_repository_identifier": ["example.edu"] * 2,
            "_institution_ror": ["https://ror.org/example"] * 2,
            "_base_url": ["https://example.edu/oai"] * 2,
            "_metadata_prefix": ["oai_dc"] * 2,
        }
    )

    identifiers, sets = oai_load_identifiers(raw)

    assert identifiers["is_deleted"].tolist() == [False, True]
    assert identifiers["_source_key"].unique().tolist() == ["example"]
    assert sets[["record_id", "set_id"]].values.tolist() == [
        ["oai:example:1", "col_1"]
    ]
