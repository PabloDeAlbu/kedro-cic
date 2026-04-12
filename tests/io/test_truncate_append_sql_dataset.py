from __future__ import annotations

from pathlib import Path

import pandas as pd
from kedro.config import OmegaConfigLoader
from sqlalchemy import create_engine

from kedro_cic.io.truncate_append_sql_dataset import TruncateAppendSQLTableDataset


class _RecordingConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, statement) -> None:
        self.statements.append(str(statement))

    def __enter__(self) -> "_RecordingConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _RecordingEngine:
    def __init__(self) -> None:
        self.dialect = create_engine("sqlite://").dialect
        self.connection = _RecordingConnection()

    def begin(self) -> _RecordingConnection:
        return self.connection


def test_save_truncates_then_appends_without_replace(monkeypatch):
    dataset = TruncateAppendSQLTableDataset(
        table_name="researchproduct",
        credentials={"con": "postgresql://unit-test"},
        load_args={"schema": "ldg_openaire"},
        save_args={
            "schema": "ldg_openaire",
            "if_exists": "append",
            "index": False,
            "chunksize": 500,
        },
    )
    fake_engine = _RecordingEngine()
    type(dataset).engines[dataset._connection_str] = fake_engine
    monkeypatch.setattr(dataset, "_exists", lambda: True)
    monkeypatch.setattr(dataset, "_get_existing_column_names", lambda: ["id"])

    captured: dict[str, object] = {}

    def fake_to_sql(self, *, con, **kwargs):
        captured["con"] = con
        captured["kwargs"] = kwargs

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    dataset.save(pd.DataFrame({"id": [1, 2]}))

    assert fake_engine.connection.statements == [
        "TRUNCATE TABLE ldg_openaire.researchproduct"
    ]
    assert captured["con"] is fake_engine.connection
    assert captured["kwargs"] == {
        "name": "researchproduct",
        "schema": "ldg_openaire",
        "if_exists": "append",
        "index": False,
        "chunksize": 500,
    }
    assert "replace" not in str(captured["kwargs"])


def test_save_appends_without_truncate_when_table_does_not_exist(monkeypatch):
    dataset = TruncateAppendSQLTableDataset(
        table_name="researchproduct",
        credentials={"con": "postgresql://unit-test-no-table"},
        save_args={"schema": "ldg_openaire"},
    )
    fake_engine = _RecordingEngine()
    type(dataset).engines[dataset._connection_str] = fake_engine
    monkeypatch.setattr(dataset, "_exists", lambda: False)

    calls: list[dict[str, object]] = []

    def fake_to_sql(self, *, con, **kwargs):
        calls.append({"con": con, "kwargs": kwargs})

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    dataset.save(pd.DataFrame({"id": [1]}))

    assert fake_engine.connection.statements == []
    assert calls == [
        {
            "con": fake_engine.connection,
            "kwargs": {
                "name": "researchproduct",
                "schema": "ldg_openaire",
                "if_exists": "append",
                "index": False,
            },
        }
    ]


def test_save_filters_out_columns_missing_from_existing_table(monkeypatch):
    dataset = TruncateAppendSQLTableDataset(
        table_name="author",
        credentials={"con": "postgresql://unit-test-filter-columns"},
        save_args={"schema": "ldg_openalex"},
    )
    fake_engine = _RecordingEngine()
    type(dataset).engines[dataset._connection_str] = fake_engine
    monkeypatch.setattr(dataset, "_exists", lambda: True)
    monkeypatch.setattr(dataset, "_get_existing_column_names", lambda: ["id", "_load_datetime"])

    captured: dict[str, object] = {}

    def fake_to_sql(self, *, con, **kwargs):
        captured["columns"] = list(self.columns)
        captured["con"] = con
        captured["kwargs"] = kwargs

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    dataset.save(
        pd.DataFrame(
            {
                "id": ["https://openalex.org/A1"],
                "source_system": ["openalex"],
                "_load_datetime": [pd.Timestamp("2026-04-03 00:00:00")],
            }
        )
    )

    assert captured["columns"] == ["id", "_load_datetime"]

def test_catalog_uses_custom_dataset_for_landing_tables():
    config_loader = OmegaConfigLoader(
        conf_source=str(Path.cwd() / "conf"),
        base_env="base",
        default_run_env="local",
    )

    catalog_config = config_loader["catalog"]
    dataset_config = catalog_config["ldg/{source}/{tablename}"]

    assert (
        dataset_config["type"]
        == "kedro_cic.io.truncate_append_sql_dataset.TruncateAppendSQLTableDataset"
    )
    assert dataset_config["credentials"] == "dw"
    assert dataset_config["load_args"]["schema"] == "ldg_{source}"
    assert dataset_config["save_args"] == {"schema": "ldg_{source}"}
    assert dataset_config["truncate"] is True
    assert dataset_config["truncate_cascade"] is False


def test_catalog_overrides_dspace5_metadatavalue_chunksize():
    config_loader = OmegaConfigLoader(
        conf_source=str(Path.cwd() / "conf"),
        base_env="base",
        default_run_env="local",
    )

    catalog_config = config_loader["catalog"]
    dataset_config = catalog_config["ldg/dspace5/metadatavalue"]

    assert (
        dataset_config["type"]
        == "kedro_cic.io.truncate_append_sql_dataset.TruncateAppendSQLTableDataset"
    )
    assert dataset_config["table_name"] == "metadatavalue"
    assert dataset_config["load_args"] == {"schema": "ldg_dspace5"}
    assert dataset_config["save_args"] == {
        "schema": "ldg_dspace5",
        "chunksize": 100,
    }
    assert dataset_config["truncate"] is True
    assert dataset_config["truncate_cascade"] is False
