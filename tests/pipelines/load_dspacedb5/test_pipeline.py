import pandas as pd

from kedro_cic.pipelines.load_dspacedb5.nodes import load_dspacedb5_tables


def test_load_dspacedb5_tables_preserves_extract_metadata_and_adds_load_datetime():
    base_df = pd.DataFrame(
        {
            "id": [1],
            "uuid": ["abc"],
            "_source_system": ["dspacedb5"],
            "_source_table": ["bitstream"],
            "_extract_datetime": ["2026-03-26 10:00:00"],
            "_extract_date": ["2026-03-26"],
            "_source_label": ["sedici"],
            "_institution_ror": ["https://ror.org/01tjs6929"],
            "_extract_env": ["dev"],
            "_filter_param": [pd.NA],
            "_filter_value": [pd.NA],
        }
    )

    outputs = load_dspacedb5_tables(
        base_df,
        pd.DataFrame({"bundle_id": [1], "bitstream_id": [2]}),
        pd.DataFrame({"collection_id": [1], "item_id": [2]}),
        pd.DataFrame({"uuid": ["col-1"]}),
        pd.DataFrame({"collection_id": [1], "community_id": [2]}),
        pd.DataFrame({"parent_comm_id": [1], "child_comm_id": [2]}),
        pd.DataFrame({"uuid": ["com-1"]}),
        pd.DataFrame({"resource_id": [1]}),
        pd.DataFrame({"bundle_id": [1], "item_id": [2]}),
        pd.DataFrame({"uuid": ["item-1"]}),
        pd.DataFrame({"metadata_field_id": [1]}),
        pd.DataFrame({"schema_id": [1]}),
        pd.DataFrame({"dspace_object_id": [1]}),
    )

    loaded_bitstream = outputs[0]

    assert loaded_bitstream.loc[0, "_source_system"] == "dspacedb5"
    assert loaded_bitstream.loc[0, "_source_table"] == "bitstream"
    assert loaded_bitstream.loc[0, "_source_label"] == "sedici"
    assert loaded_bitstream.loc[0, "_institution_ror"] == "https://ror.org/01tjs6929"
    assert pd.notna(loaded_bitstream.loc[0, "_extract_datetime"])
    assert pd.notna(loaded_bitstream.loc[0, "_load_datetime"])
