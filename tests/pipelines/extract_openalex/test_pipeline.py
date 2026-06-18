import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from kedro_cic.pipelines.extract_openalex import create_pipeline


def test_extract_openalex_pipeline_outputs_new_raw_layout():
    pipeline = create_pipeline()
    outputs = sorted(output for node in pipeline.nodes for output in node.outputs)

    assert "raw/openalex/work/parquet/work" in outputs
    assert "raw/openalex/work/parquet/work_dev" in outputs
    assert "raw/openalex/author/parquet/author" in outputs
    assert "raw/openalex/institution/parquet/institution" in outputs
    assert all("extract_openalex" in node.tags for node in pipeline.nodes)
