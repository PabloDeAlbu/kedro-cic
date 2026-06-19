from kedro.pipeline import Pipeline, node

from .nodes import extract_dspacedb5_tables


_INPUT_TABLES = [
    "dspacedb5/public/bitstream",
    "dspacedb5/public/bundle2bitstream",
    "dspacedb5/public/collection2item",
    "dspacedb5/public/collection",
    "dspacedb5/public/community2collection",
    "dspacedb5/public/community2community",
    "dspacedb5/public/community",
    "dspacedb5/public/handle",
    "dspacedb5/public/item2bundle",
    "dspacedb5/public/item",
    "dspacedb5/public/metadatafieldregistry",
    "dspacedb5/public/metadataschemaregistry",
    "dspacedb5/public/metadatavalue",
]

_OUTPUT_TABLES = [
    "raw/dspacedb5/bitstream#parquet",
    "raw/dspacedb5/bundle2bitstream#parquet",
    "raw/dspacedb5/collection2item#parquet",
    "raw/dspacedb5/collection#parquet",
    "raw/dspacedb5/community2collection#parquet",
    "raw/dspacedb5/community2community#parquet",
    "raw/dspacedb5/community#parquet",
    "raw/dspacedb5/handle#parquet",
    "raw/dspacedb5/item2bundle#parquet",
    "raw/dspacedb5/item#parquet",
    "raw/dspacedb5/metadatafieldregistry#parquet",
    "raw/dspacedb5/metadataschemaregistry#parquet",
    "raw/dspacedb5/metadatavalue#parquet",
]


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="extract_dspacedb5_tables",
                func=extract_dspacedb5_tables,
                inputs=[
                    "params:extract_dspacedb5_options.tables",
                    "params:extract_dspacedb5_options.source_label",
                    "params:extract_dspacedb5_options.institution_ror",
                    "params:extract_dspacedb5_options.env",
                    "params:extract_dspacedb5_options.filter_param",
                    "params:extract_dspacedb5_options.filter_value",
                    *_INPUT_TABLES,
                ],
                outputs=_OUTPUT_TABLES,
            )
        ],
        tags="extract_dspacedb5",
    )
