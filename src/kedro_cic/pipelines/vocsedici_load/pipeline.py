"""Pipeline definition for `vocsedici_load`."""

from kedro.pipeline import Pipeline, node

from .nodes import load_vocsedici_tables


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="legacy_load_vocsedici_tables",
                func=load_vocsedici_tables,
                inputs=[
                    "raw/voc/node_legacy#parquet",
                    "raw/voc/node_field_data_legacy#parquet",
                    "raw/voc/paragraphs_item_legacy#parquet",
                    "raw/voc/paragraphs_item_field_data_legacy#parquet",
                    "raw/voc/paragraph__field_persona_id_legacy#parquet",
                    "raw/voc/paragraph__field_institucion_legacy#parquet",
                    "raw/voc/paragraph__field_fecha_inicio_legacy#parquet",
                    "raw/voc/paragraph__field_fecha_fin_legacy#parquet",
                    "raw/voc/node__field_nombre_legacy#parquet",
                    "raw/voc/node__field_apellido_legacy#parquet",
                    "raw/voc/node__field_orcid_legacy#parquet",
                    "raw/voc/node__field_mail_legacy#parquet",
                    "raw/voc/node__field_dni_legacy#parquet",
                    "raw/voc/node__field_cuit_legacy#parquet",
                    "raw/voc/node__field_telefono_legacy#parquet",
                    "raw/voc/node__field_direcci_n_legacy#parquet",
                    "raw/voc/node__field_google_scholar_legacy#parquet",
                    "raw/voc/node__field_researchgate_legacy#parquet",
                    "raw/voc/node__field_old_id_legacy#parquet",
                    "raw/voc/node__field_filiacion_legacy#parquet",
                    "raw/voc/node__field_nombre_institucion_legacy#parquet",
                    "raw/voc/node__field_nombre_institucion_variant_legacy#parquet",
                    "raw/voc/node__field_abreviatura_legacy#parquet",
                    "raw/voc/node__field_id_pidu_legacy#parquet",
                    "raw/voc/node__field_id_termino_legacy#parquet",
                    "raw/voc/node__field_padre_legacy#parquet",
                ],
                outputs=[
                    "ldg/vocsedici/node_legacy",
                    "ldg/vocsedici/node_field_data_legacy",
                    "ldg/vocsedici/paragraphs_item_legacy",
                    "ldg/vocsedici/paragraphs_item_field_data_legacy",
                    "ldg/vocsedici/paragraph__field_persona_id_legacy",
                    "ldg/vocsedici/paragraph__field_institucion_legacy",
                    "ldg/vocsedici/paragraph__field_fecha_inicio_legacy",
                    "ldg/vocsedici/paragraph__field_fecha_fin_legacy",
                    "ldg/vocsedici/node__field_nombre_legacy",
                    "ldg/vocsedici/node__field_apellido_legacy",
                    "ldg/vocsedici/node__field_orcid_legacy",
                    "ldg/vocsedici/node__field_mail_legacy",
                    "ldg/vocsedici/node__field_dni_legacy",
                    "ldg/vocsedici/node__field_cuit_legacy",
                    "ldg/vocsedici/node__field_telefono_legacy",
                    "ldg/vocsedici/node__field_direcci_n_legacy",
                    "ldg/vocsedici/node__field_google_scholar_legacy",
                    "ldg/vocsedici/node__field_researchgate_legacy",
                    "ldg/vocsedici/node__field_old_id_legacy",
                    "ldg/vocsedici/node__field_filiacion_legacy",
                    "ldg/vocsedici/node__field_nombre_institucion_legacy",
                    "ldg/vocsedici/node__field_nombre_institucion_variant_legacy",
                    "ldg/vocsedici/node__field_abreviatura_legacy",
                    "ldg/vocsedici/node__field_id_pidu_legacy",
                    "ldg/vocsedici/node__field_id_termino_legacy",
                    "ldg/vocsedici/node__field_padre_legacy",
                ],
            )
        ],
        tags="vocsedici_load",
    )
