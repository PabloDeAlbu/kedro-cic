from kedro.pipeline import Pipeline, node, pipeline

from .nodes import load_google_scholar_author


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                name="load_google_scholar_author",
                func=load_google_scholar_author,
                inputs="raw/google_scholar/html",
                outputs="ldg/google_scholar/author",
            ),
        ],
        tags="load_google_scholar",
    )
