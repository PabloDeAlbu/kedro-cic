import pandas as pd

from kedro_cic.pipelines.vocsedici_extract.nodes import vocsedici_extract_tables


def test_vocsedici_extract_tables_adds_extract_metadata():
    base_df = pd.DataFrame({"nid": [1]})

    outputs = vocsedici_extract_tables(
        [
            "node",
            "node_field_data",
            "node__field_nombre",
            "node__field_apellido",
            "node__field_orcid",
            "node__field_mail",
            "node__field_dni",
            "node__field_cuit",
            "node__field_telefono",
            "node__field_direcci_n",
            "node__field_google_scholar",
            "node__field_researchgate",
            "node__field_old_id",
            "node__field_filiacion",
            "node__field_nombre_institucion",
            "node__field_nombre_institucion_variant",
            "node__field_abreviatura",
            "node__field_id_pidu",
            "node__field_id_termino",
            "node__field_padre",
        ],
        "voc_sedici",
        "dev",
        "",
        None,
        *([base_df] * 20),
    )

    extracted_node = outputs[0]

    assert extracted_node.loc[0, "_source_system"] == "voc"
    assert extracted_node.loc[0, "_source_table"] == "node"
    assert extracted_node.loc[0, "_source_label"] == "voc_sedici"
    assert extracted_node.loc[0, "_extract_env"] == "dev"
    assert pd.isna(extracted_node.loc[0, "_filter_param"])
    assert pd.isna(extracted_node.loc[0, "_filter_value"])
    assert pd.notna(extracted_node.loc[0, "_extract_datetime"])
