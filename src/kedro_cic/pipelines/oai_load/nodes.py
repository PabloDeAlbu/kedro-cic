import pandas as pd


def _pick_load_datetime(df: pd.DataFrame) -> pd.Timestamp:
    """Return the batch load timestamp, preserving an existing value if present."""
    for column in ("load_datetime", "_load_datetime"):
        if column not in df.columns:
            continue
        values = pd.to_datetime(df[column], errors="coerce", utc=True).dropna()
        if not values.empty:
            return values.max()
    return pd.Timestamp.now(tz="UTC")


def _normalize_extract_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Expose the raw extraction timestamp under the landing contract name."""
    if "extract_datetime" in df.columns:
        return df
    if "_extract_datetime" not in df.columns:
        raise ValueError("OAI records require _extract_datetime")
    return df.rename(columns={"_extract_datetime": "extract_datetime"})


def oai_load_identifiers(df_identifiers_raw: pd.DataFrame) -> pd.DataFrame:
    df_identifiers_raw = _normalize_extract_datetime(df_identifiers_raw.copy())
    load_dt = _pick_load_datetime(df_identifiers_raw)

    identifier_columns = [
        'record_id',
        'datestamp',
        'is_deleted',
        'extract_datetime',
        '_context',
        '_source_key',
        '_repository_identifier',
        '_institution_ror',
        '_base_url',
        '_metadata_prefix',
    ]
    df_identifiers = df_identifiers_raw[identifier_columns].copy()
    df_identifiers_sets = (
        df_identifiers_raw[
            ['record_id', 'set_id', 'extract_datetime', '_source_key']
        ]
        .explode('set_id', ignore_index=True)
        .dropna(subset=['set_id'])
    )

    df_identifiers['_load_datetime'] = load_dt
    df_identifiers_sets['_load_datetime'] = load_dt

    return df_identifiers, df_identifiers_sets


def oai_load_records(df_records_raw: pd.DataFrame, env: str = 'dev') -> pd.DataFrame:
    df_records_raw = _normalize_extract_datetime(df_records_raw.copy())
    load_dt = _pick_load_datetime(df_records_raw)

    if env == 'dev':
        df_records_raw = df_records_raw.head(1000)

    def _select(columns):
        return df_records_raw.loc[:, columns].copy()

    def _explode(column):
        base_cols = ['record_id', column, 'extract_datetime']
        missing_cols = [col for col in base_cols if col not in df_records_raw.columns]
        if missing_cols:
            raise ValueError(
                f"OAI records require columns for {column}: {missing_cols}"
            )
        return (
            _select(base_cols)
            .explode(column, ignore_index=True)
            .dropna(subset=[column])
            .assign(load_datetime=load_dt)
        )

    record_columns = [
        'record_id',
        'col_id',
        'title',
        'date_issued',
        'extract_datetime',
        '_context',
        '_source_key',
        '_repository_identifier',
        '_institution_ror',
        '_base_url',
        '_metadata_prefix',
    ]
    df_records = _select(record_columns).assign(load_datetime=load_dt)
    df_record_creators = _explode('creators')
    df_record_descriptions = _explode('description')
    df_record_types = _explode('types')
    df_record_identifiers = _explode('identifiers')
    df_record_languages = _explode('languages')
    df_record_subjects = _explode('subjects')
    df_record_publishers = _explode('publishers')
    df_record_relations = _explode('relations')
    df_record_rights = _explode('rights')
    df_record_formats = _explode('formats')
    df_record_sets = _explode('set_id')

#    df_record_sets = _select(['record_id','set_id', 'extract_datetime'])
#    sets_df = df_record_sets.pop('set_id').apply(pd.Series)
#    sets_df = sets_df.rename(columns=lambda i: f'set_{i}')
#    df_record_sets = pd.concat([df_record_sets, sets_df], axis=1)
#    df_record_sets['_load_datetime'] = load_dt

    return df_records, df_record_creators, df_record_descriptions, \
        df_record_types, df_record_identifiers, df_record_languages, \
        df_record_subjects, df_record_publishers, df_record_relations, \
        df_record_rights, df_record_formats, df_record_sets


def oai_load_sets(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    load_dt = _pick_load_datetime(df)
    df.dropna(inplace=True)
    df['_load_datetime'] = load_dt

    return df
