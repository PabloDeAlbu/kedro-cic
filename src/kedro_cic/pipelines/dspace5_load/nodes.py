"""Nodes for the `dspace5_load` pipeline."""

from __future__ import annotations

import pandas as pd

_EXTRACT_META_COLS = ["_source_label", "_institution_ror", "_extract_datetime"]


def _add_extract_metadata(df: pd.DataFrame) -> pd.DataFrame:
    enriched_df = df.copy()
    for col in _EXTRACT_META_COLS:
        if col not in enriched_df.columns:
            enriched_df[col] = pd.NA
    enriched_df["_extract_datetime"] = pd.to_datetime(
        enriched_df["_extract_datetime"], errors="coerce"
    )
    return enriched_df


def _add_load_metadata(df: pd.DataFrame, load_datetime=None) -> pd.DataFrame:
    enriched_df = df.copy()
    if load_datetime is None:
        load_datetime = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)
    enriched_df["_load_datetime"] = pd.to_datetime(load_datetime)
    return enriched_df


def _astype_str(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype(str)
    return df


def _prepare_table(
    df: pd.DataFrame,
    string_columns: list[str] | None = None,
    drop_columns: list[str] | None = None,
) -> pd.DataFrame:
    prepared_df = _add_extract_metadata(df).convert_dtypes()
    if string_columns:
        prepared_df = _astype_str(prepared_df, string_columns)
    if drop_columns:
        prepared_df = prepared_df.drop(columns=drop_columns, errors="ignore")
    return _add_load_metadata(prepared_df)


def load_dspace5(
    df_bitstream,
    df_bundle2bitstream,
    df_collection2item,
    df_collection,
    df_community2collection,
    df_community2community,
    df_community,
    df_handle,
    df_item2bundle,
    df_item,
    df_metadatafieldregistry,
    df_metadataschemaregistry,
    df_metadatavalue,
):
    return (
        _prepare_table(df_bitstream, string_columns=["uuid"]),
        _prepare_table(
            df_bundle2bitstream, string_columns=["bundle_id", "bitstream_id"]
        ),
        _prepare_table(df_collection2item, string_columns=["collection_id", "item_id"]),
        _prepare_table(
            df_collection,
            string_columns=["uuid", "submitter", "admin"],
            drop_columns=["template_item_id", "logo_bitstream_id"],
        ),
        _prepare_table(
            df_community2collection,
            string_columns=["collection_id", "community_id"],
        ),
        _prepare_table(
            df_community2community,
            string_columns=["parent_comm_id", "child_comm_id"],
        ),
        _prepare_table(
            df_community,
            string_columns=["uuid", "admin"],
            drop_columns=["logo_bitstream_id"],
        ),
        _prepare_table(df_handle, string_columns=["resource_id"]),
        _prepare_table(df_item2bundle, string_columns=["bundle_id", "item_id"]),
        _prepare_table(
            df_item,
            string_columns=["uuid", "item_id", "submitter_id", "owning_collection"],
        ),
        _prepare_table(df_metadatafieldregistry),
        _prepare_table(df_metadataschemaregistry),
        _prepare_table(df_metadatavalue, string_columns=["dspace_object_id"]),
    )
