from __future__ import annotations

import pandas as pd

DSPACE_DB5_TABLES = (
    "bitstream",
    "bundle2bitstream",
    "collection2item",
    "collection",
    "community2collection",
    "community2community",
    "community",
    "handle",
    "item2bundle",
    "item",
    "metadatafieldregistry",
    "metadataschemaregistry",
    "metadatavalue",
)


def _add_extract_metadata(
    df: pd.DataFrame,
    *,
    source_label: str,
    institution_ror: str,
    extract_env: str,
    source_table: str,
    filter_param: str | None,
    filter_value,
    extract_datetime: pd.Timestamp,
) -> pd.DataFrame:
    enriched_df = df.copy()
    enriched_df["_source_system"] = "dspacedb5"
    enriched_df["_source_table"] = source_table
    enriched_df["_extract_datetime"] = extract_datetime
    enriched_df["_extract_date"] = extract_datetime.date()
    enriched_df["_source_label"] = source_label
    enriched_df["_institution_ror"] = institution_ror
    enriched_df["_extract_env"] = extract_env
    enriched_df["_filter_param"] = filter_param if filter_param else pd.NA
    enriched_df["_filter_value"] = filter_value if filter_value not in (None, "") else pd.NA
    return enriched_df


def extract_dspacedb5_tables(
    tables,
    source_label,
    institution_ror,
    extract_env,
    filter_param,
    filter_value,
    *dataframes,
):
    configured_tables = tuple(tables)

    if configured_tables != DSPACE_DB5_TABLES:
        raise ValueError(
            f"Configured tables do not match pipeline inputs. "
            f"Expected {DSPACE_DB5_TABLES}, got {configured_tables}."
        )

    if len(dataframes) != len(DSPACE_DB5_TABLES):
        raise ValueError(
            f"Expected {len(DSPACE_DB5_TABLES)} dataframes, got {len(dataframes)}."
        )

    extract_datetime = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)

    return tuple(
        _add_extract_metadata(
            df,
            source_label=source_label,
            institution_ror=institution_ror,
            extract_env=extract_env,
            source_table=table_name,
            filter_param=filter_param,
            filter_value=filter_value,
            extract_datetime=extract_datetime,
        )
        for table_name, df in zip(DSPACE_DB5_TABLES, dataframes)
    )
