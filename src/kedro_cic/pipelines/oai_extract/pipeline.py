from kedro.pipeline import Node, Pipeline

from .nodes import (
    oai_extract_identifiers,
    oai_extract_records,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        Node(
            name="oai_extract_identifiers",
            func=oai_extract_identifiers,
            inputs=[
                "params:oai_extract_options.base_url",
                "params:oai_extract_options.context",
                "params:oai_extract_options.env",
                "params:oai_extract_options.source_key",
                "params:oai_extract_options.repository_identifier",
                "params:oai_extract_options.institution_ror",
                "params:oai_extract_options.metadata_prefix",
                "params:oai_extract_options.dev_page_limit",
                "params:oai_extract_options.initial_resumption_token",
                "params:oai_extract_options.page_limit",
            ],
            outputs=["raw/oai/identifiers#parquet", "raw/oai/identifiers_dev"],
        ),
        Node(
            name="oai_extract_records",
            func=oai_extract_records,
            inputs=[
                "params:oai_extract_options.base_url",
                "params:oai_extract_options.context",
                "params:oai_extract_options.env",
                "params:oai_extract_options.source_key",
                "params:oai_extract_options.repository_identifier",
                "params:oai_extract_options.institution_ror",
                "params:oai_extract_options.metadata_prefix",
                "params:oai_extract_options.dev_page_limit",
                "params:oai_extract_options.initial_resumption_token",
                "params:oai_extract_options.page_limit",
            ],
            outputs=["raw/oai/records#parquet" , "raw/oai/records_dev"]
        ),
    ], tags="oai_extract")
