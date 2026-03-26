import pandas as pd


DSPACE5_TABLES = (
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
    source_label: str,
    institution_ror: str,
    extract_datetime: pd.Timestamp,
) -> pd.DataFrame:
    df = df.copy()
    df["_source_label"] = source_label
    df["_institution_ror"] = institution_ror
    df["_extract_datetime"] = extract_datetime
    return df


def dspace5_extract_tables(
    tables,
    source_label,
    institution_ror,
    *dataframes,
):
    configured_tables = tuple(tables)

    if configured_tables != DSPACE5_TABLES:
        raise ValueError(
            f"Configured tables do not match pipeline inputs. "
            f"Expected {DSPACE5_TABLES}, got {configured_tables}."
        )

    if len(dataframes) != len(DSPACE5_TABLES):
        raise ValueError(
            f"Expected {len(DSPACE5_TABLES)} dataframes, got {len(dataframes)}."
        )

    extract_datetime = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)

    return tuple(
        _add_extract_metadata(df, source_label, institution_ror, extract_datetime)
        for df in dataframes
    )
