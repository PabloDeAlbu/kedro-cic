from kedro.pipeline import Pipeline, node

from .nodes import extract_openaire_researchproduct


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="extract_openaire_researchproduct",
                func=extract_openaire_researchproduct,
                inputs=[
                    "params:extract_openaire_options.filter_param",
                    "params:extract_openaire_options.ror_filter_value",
                    "params:extract_openaire_options.access_token",
                    "params:extract_openaire_options.refresh_token",
                    "params:extract_openaire_options.env",
                ],
                outputs=[
                    "raw/openaire/researchproduct/parquet/researchproduct",
                    "raw/openaire/researchproduct/parquet/researchproduct_dev",
                ],
            )
        ],
        tags="extract_openaire",
    )
