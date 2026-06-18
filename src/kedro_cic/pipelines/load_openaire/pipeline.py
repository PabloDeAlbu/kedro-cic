from kedro.pipeline import Pipeline, node

from .nodes import (
    load_openaire_researchproduct,
    load_openaire_researchproduct_authors,
    load_openaire_researchproduct_collectedfrom,
    load_openaire_researchproduct_contributors,
    load_openaire_researchproduct_instances,
    load_openaire_researchproduct_organizations,
    load_openaire_researchproduct_originalid,
    load_openaire_researchproduct_pids,
    load_openaire_researchproduct_sources,
    load_openaire_researchproduct_subjects,
)


RAW_RESEARCHPRODUCT = "raw/openaire/researchproduct/parquet/researchproduct"


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="load_openaire_researchproduct",
                func=load_openaire_researchproduct,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/researchproduct",
            ),
            node(
                name="load_openaire_researchproduct_authors",
                func=load_openaire_researchproduct_authors,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_author",
            ),
            node(
                name="load_openaire_researchproduct_collectedfrom",
                func=load_openaire_researchproduct_collectedfrom,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_collectedfrom",
            ),
            node(
                name="load_openaire_researchproduct_contributors",
                func=load_openaire_researchproduct_contributors,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_contributor",
            ),
            node(
                name="load_openaire_researchproduct_instances",
                func=load_openaire_researchproduct_instances,
                inputs=RAW_RESEARCHPRODUCT,
                outputs=[
                    "ldg/openaire/map_researchproduct_instance",
                    "ldg/openaire/map_researchproduct_alternateidentifier",
                ],
            ),
            node(
                name="load_openaire_researchproduct_organizations",
                func=load_openaire_researchproduct_organizations,
                inputs=RAW_RESEARCHPRODUCT,
                outputs=[
                    "ldg/openaire/organization",
                    "ldg/openaire/map_researchproduct_organization",
                    "ldg/openaire/map_organization_pid",
                ],
            ),
            node(
                name="load_openaire_researchproduct_originalid",
                func=load_openaire_researchproduct_originalid,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_originalid",
            ),
            node(
                name="load_openaire_researchproduct_pids",
                func=load_openaire_researchproduct_pids,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_pid",
            ),
            node(
                name="load_openaire_researchproduct_sources",
                func=load_openaire_researchproduct_sources,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_source",
            ),
            node(
                name="load_openaire_researchproduct_subjects",
                func=load_openaire_researchproduct_subjects,
                inputs=RAW_RESEARCHPRODUCT,
                outputs="ldg/openaire/map_researchproduct_subject",
            ),
        ],
        tags="load_openaire",
    )
