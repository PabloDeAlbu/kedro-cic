from kedro.pipeline import Node, Pipeline
from .nodes import (
    oai_load_identifiers,
    oai_load_item,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        Node(
            name="oai_load_identifiers",
            func=oai_load_identifiers,
            inputs="raw/oai/identifiers#parquet",
            outputs=[
                "ldg/oai/identifiers",
                "ldg/oai/map_identifier_set",
            ],
        ),
        Node(
            name="oai_load_item",
            func=oai_load_item,
            inputs=[
                "raw/oai/item#parquet"
            ],
            outputs=[
                "ldg/oai/item",
                "ldg/oai/map_item_creator",
                "ldg/oai/map_item_type",
                "ldg/oai/map_item_identifier",
                "ldg/oai/map_item_language",
                "ldg/oai/map_item_subject",
                "ldg/oai/map_item_publisher",
                "ldg/oai/map_item_relation",
                "ldg/oai/map_item_right",
            ],
        ),
    ], tags="oai_load")
