"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from kedro_cic.pipelines.dspace5_extract import create_pipeline as create_dspace5_extract
from kedro_cic.pipelines.dspace5_load import create_pipeline as create_dspace5_load
from kedro_cic.pipelines.dspacedb import create_pipeline as create_dspacedb
from kedro_cic.pipelines.extract_dspacedb5 import (
    create_pipeline as create_extract_dspacedb5,
)
from kedro_cic.pipelines.extract_openaire import (
    create_pipeline as create_extract_openaire,
)
from kedro_cic.pipelines.extract_openalex import (
    create_pipeline as create_extract_openalex,
)
from kedro_cic.pipelines.load_dspacedb5 import (
    create_pipeline as create_load_dspacedb5,
)
from kedro_cic.pipelines.load_openaire import create_pipeline as create_load_openaire
from kedro_cic.pipelines.load_openalex import create_pipeline as create_load_openalex
from kedro_cic.pipelines.load_google_scholar import (
    create_pipeline as create_load_google_scholar,
)
from kedro_cic.pipelines.oai_extract import create_pipeline as create_oai_extract
from kedro_cic.pipelines.oai_load import create_pipeline as create_oai_load
from kedro_cic.pipelines.oai_load_item import create_pipeline as create_oai_load_item
from kedro_cic.pipelines.vocsedici_extract import create_pipeline as create_vocsedici_extract
from kedro_cic.pipelines.vocsedici_load import create_pipeline as create_vocsedici_load


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines = {
        "dspace5_extract": create_dspace5_extract(),
        "dspace5_load": create_dspace5_load(),
        "dspacedb": create_dspacedb(),
        "extract_dspacedb5": create_extract_dspacedb5(),
        "extract_openaire": create_extract_openaire(),
        "extract_openalex": create_extract_openalex(),
        "load_dspacedb5": create_load_dspacedb5(),
        "load_google_scholar": create_load_google_scholar(),
        "load_openaire": create_load_openaire(),
        "load_openalex": create_load_openalex(),
        "oai_extract": create_oai_extract(),
        "oai_load": create_oai_load(),
        "oai_load_item": create_oai_load_item(),
        "vocsedici_extract": create_vocsedici_extract(),
        "vocsedici_load": create_vocsedici_load(),
    }
    pipelines["__default__"] = sum(pipelines.values())
    return pipelines
