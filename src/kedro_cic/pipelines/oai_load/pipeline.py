from kedro.pipeline import Node, Pipeline
from .nodes import (
    oai_load_identifiers,
    oai_load_records,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
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
                name="oai_load_records",
                func=oai_load_records,
                inputs=[
                    "raw/oai/records#parquet",
                    "params:oai_load_options.env",
                ],
                outputs=[
                    "ldg/oai/records",
                    "ldg/oai/map_record_creator",
                    "ldg/oai/map_record_description",
                    "ldg/oai/map_record_type",
                    "ldg/oai/map_record_identifier",
                    "ldg/oai/map_record_language",
                    "ldg/oai/map_record_subject",
                    "ldg/oai/map_record_publisher",
                    "ldg/oai/map_record_relation",
                    "ldg/oai/map_record_right",
                    "ldg/oai/map_record_format",
                    "ldg/oai/map_record_set",
                ],
            ),
        ],
        tags="oai_load",
    )
