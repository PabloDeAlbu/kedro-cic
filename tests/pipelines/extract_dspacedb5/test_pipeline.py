import pandas as pd

from kedro_cic.pipelines.extract_dspacedb5.nodes import (
    DSPACE_DB5_TABLES,
    extract_dspacedb5_tables,
)


def test_extract_dspacedb5_tables_adds_extract_metadata():
    base_df = pd.DataFrame({"item_id": [1]})

    outputs = extract_dspacedb5_tables(
        DSPACE_DB5_TABLES,
        "sedici",
        "https://ror.org/01tjs6929",
        "dev",
        "",
        None,
        *([base_df] * len(DSPACE_DB5_TABLES)),
    )

    extracted_bitstream = outputs[0]

    assert extracted_bitstream.loc[0, "_source_system"] == "dspacedb5"
    assert extracted_bitstream.loc[0, "_source_table"] == "bitstream"
    assert extracted_bitstream.loc[0, "_source_label"] == "sedici"
    assert extracted_bitstream.loc[0, "_institution_ror"] == "https://ror.org/01tjs6929"
    assert extracted_bitstream.loc[0, "_extract_env"] == "dev"
    assert pd.isna(extracted_bitstream.loc[0, "_filter_param"])
    assert pd.isna(extracted_bitstream.loc[0, "_filter_value"])
    assert pd.notna(extracted_bitstream.loc[0, "_extract_datetime"])
    assert pd.notna(extracted_bitstream.loc[0, "_extract_date"])
