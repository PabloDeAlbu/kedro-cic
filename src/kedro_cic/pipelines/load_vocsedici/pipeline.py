from kedro.pipeline import Pipeline, node

from .nodes import load_vocsedici_tables


_INPUT_TABLES = [
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

_OUTPUT_TABLES = [
    "ldg/vocsedici/node",
    "ldg/vocsedici/node_field_data",
    "ldg/vocsedici/paragraphs_item",
    "ldg/vocsedici/paragraphs_item_field_data",
    "ldg/vocsedici/paragraph__field_persona_id",
    "ldg/vocsedici/paragraph__field_institucion",
    "ldg/vocsedici/paragraph__field_fecha_inicio",
    "ldg/vocsedici/paragraph__field_fecha_fin",
    "ldg/vocsedici/node__field_nombre",
    "ldg/vocsedici/node__field_apellido",
    "ldg/vocsedici/node__field_orcid",
    "ldg/vocsedici/node__field_mail",
    "ldg/vocsedici/node__field_dni",
    "ldg/vocsedici/node__field_cuit",
    "ldg/vocsedici/node__field_telefono",
    "ldg/vocsedici/node__field_direcci_n",
    "ldg/vocsedici/node__field_google_scholar",
    "ldg/vocsedici/node__field_researchgate",
    "ldg/vocsedici/node__field_old_id",
    "ldg/vocsedici/node__field_filiacion",
    "ldg/vocsedici/node__field_nombre_institucion",
    "ldg/vocsedici/node__field_nombre_institucion_variant",
    "ldg/vocsedici/node__field_abreviatura",
    "ldg/vocsedici/node__field_id_pidu",
    "ldg/vocsedici/node__field_id_termino",
    "ldg/vocsedici/node__field_padre",
]


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="load_vocsedici_tables",
                func=load_vocsedici_tables,
                inputs=_INPUT_TABLES,
                outputs=_OUTPUT_TABLES,
            )
        ],
        tags="load_vocsedici",
    )
