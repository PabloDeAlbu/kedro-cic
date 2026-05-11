import pandas as pd

from kedro_cic.pipelines.vocsedici_load.nodes import load_vocsedici_tables


def test_load_vocsedici_tables_preserves_extract_metadata_and_adds_load_datetime():
    base_df = pd.DataFrame(
        {
            "nid": [1],
            "_source_system": ["voc"],
            "_source_table": ["node"],
            "_extract_datetime": ["2026-05-11 12:00:00"],
            "_extract_date": ["2026-05-11"],
            "_source_label": ["voc_sedici"],
            "_extract_env": ["dev"],
            "_filter_param": [pd.NA],
            "_filter_value": [pd.NA],
        }
    )

    outputs = load_vocsedici_tables(*([base_df] * 20))
    loaded_node = outputs[0]

    assert loaded_node.loc[0, "_source_system"] == "voc"
    assert loaded_node.loc[0, "_source_table"] == "node"
    assert pd.notna(loaded_node.loc[0, "_extract_datetime"])
    assert pd.notna(loaded_node.loc[0, "_load_datetime"])
