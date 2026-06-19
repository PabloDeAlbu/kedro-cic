from kedro.pipeline import Pipeline, node

from .nodes import extract_vocsedici_tables


_INPUT_TABLES = [
    "voc_mariadb/node",
    "voc_mariadb/node_field_data",
    "voc_mariadb/paragraphs_item",
    "voc_mariadb/paragraphs_item_field_data",
    "voc_mariadb/paragraph__field_persona_id",
    "voc_mariadb/paragraph__field_institucion",
    "voc_mariadb/paragraph__field_fecha_inicio",
    "voc_mariadb/paragraph__field_fecha_fin",
    "voc_mariadb/node__field_nombre",
    "voc_mariadb/node__field_apellido",
    "voc_mariadb/node__field_orcid",
    "voc_mariadb/node__field_mail",
    "voc_mariadb/node__field_dni",
    "voc_mariadb/node__field_cuit",
    "voc_mariadb/node__field_telefono",
    "voc_mariadb/node__field_direcci_n",
    "voc_mariadb/node__field_google_scholar",
    "voc_mariadb/node__field_researchgate",
    "voc_mariadb/node__field_old_id",
    "voc_mariadb/node__field_filiacion",
    "voc_mariadb/node__field_nombre_institucion",
    "voc_mariadb/node__field_nombre_institucion_variant",
    "voc_mariadb/node__field_abreviatura",
    "voc_mariadb/node__field_id_pidu",
    "voc_mariadb/node__field_id_termino",
    "voc_mariadb/node__field_padre",
]

_OUTPUT_TABLES = [
    "raw/voc/node#parquet",
    "raw/voc/node_field_data#parquet",
    "raw/voc/paragraphs_item#parquet",
    "raw/voc/paragraphs_item_field_data#parquet",
    "raw/voc/paragraph__field_persona_id#parquet",
    "raw/voc/paragraph__field_institucion#parquet",
    "raw/voc/paragraph__field_fecha_inicio#parquet",
    "raw/voc/paragraph__field_fecha_fin#parquet",
    "raw/voc/node__field_nombre#parquet",
    "raw/voc/node__field_apellido#parquet",
    "raw/voc/node__field_orcid#parquet",
    "raw/voc/node__field_mail#parquet",
    "raw/voc/node__field_dni#parquet",
    "raw/voc/node__field_cuit#parquet",
    "raw/voc/node__field_telefono#parquet",
    "raw/voc/node__field_direcci_n#parquet",
    "raw/voc/node__field_google_scholar#parquet",
    "raw/voc/node__field_researchgate#parquet",
    "raw/voc/node__field_old_id#parquet",
    "raw/voc/node__field_filiacion#parquet",
    "raw/voc/node__field_nombre_institucion#parquet",
    "raw/voc/node__field_nombre_institucion_variant#parquet",
    "raw/voc/node__field_abreviatura#parquet",
    "raw/voc/node__field_id_pidu#parquet",
    "raw/voc/node__field_id_termino#parquet",
    "raw/voc/node__field_padre#parquet",
]


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="extract_vocsedici_tables",
                func=extract_vocsedici_tables,
                inputs=[
                    "params:extract_vocsedici_options.tables",
                    "params:extract_vocsedici_options.source_label",
                    "params:extract_vocsedici_options.env",
                    "params:extract_vocsedici_options.filter_param",
                    "params:extract_vocsedici_options.filter_value",
                    *_INPUT_TABLES,
                ],
                outputs=_OUTPUT_TABLES,
            )
        ],
        tags="extract_vocsedici",
    )
