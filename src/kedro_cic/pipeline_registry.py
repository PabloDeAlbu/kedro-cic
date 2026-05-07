"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from kedro_cic.pipelines.dspace5_extract import create_pipeline as create_dspace5_extract
from kedro_cic.pipelines.dspace5_load import create_pipeline as create_dspace5_load
from kedro_cic.pipelines.dspacedb import create_pipeline as create_dspacedb
from kedro_cic.pipelines.gs_load import create_pipeline as create_gs_load
from kedro_cic.pipelines.oai_extract import create_pipeline as create_oai_extract
from kedro_cic.pipelines.oai_load import create_pipeline as create_oai_load
from kedro_cic.pipelines.oai_load_item import create_pipeline as create_oai_load_item
from kedro_cic.pipelines.openaire_extract import create_pipeline as create_openaire_extract
from kedro_cic.pipelines.openaire_load import create_pipeline as create_openaire_load
from kedro_cic.pipelines.openalex_extract import create_pipeline as create_openalex_extract
from kedro_cic.pipelines.openalex_load import create_pipeline as create_openalex_load


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines = {
        "dspace5_extract": create_dspace5_extract(),
        "dspace5_load": create_dspace5_load(),
        "dspacedb": create_dspacedb(),
        "gs_load": create_gs_load(),
        "oai_extract": create_oai_extract(),
        "oai_load": create_oai_load(),
        "oai_load_item": create_oai_load_item(),
        "openaire_extract": create_openaire_extract(),
        "openaire_load": create_openaire_load(),
        "openalex_extract": create_openalex_extract(),
        "openalex_load": create_openalex_load(),
    }
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines
