from __future__ import annotations

from pathlib import Path

import pandas as pd

from kedro_cic.io.parquet_batch_dataset import ParquetBatchDataset


def test_load_returns_dataframe_batches(tmp_path: Path):
    filepath = tmp_path / "work.parquet"
    pd.DataFrame(
        {
            "id": ["W1", "W2", "W3"],
            "title": ["t1", "t2", "t3"],
            "unused": [1, 2, 3],
        }
    ).to_parquet(filepath)

    dataset = ParquetBatchDataset(
        filepath=str(filepath),
        batch_size=2,
        load_args={"columns": ["id", "title", "missing_column"]},
    )

    batches = list(dataset.load())

    assert [list(batch.columns) for batch in batches] == [["id", "title"], ["id", "title"]]
    assert [len(batch) for batch in batches] == [2, 1]
