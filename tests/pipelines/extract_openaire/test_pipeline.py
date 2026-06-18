import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from kedro_cic.pipelines.extract_openaire import create_pipeline


def test_extract_openaire_pipeline_outputs_new_raw_layout():
    pipeline = create_pipeline()
    node = pipeline.nodes[0]

    assert node.name == "extract_openaire_researchproduct"
    assert node.outputs == [
        "raw/openaire/researchproduct/parquet/researchproduct",
        "raw/openaire/researchproduct/parquet/researchproduct_dev",
    ]
    assert "extract_openaire" in node.tags
