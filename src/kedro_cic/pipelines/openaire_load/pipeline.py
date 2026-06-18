from kedro.pipeline import Node, Pipeline
from .nodes import (
    openaire_load_researchproduct,
    openaire_load_researchproduct_authors,
    openaire_load_researchproduct_collectedfrom,
    openaire_load_researchproduct_contributors,
    # openaire_load_researchproduct_descriptions,
    openaire_load_researchproduct_instances,
    openaire_load_researchproduct_organizations,
    openaire_load_researchproduct_originalid,
    openaire_load_researchproduct_pids,
    openaire_load_researchproduct_sources,
    openaire_load_researchproduct_subjects,
)

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        Node(
            name="openaire_load_researchproduct",
            func=openaire_load_researchproduct,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/researchproduct"
        ),
        Node(
            name="openaire_load_researchproduct_authors",
            func=openaire_load_researchproduct_authors,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_author",
        ),
        Node(
            name="openaire_load_researchproduct_collectedfrom",
            func=openaire_load_researchproduct_collectedfrom,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_collectedfrom"
        ),
        Node(
            name="openaire_load_researchproduct_contributors",
            func=openaire_load_researchproduct_contributors,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_contributor"
        ),
        # node(
        #     name="openaire_load_researchproduct_descriptions",
        #     func=openaire_load_researchproduct_descriptions,
        #     inputs="raw/openaire/researchproduct#parquet",
        #     outputs="ldg/legacy_openaire/researchproduct_descriptions"
        # ),
        Node(
            name="openaire_load_researchproduct_instances",
            func=openaire_load_researchproduct_instances,
            inputs="raw/openaire/researchproduct#parquet",
            outputs=[
                "ldg/legacy_openaire/map_researchproduct_instance",
                "ldg/legacy_openaire/map_researchproduct_alternateidentifier",
            ]
        ),
        Node(
            name="openaire_load_researchproduct_organizations",
            func=openaire_load_researchproduct_organizations,
            inputs="raw/openaire/researchproduct#parquet",
            outputs=[
                "ldg/legacy_openaire/organization",
                "ldg/legacy_openaire/map_researchproduct_organization",
                "ldg/legacy_openaire/map_organization_pid",
            ]
        ),
        Node(
            name="openaire_load_researchproduct_originalid",
            func=openaire_load_researchproduct_originalid,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_originalid"
        ),
        Node(
            name="openaire_load_researchproduct_pids",
            func=openaire_load_researchproduct_pids,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_pid"
        ),
        Node(
            name="openaire_load_researchproduct_sources",
            func=openaire_load_researchproduct_sources,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_source"
        ),
        Node(
            name="openaire_load_researchproduct_subjects",
            func=openaire_load_researchproduct_subjects,
            inputs="raw/openaire/researchproduct#parquet",
            outputs="ldg/legacy_openaire/map_researchproduct_subject"
        ),
    ], tags="openaire_load")
