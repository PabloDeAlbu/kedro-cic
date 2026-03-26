"""Pipeline definition for `dspace5_load`."""

from kedro.pipeline import Pipeline, node

from .nodes import load_dspace5


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="load_dspace5",
                func=load_dspace5,
                inputs=[
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
                outputs=[
                    "ldg/dspace5/bitstream",
                    "ldg/dspace5/bundle2bitstream",
                    "ldg/dspace5/collection2item",
                    "ldg/dspace5/collection",
                    "ldg/dspace5/community2collection",
                    "ldg/dspace5/community2community",
                    "ldg/dspace5/community",
                    "ldg/dspace5/handle",
                    "ldg/dspace5/item2bundle",
                    "ldg/dspace5/item",
                    "ldg/dspace5/metadatafieldregistry",
                    "ldg/dspace5/metadataschemaregistry",
                    "ldg/dspace5/metadatavalue",
                ],
            )
        ],
        tags="dspace5_load",
    )
