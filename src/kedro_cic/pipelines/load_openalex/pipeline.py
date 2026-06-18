from kedro.pipeline import Pipeline, node

from .nodes import (
    load_openalex_author,
    load_openalex_author_institution_year,
    load_openalex_author_topic,
    load_openalex_institution,
    load_openalex_work,
    load_openalex_work_authorships,
    load_openalex_work_concept,
    load_openalex_work_corresponding_author_ids,
    load_openalex_work_location,
    load_openalex_work_referenced_works,
    load_openalex_work_topics,
    load_openalex_stage_work,
)


RAW_AUTHOR = "raw/openalex/author/parquet/author"
RAW_INSTITUTION = "raw/openalex/institution/parquet/institution"
RAW_WORK = "raw/openalex/work/parquet/work"


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                name="load_openalex_author",
                func=load_openalex_author,
                inputs=RAW_AUTHOR,
                outputs="ldg/openalex/author",
            ),
            node(
                name="load_openalex_author_institution_year",
                func=load_openalex_author_institution_year,
                inputs=RAW_AUTHOR,
                outputs="ldg/openalex/map_author_institution_year",
            ),
            node(
                name="load_openalex_author_topic",
                func=load_openalex_author_topic,
                inputs=RAW_AUTHOR,
                outputs="ldg/openalex/map_author_topic",
            ),
            node(
                name="load_openalex_stage_work",
                func=load_openalex_stage_work,
                inputs=RAW_WORK,
                outputs="memory/openalex/work",
            ),
            node(
                name="load_openalex_work",
                func=load_openalex_work,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/work",
            ),
            node(
                name="load_openalex_work_authorships",
                func=load_openalex_work_authorships,
                inputs="memory/openalex/work",
                outputs=[
                    "ldg/openalex/map_work_author",
                    "ldg/openalex/map_work_institution",
                    "ldg/openalex/map_author_institution",
                ],
            ),
            node(
                name="load_openalex_work_location",
                func=load_openalex_work_location,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/map_work_location",
            ),
            node(
                name="load_openalex_work_referenced_works",
                func=load_openalex_work_referenced_works,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/map_work_referenced_work",
            ),
            node(
                name="load_openalex_work_concept",
                func=load_openalex_work_concept,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/map_work_concept",
            ),
            node(
                name="load_openalex_work_corresponding_author_ids",
                func=load_openalex_work_corresponding_author_ids,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/map_work_corresponding_author",
            ),
            node(
                name="load_openalex_work_topics",
                func=load_openalex_work_topics,
                inputs="memory/openalex/work",
                outputs="ldg/openalex/map_work_topic",
            ),
            node(
                name="load_openalex_institution",
                func=load_openalex_institution,
                inputs=RAW_INSTITUTION,
                outputs="ldg/openalex/institution",
            ),
        ],
        tags="load_openalex",
    )
