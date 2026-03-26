from kedro.pipeline import Node, Pipeline

from .nodes import dspace5_extract_tables


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            Node(
                name="dspace5_extract",
                func=dspace5_extract_tables,
                inputs=[
                    "params:dspace5_extract_options.tables",
                    "params:dspace5_extract_options.source_label",
                    "params:dspace5_extract_options.institution_ror",
                    "dspace5/public/bitstream",
                    "dspace5/public/bundle2bitstream",
                    "dspace5/public/collection2item",
                    "dspace5/public/collection",
                    "dspace5/public/community2collection",
                    "dspace5/public/community2community",
                    "dspace5/public/community",
                    "dspace5/public/handle",
                    "dspace5/public/item2bundle",
                    "dspace5/public/item",
                    "dspace5/public/metadatafieldregistry",
                    "dspace5/public/metadataschemaregistry",
                    "dspace5/public/metadatavalue",
                ],
                outputs=[
                    "raw/dspace5/bitstream#parquet",
                    "raw/dspace5/bundle2bitstream#parquet",
                    "raw/dspace5/collection2item#parquet",
                    "raw/dspace5/collection#parquet",
                    "raw/dspace5/community2collection#parquet",
                    "raw/dspace5/community2community#parquet",
                    "raw/dspace5/community#parquet",
                    "raw/dspace5/handle#parquet",
                    "raw/dspace5/item2bundle#parquet",
                    "raw/dspace5/item#parquet",
                    "raw/dspace5/metadatafieldregistry#parquet",
                    "raw/dspace5/metadataschemaregistry#parquet",
                    "raw/dspace5/metadatavalue#parquet",
                ],
            )
        ],
        tags="dspace5_extract",
    )
