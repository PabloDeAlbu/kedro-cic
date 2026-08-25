import os
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import certifi
import pandas as pd
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_oai_response(
    base_url,
    verify=None,
    max_retries=3,
    backoff_factor=1.0,
    min_interval=0.0,
    timeout=30.0,
):

    # Usa el bundle de certifi para evitar errores de certificado en requests
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    VERIFY_SSL = os.getenv("OAI_VERIFY_SSL", "false").lower() == "true"
    CA_BUNDLE = os.getenv("OAI_CA_BUNDLE") or certifi.where()
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    verify_param = CA_BUNDLE if VERIFY_SSL else False
    if verify is not None:
        verify_param = verify

    for attempt in range(1, max_retries + 1):
        start_time = time.time()
        response = None
        error = None
        try:
            response = requests.get(base_url, verify=verify_param, timeout=timeout)
        except requests.RequestException as exc:
            error = exc
        elapsed_time = time.time() - start_time

        if min_interval > 0:
            wait_time = max(min_interval - elapsed_time, 0)
            if wait_time > 0:
                print(f"Pausando {wait_time:.2f} segundos para no saturar el servidor")
                time.sleep(wait_time)

        if error:
            print(f"Error en request (intento {attempt}/{max_retries}): {error}")

        if response is not None and response.status_code == 200:
            return response

        status = response.status_code if response is not None else "sin respuesta"
        print(f"Error: {status} (intento {attempt}/{max_retries})")

        if attempt < max_retries:
            backoff = backoff_factor * attempt
            print(f"Reintentando en {backoff:.2f} segundos...")
            time.sleep(backoff)
    return None

def log_oai_progress(token_elem, total_processed: int):
    """Muestra el avance usando completeListSize y los registros acumulados."""
    if token_elem is None:
        return
    total = token_elem.get('completeListSize')
    try:
        total_int = int(total) if total is not None else None
        if total_int is not None and total_processed is not None:
            remaining = total_int - total_processed
            print(f"Progreso OAI: {total_processed}/{total_int} (faltan ~{remaining})")
    except ValueError:
        # Si el servidor devuelve valores no numéricos, ignora el progreso.
        pass


def oai_extract_identifiers(
    base_url: str,
    context: str,
    env: str,
    source_key: str,
    repository_identifier: str,
    institution_ror: str,
    metadata_prefix: str = "oai_dc",
    dev_page_limit: int = 2,
    initial_resumption_token: str | None = None,
    page_limit: int | None = None,
    date_windows: list[dict[str, str]] | None = None,
    verify=None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build a manifest, optionally harvesting independent date windows."""
    identifiers = []
    iteration_limit = dev_page_limit if env == "dev" else page_limit
    windows = date_windows or [{}]
    if initial_resumption_token and len(windows) > 1:
        raise ValueError(
            "initial_resumption_token cannot be combined with multiple date windows"
        )

    for window in windows:
        unknown_keys = set(window) - {"from", "until"}
        if unknown_keys:
            raise ValueError(f"Unsupported OAI date window keys: {unknown_keys}")
        resumption_token = initial_resumption_token
        iteration_count = 0
        window_processed = 0

        while iteration_limit is None or iteration_count < iteration_limit:
            if resumption_token:
                query = {
                    "verb": "ListIdentifiers",
                    "resumptionToken": resumption_token,
                }
            else:
                query = {
                    "verb": "ListIdentifiers",
                    "metadataPrefix": metadata_prefix,
                    **window,
                }
            url = f"{base_url.rstrip('/')}/{context}?{urlencode(query)}"
            print(f"Consultando: {url}")

            response = get_oai_response(url, verify=verify)
            if response is None or not response.ok:
                raise RuntimeError(f"No se pudo completar el manifiesto OAI: {url}")

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as error:
                raise RuntimeError(f"Respuesta XML inválida para: {url}") from error

            ns = {"oai": "http://www.openarchives.org/OAI/2.0/"}
            headers = root.findall(".//oai:header", ns)
            for header in headers:
                identifier = header.find("oai:identifier", ns)
                datestamp = header.find("oai:datestamp", ns)
                identifiers.append(
                    {
                        "record_id": (
                            identifier.text if identifier is not None else None
                        ),
                        "datestamp": datestamp.text if datestamp is not None else None,
                        "set_id": [
                            node.text for node in header.findall("oai:setSpec", ns)
                        ],
                        "is_deleted": header.get("status") == "deleted",
                    }
                )

            iteration_count += 1
            window_processed += len(headers)
            token_elem = root.find(".//oai:resumptionToken", ns)
            resumption_token = token_elem.text if token_elem is not None else None
            log_oai_progress(token_elem, window_processed)
            if not resumption_token:
                break

    manifest = (
        pd.DataFrame(
            identifiers,
            columns=["record_id", "datestamp", "set_id", "is_deleted"],
        )
        .drop_duplicates(subset=["record_id"], keep="last")
        .reset_index(drop=True)
    )
    timestamp = pd.Timestamp.now(tz="UTC")
    manifest["_extract_datetime"] = timestamp
    manifest["_context"] = context
    manifest["_source_key"] = source_key
    manifest["_repository_identifier"] = repository_identifier
    manifest["_institution_ror"] = institution_ror
    manifest["_base_url"] = base_url.rstrip("/")
    manifest["_metadata_prefix"] = metadata_prefix
    return manifest, manifest.head(100)

def oai_extract_identifiers_by_sets(base_url: str, context: str, env: str, df_set: pd.DataFrame, iteration_limit = 1, verify=None) -> pd.DataFrame:
    records = []
    if env == "dev": iteration_limit = 2 

    col_ids = df_set.loc[:, "setSpec"].tolist()

    for set_id in col_ids:
        iteration_count = 0
        resumption_token = f'oai_dc///{set_id}/0'

        while True:
            if iteration_count >= iteration_limit:
                break

            params = f'/{context}?verb=ListIdentifiers&resumptionToken={resumption_token}'
            url = base_url + params

            print(f"Consultando: {url}")

            response = get_oai_response(url, verify=verify)
            if not response or not response.ok:
                print(f"Error al consultar: {url}")
                break
            
            iteration_count += 1

            xml_content = response.text

            root = ET.fromstring(xml_content)
            ns = { 'oai': 'http://www.openarchives.org/OAI/2.0/' }
        
            record_nodes = root.findall('.//oai:header', ns)

            if not record_nodes:
                print("No se encontraron más registros.")
                break

            for record in record_nodes:
                
                # Valores simples
                record_id = record.find('.//oai:identifier', ns)
                record_datestamp = record.find('.//oai:datestamp', ns)
                
                # Multivaluados
                setspec = [e.text for e in record.findall('.//oai:setSpec', ns)]

                records.append({
                    'record_id': record_id.text if record_id is not None else None,
                    'datestamp': record_datestamp.text if record_datestamp is not None else None,
                    'set_id': setspec,
                })

            token_elem = root.find('.//oai:resumptionToken', ns)
            if token_elem is not None:
                complete_list_size = int(token_elem.get('completeListSize'))
                resumption_token = token_elem.text

            # guarda el tamaño en el df de sets
            df_set.loc[df_set["setSpec"] == set_id, "completeListSize"] = (
                int(complete_list_size) if complete_list_size is not None else None
            )
          
    df = pd.DataFrame(records)

    timestamp = pd.Timestamp.now(tz="UTC").normalize()
    df['_extract_datetime'] = timestamp

    return df, df_set, df.head(100)

OAI_NAMESPACES = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

OAI_RECORD_COLUMNS = [
    "record_id", "datestamp", "set_id", "col_id", "title", "date_issued",
    "creators", "description", "types", "identifiers", "languages",
    "subjects", "publishers", "relations", "rights", "formats",
]

OAI_PROVENANCE_COLUMNS = [
    "_extract_datetime", "_context", "_source_key",
    "_repository_identifier", "_institution_ror", "_base_url",
    "_metadata_prefix",
]


def add_oai_provenance(
    df: pd.DataFrame,
    *,
    context: str,
    source_key: str,
    repository_identifier: str,
    institution_ror: str,
    base_url: str,
    metadata_prefix: str,
    timestamp: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Attach the common extraction provenance contract to an OAI dataset."""
    result = df.copy()
    result["_extract_datetime"] = timestamp or pd.Timestamp.now(tz="UTC")
    result["_context"] = context
    result["_source_key"] = source_key
    result["_repository_identifier"] = repository_identifier
    result["_institution_ror"] = institution_ror
    result["_base_url"] = base_url.rstrip("/")
    result["_metadata_prefix"] = metadata_prefix
    return result


def parse_oai_record(record: ET.Element) -> dict | None:
    """Parse one OAI-PMH record into the canonical raw records schema."""
    header = record.find("oai:header", OAI_NAMESPACES)
    metadata = record.find("oai:metadata", OAI_NAMESPACES)
    if header is None or metadata is None or header.get("status") == "deleted":
        return None

    def _text(path: str):
        node = metadata.find(path, OAI_NAMESPACES)
        return node.text if node is not None else None

    def _texts(path: str) -> list[str | None]:
        return [node.text for node in metadata.findall(path, OAI_NAMESPACES)]

    identifier = header.find("oai:identifier", OAI_NAMESPACES)
    datestamp = header.find("oai:datestamp", OAI_NAMESPACES)
    sets = [node.text for node in header.findall("oai:setSpec", OAI_NAMESPACES)]
    return {
        "record_id": identifier.text if identifier is not None else None,
        "datestamp": datestamp.text if datestamp is not None else None,
        "set_id": sets,
        "col_id": sets[0] if sets else None,
        "title": _text(".//dc:title"),
        "date_issued": _text(".//dc:date"),
        "creators": _texts(".//dc:creator"),
        "description": _texts(".//dc:description"),
        "types": _texts(".//dc:type"),
        "identifiers": _texts(".//dc:identifier"),
        "languages": _texts(".//dc:language"),
        "subjects": _texts(".//dc:subject"),
        "publishers": _texts(".//dc:publisher"),
        "relations": _texts(".//dc:relation"),
        "rights": _texts(".//dc:rights"),
        "formats": _texts(".//dc:format"),
    }


def oai_extract_records_by_identifiers(
    base_url: str,
    context: str,
    env: str,
    df_ids: pd.DataFrame,
    source_key: str,
    repository_identifier: str,
    institution_ror: str,
    metadata_prefix: str = "oai_dc",
    dev_identifier_limit: int = 2,
    identifier_limit: int | None = None,
    verify=None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Recover selected records with GetRecord and audit every failure."""
    records = []
    errors = []
    ids_limit = dev_identifier_limit if env == "dev" else identifier_limit
    ids = df_ids.head(ids_limit).loc[:, "record_id"].dropna().tolist()

    for record_id in ids:
        query = urlencode(
            {
                "verb": "GetRecord",
                "metadataPrefix": metadata_prefix,
                "identifier": record_id,
            }
        )
        url = f"{base_url.rstrip('/')}/{context}?{query}"

        print(f"Consultando: {url}")

        response = get_oai_response(url, verify=verify)
        if response is None or not response.ok:
            errors.append(
                {"record_id": record_id, "error_type": "request_failed", "url": url}
            )
            continue

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError:
            errors.append(
                {"record_id": record_id, "error_type": "invalid_xml", "url": url}
            )
            continue
        record_nodes = root.findall('.//oai:record', OAI_NAMESPACES)

        if not record_nodes:
            errors.append(
                {"record_id": record_id, "error_type": "record_not_found", "url": url}
            )
            continue

        parsed = parse_oai_record(record_nodes[0])
        if parsed is None:
            errors.append(
                {"record_id": record_id, "error_type": "record_deleted", "url": url}
            )
            continue
        records.append(parsed)

    timestamp = pd.Timestamp.now(tz="UTC")
    recovered = add_oai_provenance(
        pd.DataFrame(records, columns=OAI_RECORD_COLUMNS),
        context=context,
        source_key=source_key,
        repository_identifier=repository_identifier,
        institution_ror=institution_ror,
        base_url=base_url,
        metadata_prefix=metadata_prefix,
        timestamp=timestamp,
    )
    error_df = add_oai_provenance(
        pd.DataFrame(errors, columns=["record_id", "error_type", "url"]),
        context=context,
        source_key=source_key,
        repository_identifier=repository_identifier,
        institution_ror=institution_ror,
        base_url=base_url,
        metadata_prefix=metadata_prefix,
        timestamp=timestamp,
    )
    return recovered, error_df, recovered.head(100)


def oai_find_missing_record_identifiers(
    manifest: pd.DataFrame,
    records: pd.DataFrame,
) -> pd.DataFrame:
    """Return active manifest entries that are absent from harvested records."""
    active = manifest.loc[~manifest["is_deleted"].fillna(False)].copy()
    recovered_ids = records["record_id"].dropna().unique()
    return (
        active.loc[~active["record_id"].isin(recovered_ids)]
        .drop_duplicates(subset=["record_id"], keep="last")
        .reset_index(drop=True)
    )


def oai_merge_harvested_records(
    records: pd.DataFrame,
    recovered_records: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Consolidate bulk and GetRecord results into the latest raw snapshot."""
    consolidated = (
        pd.concat([records, recovered_records], ignore_index=True)
        .drop_duplicates(subset=["record_id"], keep="last")
        .reset_index(drop=True)
    )
    return consolidated, consolidated.head(100)


def oai_extract_records(
    base_url: str,
    context: str,
    env: str,
    source_key: str,
    repository_identifier: str,
    institution_ror: str,
    metadata_prefix: str = "oai_dc",
    dev_page_limit: int = 2,
    initial_resumption_token: str | None = None,
    page_limit: int | None = None,
    date_windows: list[dict[str, str]] | None = None,
    verify=None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if metadata_prefix != "oai_dc":
        raise ValueError(
            "oai_extract_records currently supports metadata_prefix=oai_dc"
        )

    records = []
    page_errors = []

    iteration_limit = dev_page_limit if env == "dev" else page_limit
    windows = date_windows or [{}]
    if initial_resumption_token and len(windows) > 1:
        raise ValueError(
            "initial_resumption_token cannot be combined with multiple date windows"
        )

    for window in windows:
        unknown_keys = set(window) - {"from", "until"}
        if unknown_keys:
            raise ValueError(f"Unsupported OAI date window keys: {unknown_keys}")
        resumption_token = initial_resumption_token
        iteration_count = 0
        window_processed = 0

        while iteration_limit is None or iteration_count < iteration_limit:
            if resumption_token:
                query = {"verb": "ListRecords", "resumptionToken": resumption_token}
            else:
                query = {
                    "verb": "ListRecords",
                    "metadataPrefix": metadata_prefix,
                    **window,
                }
            url = f"{base_url.rstrip('/')}/{context}?{urlencode(query)}"
            print(f"Consultando: {url}")
            response = get_oai_response(url, verify=verify)
            iteration_count += 1

            if response is None or not response.ok:
                if date_windows is None:
                    raise RuntimeError(f"No se pudo completar la cosecha OAI: {url}")
                page_errors.append(
                    {
                        "from": window.get("from"),
                        "until": window.get("until"),
                        "resumption_token": resumption_token,
                        "error_type": "request_failed",
                        "url": url,
                    }
                )
                break

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as error:
                if date_windows is None:
                    raise RuntimeError(f"Respuesta XML inválida para: {url}") from error
                page_errors.append(
                    {
                        "from": window.get("from"),
                        "until": window.get("until"),
                        "resumption_token": resumption_token,
                        "error_type": "invalid_xml",
                        "url": url,
                    }
                )
                break

            record_nodes = root.findall('.//oai:record', OAI_NAMESPACES)
            for record in record_nodes:
                parsed = parse_oai_record(record)
                if parsed is not None:
                    records.append(parsed)

            window_processed += len(record_nodes)
            token_elem = root.find('.//oai:resumptionToken', OAI_NAMESPACES)
            resumption_token = token_elem.text if token_elem is not None else None
            log_oai_progress(token_elem, window_processed)
            if not resumption_token:
                break

    df = add_oai_provenance(
        pd.DataFrame(records, columns=OAI_RECORD_COLUMNS)
        .drop_duplicates(subset=["record_id"], keep="last")
        .reset_index(drop=True),
        context=context,
        source_key=source_key,
        repository_identifier=repository_identifier,
        institution_ror=institution_ror,
        base_url=base_url,
        metadata_prefix=metadata_prefix,
    )

    errors = add_oai_provenance(
        pd.DataFrame(
            page_errors,
            columns=["from", "until", "resumption_token", "error_type", "url"],
        ),
        context=context,
        source_key=source_key,
        repository_identifier=repository_identifier,
        institution_ror=institution_ror,
        base_url=base_url,
        metadata_prefix=metadata_prefix,
    )
    return df, errors, df.head(100)

def oai_extract_sets(base_url, context, env, verify=None, iteration_limit=None):

    if iteration_limit is None and env == "dev":
        iteration_limit = 2

    resumption_token = 0
    all_sets = []

    iteration_count = 0

    while True:

        if iteration_limit is not None and iteration_count >= iteration_limit:
            break

        params = f'/{context}?verb=ListSets&resumptionToken=////{resumption_token}'
        url = base_url + params

        print(f"Consultando: {url}")

        response = get_oai_response(url, verify=verify)
        if not response:
            break

        xml_content = response.text
        root = ET.fromstring(xml_content)
        ns = {'oai': 'http://www.openarchives.org/OAI/2.0/'}

        sets_data = []
        for set_elem in root.findall('.//oai:set', ns):
            set_spec = set_elem.find('oai:setSpec', ns).text if set_elem.find('oai:setSpec', ns) is not None else None
            set_name = set_elem.find('oai:setName', ns).text if set_elem.find('oai:setName', ns) is not None else None
            sets_data.append({'setSpec': set_spec, 'setName': set_name})

        if not sets_data:
            print("No se encontraron más sets.")
            break

        all_sets.extend(sets_data)
        resumption_token += 100  # avanzar manualmente
        iteration_count += 1

    df_sets = pd.DataFrame(all_sets)

    timestamp = pd.Timestamp.now(tz="UTC").normalize()
    df_sets['_extract_datetime'] = timestamp

    return df_sets

def oai_intermediate_sets(df_sets):
    
    df_sets["is_col_set"] = df_sets["setSpec"].str.startswith("col_")
    df_sets["is_com_set"] = df_sets["setSpec"].str.startswith("com_")

    return df_sets

def oai_filter_col(df_sets, env):
    
    col_filter = df_sets["is_col_set"] == True
    df_col = df_sets[col_filter]#.loc[:, "setSpec"]

    if env == "dev":
        df_col = df_col.head(2)
    
    return df_col
