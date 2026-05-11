from kedro.pipeline import Pipeline, node

from .nodes import vocsedici_extract_tables


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="vocsedici_extract_tables",
                func=vocsedici_extract_tables,
                inputs=[
                    "params:vocsedici_extract_options.tables",
                    "params:vocsedici_extract_options.source_label",
                    "params:vocsedici_extract_options.env",
                    "params:vocsedici_extract_options.filter_param",
                    "params:vocsedici_extract_options.filter_value",
                    "voc_mariadb/node",
                    "voc_mariadb/node_field_data",
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
                ],
                outputs=[
                    "raw/voc/node#parquet",
                    "raw/voc/node_field_data#parquet",
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
                ],
            )
        ],
        tags="vocsedici_extract",
    )
