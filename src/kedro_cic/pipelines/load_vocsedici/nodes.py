from __future__ import annotations

import pandas as pd

_EXTRACT_META_COLS = [
    "_source_system",
    "_source_table",
    "_extract_datetime",
    "_extract_date",
    "_source_label",
    "_extract_env",
    "_filter_param",
    "_filter_value",
]


def _add_extract_metadata(df: pd.DataFrame) -> pd.DataFrame:
    enriched_df = df.copy()
    for col in _EXTRACT_META_COLS:
        if col not in enriched_df.columns:
            enriched_df[col] = pd.NA
    enriched_df["_extract_datetime"] = pd.to_datetime(
        enriched_df["_extract_datetime"], errors="coerce"
    )
    if "_extract_date" in enriched_df.columns:
        enriched_df["_extract_date"] = pd.to_datetime(
            enriched_df["_extract_date"], errors="coerce"
        ).dt.date
    return enriched_df


def _add_load_metadata(df: pd.DataFrame, load_datetime=None) -> pd.DataFrame:
    enriched_df = df.copy()
    if load_datetime is None:
        load_datetime = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)
    enriched_df["_load_datetime"] = pd.to_datetime(load_datetime)
    return enriched_df


def _prepare_table(df: pd.DataFrame) -> pd.DataFrame:
    prepared_df = _add_extract_metadata(df).convert_dtypes()
    return _add_load_metadata(prepared_df)


def load_vocsedici_tables(*dataframes):
    return tuple(_prepare_table(df) for df in dataframes)
