from kedro.pipeline import Node, Pipeline

from .nodes import (
    oai_extract_identifiers,
    oai_extract_records,
    oai_extract_records_by_identifiers,
    oai_find_missing_record_identifiers,
    oai_merge_harvested_records,
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
                "params:oai_extract_options.date_windows",
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
                "params:oai_extract_options.date_windows",
            ],
            outputs=[
                "memory/oai/records_bulk",
                "raw/oai/record_page_errors#parquet",
                "memory/oai/records_bulk_preview",
            ]
        ),
        Node(
            name="oai_find_missing_record_identifiers",
            func=oai_find_missing_record_identifiers,
            inputs=[
                "raw/oai/identifiers#parquet",
                "memory/oai/records_bulk",
            ],
            outputs="raw/oai/missing_record_identifiers#parquet",
        ),
        Node(
            name="oai_extract_missing_records",
            func=oai_extract_records_by_identifiers,
            inputs=[
                "params:oai_extract_options.base_url",
                "params:oai_extract_options.context",
                "params:oai_extract_options.env",
                "raw/oai/missing_record_identifiers#parquet",
                "params:oai_extract_options.source_key",
                "params:oai_extract_options.repository_identifier",
                "params:oai_extract_options.institution_ror",
                "params:oai_extract_options.metadata_prefix",
                "params:oai_extract_options.dev_identifier_limit",
                "params:oai_extract_options.identifier_limit",
            ],
            outputs=[
                "raw/oai/records_recovered#parquet",
                "raw/oai/record_errors#parquet",
                "raw/oai/records_recovered_dev",
            ],
        ),
        Node(
            name="oai_merge_harvested_records",
            func=oai_merge_harvested_records,
            inputs=[
                "memory/oai/records_bulk",
                "raw/oai/records_recovered#parquet",
            ],
            outputs=["raw/oai/records#parquet", "raw/oai/records_dev"],
        ),
    ], tags="oai_extract")
