from functools import partial, update_wrapper

from kedro.pipeline import Pipeline, node

from .nodes import clean_extract_openalex_institution, extract_openalex


extract_openalex_institution = update_wrapper(
    partial(extract_openalex, cleaner=clean_extract_openalex_institution),
    extract_openalex,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="extract_openalex_work",
                func=extract_openalex,
                inputs=[
                    "params:extract_openalex_options.institution_ror",
                    "params:extract_openalex_options.work_filter",
                    "params:extract_openalex_options.work_endpoint",
                    "params:extract_openalex_options.env",
                    "params:extract_openalex_options.work_query_options",
                ],
                outputs=[
                    "raw/openalex/work/parquet/work",
                    "raw/openalex/work/parquet/work_dev",
                ],
            ),
            node(
                name="extract_openalex_author",
                func=extract_openalex,
                inputs=[
                    "params:extract_openalex_options.institution_ror",
                    "params:extract_openalex_options.author_filter",
                    "params:extract_openalex_options.author_endpoint",
                    "params:extract_openalex_options.env",
                    "params:extract_openalex_options.author_query_options",
                ],
                outputs=[
                    "raw/openalex/author/parquet/author",
                    "raw/openalex/author/parquet/author_dev",
                ],
            ),
            node(
                name="extract_openalex_institution",
                func=extract_openalex_institution,
                inputs=[
                    "params:extract_openalex_options.institution_ror",
                    "params:extract_openalex_options.institution_filter",
                    "params:extract_openalex_options.institution_endpoint",
                    "params:extract_openalex_options.env",
                    "params:extract_openalex_options.institution_query_options",
                ],
                outputs=[
                    "raw/openalex/institution/parquet/institution",
                    "raw/openalex/institution/parquet/institution_dev",
                ],
            ),
            node(
                name="extract_openalex_funder",
                func=extract_openalex,
                inputs=[
                    "params:extract_openalex_options.institution_ror",
                    "params:extract_openalex_options.funder_filter",
                    "params:extract_openalex_options.funder_endpoint",
                    "params:extract_openalex_options.env",
                    "params:extract_openalex_options.funder_query_options",
                ],
                outputs=[
                    "raw/openalex/funder/parquet/funder",
                    "raw/openalex/funder/parquet/funder_dev",
                ],
            ),
        ],
        tags="extract_openalex",
    )
