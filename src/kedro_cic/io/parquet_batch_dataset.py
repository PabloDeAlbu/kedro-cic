"""Parquet dataset variants optimized for batched reads."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from kedro.io.core import AbstractDataset, DatasetError


class ParquetBatchDataset(AbstractDataset):
    """Load a parquet file as an iterator of pandas DataFrames."""

    def __init__(
        self,
        *,
        filepath: str,
        batch_size: int = 1000,
        load_args: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._filepath = Path(filepath)
        self._batch_size = batch_size
        self._load_args = load_args or {}
        self._metadata = metadata or {}

    def _describe(self) -> dict[str, Any]:
        return {
            "filepath": str(self._filepath),
            "batch_size": self._batch_size,
            "load_args": self._load_args,
            "metadata": self._metadata,
        }

    def _load(self):
        if not self._filepath.exists():
            raise DatasetError(f"Parquet file not found: {self._filepath}")

        parquet_file = pq.ParquetFile(self._filepath)
        columns = self._load_args.get("columns")
        if columns is not None:
            available_columns = set(parquet_file.schema_arrow.names)
            columns = [column for column in columns if column in available_columns]

        def _iterator():
            if columns is None:
                for batch in parquet_file.iter_batches(
                    batch_size=self._batch_size,
                    use_threads=True,
                ):
                    yield batch.to_pandas()
                return

            for row_group_index in range(parquet_file.num_row_groups):
                table = parquet_file.read_row_group(
                    row_group_index,
                    columns=columns,
                )
                for batch in table.to_batches(max_chunksize=self._batch_size):
                    yield batch.to_pandas()

        return _iterator()

    def _save(self, data) -> None:
        raise DatasetError("ParquetBatchDataset is read-only.")

    def _exists(self) -> bool:
        return self._filepath.exists()
