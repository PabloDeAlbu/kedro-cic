import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from kedro_cic.pipelines.load_google_scholar import create_pipeline


def test_load_google_scholar_pipeline_contains_author_nodes():
    pipeline = create_pipeline()
    author_node = pipeline.nodes[0]

    assert author_node.name == "load_google_scholar_author"
    assert author_node.inputs == ["raw/google_scholar/html"]
    assert author_node.outputs == ["ldg/google_scholar/author"]
    assert all("load_google_scholar" in node.tags for node in pipeline.nodes)
