import json
import time

import pandas as pd
import requests


def clean_extract_openalex_institution(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza el campo "international" para evitar fallos al escribir Parquet."""
    df = df.copy()
    if "international" in df.columns:
        df["international"] = df["international"].apply(
            lambda x: None if not x else json.dumps(x, ensure_ascii=False)
        )
    return df


def _format_openalex_filter_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    return value

def _build_openalex_filter_string(
    filter_field: str,
    institution_ror: str,
    extra_filters: dict | None = None,
) -> tuple[str, dict]:
    effective_filters = {filter_field: institution_ror}
    if extra_filters:
        effective_filters.update(
            {
                key: value
                for key, value in extra_filters.items()
                if value is not None and value != ""
            }
        )

    filter_string = ",".join(
        f"{key}:{_format_openalex_filter_value(value)}"
        for key, value in effective_filters.items()
    )
    return filter_string, effective_filters


def _add_extract_openalex_metadata(
    df: pd.DataFrame,
    *,
    institution_ror: str,
    filter_field: str,
    entity: str,
    effective_filters: dict,
) -> pd.DataFrame:
    extract_ts = pd.Timestamp.now(tz="UTC").floor("s").tz_localize(None)
    extract_filters_json = json.dumps(
        effective_filters,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    enriched_df = df.copy()
    enriched_df["source_system"] = "openalex"
    enriched_df["entity_type"] = entity.removesuffix("s")
    enriched_df["extract_datetime"] = extract_ts
    enriched_df["extract_date"] = extract_ts.date()
    enriched_df["institution_ror"] = institution_ror or pd.NA
    enriched_df["extract_filters"] = extract_filters_json
    enriched_df["extract_filter_label"] = f"{filter_field}:{institution_ror}"
    enriched_df["endpoint"] = entity
    enriched_df["api_path"] = f"/{entity}"

    # Legacy aliases kept for current downstream compatibility.
    enriched_df["_filter_param"] = filter_field
    enriched_df["_filter_value"] = institution_ror
    enriched_df["_extract_datetime"] = extract_ts
    return enriched_df


def extract_openalex(
    institution_ror: str,
    filter_field: str,
    entity: str = "institutions",
    env: str = "dev",
    query_options: dict | None = None,
    cleaner=None,
):
    """
    Fetch data from OpenAlex API for a given entity and institution ROR.

    Args:
        entity (str): 'authors', 'institutions', 'works', etc.
        institution_ror (str): ROR id of the institution.
        env (str): 'dev' or 'prod'.
        filter_field (str): the filter key to use (e.g. 'affiliations.institution.ror').
        cleaner (callable): function to clean DataFrame columns, optional.

    Returns:
        pd.DataFrame: full concatenated results
        pd.DataFrame: head(1000) sample
    """
    session = requests.Session()
    base_url = f"https://api.openalex.org/{entity}"
    query_options = query_options or {}
    per_page = query_options.get("per_page", 200)
    extra_filters = query_options.get("extra_filters", {})
    request_timeout = query_options.get("timeout", (5, 30))
    filter_string, effective_filters = _build_openalex_filter_string(
        filter_field=filter_field,
        institution_ror=institution_ror,
        extra_filters=extra_filters,
    )
    cursor = "*"
    iteration_limit = 1
    iteration_count = 0
    all_dataframes = []

    print(
        f"OpenAlex extract entity={entity}, env={env}, per_page={per_page}, "
        f"iteration_limit={iteration_limit}",
        flush=True,
    )

    while True:
        request_params = {
            "filter": filter_string,
            "cursor": cursor,
            "per-page": per_page,
        }
        print(f"Iteration count: {iteration_count}", flush=True)
        print(f"GET {base_url} params={request_params}", flush=True)

        try:
            response = session.get(base_url, params=request_params, timeout=request_timeout)
            response.raise_for_status()
            api_response = response.json()
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}", flush=True)
            break
        except ValueError:
            print("Error al decodificar JSON.", flush=True)
            break

        if 'results' not in api_response or not api_response['results']:
            print("No hay más datos disponibles.", flush=True)
            break

        df_tmp = pd.DataFrame.from_dict(api_response['results'])
        if cleaner:
            df_tmp = cleaner(df_tmp)
        df_tmp = _add_extract_openalex_metadata(
            df_tmp,
            institution_ror=institution_ror,
            filter_field=filter_field,
            entity=entity,
            effective_filters={
                **effective_filters,
                "per_page": per_page,
            },
        )
        all_dataframes.append(df_tmp)

        # update cursor
        cursor = api_response.get('meta', {}).get('next_cursor')
        if not cursor:
            break

        iteration_count += 1
        if env == 'dev' and iteration_count >= iteration_limit:
            print(
                f"Stopping pagination because env=dev reached iteration_limit={iteration_limit}.",
                flush=True,
            )
            break

        time.sleep(1)

    df = pd.concat(all_dataframes, ignore_index=True) if all_dataframes else pd.DataFrame()
    if df.empty:
        df = _add_extract_openalex_metadata(
            df,
            institution_ror=institution_ror,
            filter_field=filter_field,
            entity=entity,
            effective_filters={
                **effective_filters,
                "per_page": per_page,
            },
        )

    return df, df.head(1000)
