import pandas as pd

from kedro_cic.pipelines.extract_vocsedici.nodes import (
    VOCSEDICI_TABLES,
    extract_vocsedici_tables,
)


def test_extract_vocsedici_tables_adds_extract_metadata():
    base_df = pd.DataFrame({"nid": [1]})

    outputs = extract_vocsedici_tables(
        VOCSEDICI_TABLES,
        "voc_sedici",
        "dev",
        "",
        None,
        *([base_df] * len(VOCSEDICI_TABLES)),
    )

    extracted_node = outputs[0]

    assert extracted_node.loc[0, "_source_system"] == "voc"
    assert extracted_node.loc[0, "_source_table"] == "node"
    assert extracted_node.loc[0, "_source_label"] == "voc_sedici"
    assert extracted_node.loc[0, "_extract_env"] == "dev"
    assert pd.isna(extracted_node.loc[0, "_filter_param"])
    assert pd.isna(extracted_node.loc[0, "_filter_value"])
    assert pd.notna(extracted_node.loc[0, "_extract_datetime"])
