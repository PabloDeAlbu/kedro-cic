import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from kedro_cic.pipelines.load_openaire import create_pipeline


def test_load_openaire_pipeline_reads_new_raw_layout():
    pipeline = create_pipeline()

    assert all(
        "raw/openaire/researchproduct/parquet/researchproduct" in node.inputs
        for node in pipeline.nodes
    )
    assert all("load_openaire" in node.tags for node in pipeline.nodes)
