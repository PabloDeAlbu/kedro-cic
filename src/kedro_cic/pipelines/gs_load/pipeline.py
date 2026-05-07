from kedro.pipeline import Pipeline, node, pipeline

from .nodes import gs_load_author, gs_parse_author


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                name="gs_parse_author",
                func=gs_parse_author,
                inputs="raw/google-scholar/files",
                outputs="intermediate/google-scholar/author#parquet",
            ),
            node(
                name="gs_load_author",
                func=gs_load_author,
                inputs="intermediate/google-scholar/author#parquet",
                outputs="ldg/gs/author",
            ),
        ],
        tags="gs_load",
    )
