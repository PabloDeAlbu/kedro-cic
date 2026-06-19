from kedro.pipeline import Pipeline, node

from .nodes import load_dspacedb5_tables


_INPUT_TABLES = [
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

_OUTPUT_TABLES = [
    "ldg/dspacedb5/bitstream",
    "ldg/dspacedb5/bundle2bitstream",
    "ldg/dspacedb5/collection2item",
    "ldg/dspacedb5/collection",
    "ldg/dspacedb5/community2collection",
    "ldg/dspacedb5/community2community",
    "ldg/dspacedb5/community",
    "ldg/dspacedb5/handle",
    "ldg/dspacedb5/item2bundle",
    "ldg/dspacedb5/item",
    "ldg/dspacedb5/metadatafieldregistry",
    "ldg/dspacedb5/metadataschemaregistry",
    "ldg/dspacedb5/metadatavalue",
]


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="load_dspacedb5_tables",
                func=load_dspacedb5_tables,
                inputs=_INPUT_TABLES,
                outputs=_OUTPUT_TABLES,
            )
        ],
        tags="load_dspacedb5",
    )
