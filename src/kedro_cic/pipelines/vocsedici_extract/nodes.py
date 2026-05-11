from __future__ import annotations

import pandas as pd

VOCSEDICI_TABLES = (
    "node",
    "node_field_data",
    "node__field_nombre",
    "node__field_apellido",
    "node__field_orcid",
    "node__field_mail",
    "node__field_dni",
    "node__field_cuit",
    "node__field_telefono",
    "node__field_direcci_n",
    "node__field_google_scholar",
    "node__field_researchgate",
    "node__field_old_id",
    "node__field_filiacion",
    "node__field_nombre_institucion",
    "node__field_nombre_institucion_variant",
    "node__field_abreviatura",
    "node__field_id_pidu",
    "node__field_id_termino",
    "node__field_padre",
)


def _add_extract_metadata(
    df: pd.DataFrame,
    *,
    source_label: str,
    extract_env: str,
    source_table: str,
    filter_param: str | None,
    filter_value,
    extract_datetime: pd.Timestamp,
) -> pd.DataFrame:
    enriched_df = df.copy()
    enriched_df["_source_system"] = "voc"
    enriched_df["_source_table"] = source_table
    enriched_df["_extract_datetime"] = extract_datetime
    enriched_df["_extract_date"] = extract_datetime.date()
    enriched_df["_source_label"] = source_label
    enriched_df["_extract_env"] = extract_env
    enriched_df["_filter_param"] = filter_param if filter_param else pd.NA
    enriched_df["_filter_value"] = filter_value if filter_value not in (None, "") else pd.NA
    return enriched_df


def vocsedici_extract_tables(
    tables,
    source_label,
    extract_env,
    filter_param,
    filter_value,
    *dataframes,
):
    configured_tables = tuple(tables)

    if configured_tables != VOCSEDICI_TABLES:
        raise ValueError(
            f"Configured tables do not match pipeline inputs. "
            f"Expected {VOCSEDICI_TABLES}, got {configured_tables}."
        )

    if len(dataframes) != len(VOCSEDICI_TABLES):
        raise ValueError(
            f"Expected {len(VOCSEDICI_TABLES)} dataframes, got {len(dataframes)}."
        )

    extract_datetime = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)

    return tuple(
        _add_extract_metadata(
            df,
            source_label=source_label,
            extract_env=extract_env,
            source_table=table_name,
            filter_param=filter_param,
            filter_value=filter_value,
            extract_datetime=extract_datetime,
        )
        for table_name, df in zip(VOCSEDICI_TABLES, dataframes)
    )
