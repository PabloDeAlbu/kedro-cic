import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from kedro_cic.pipelines.load_openalex import create_pipeline


def test_load_openalex_pipeline_reads_new_raw_layout():
    pipeline = create_pipeline()
    inputs = sorted(input_ for node in pipeline.nodes for input_ in node.inputs)

    assert "raw/openalex/author/parquet/author" in inputs
    assert "raw/openalex/work/parquet/work" in inputs
    assert "raw/openalex/institution/parquet/institution" in inputs
    assert all("load_openalex" in node.tags for node in pipeline.nodes)
