from unittest.mock import patch

import pandas as pd

from kedro_cic.pipelines.oai_extract.nodes import (
    oai_extract_identifiers,
    oai_extract_records,
    oai_extract_records_by_identifiers,
)


class _Response:
    def __init__(self, text: str) -> None:
        self.text = text
        self.ok = True

    def __bool__(self) -> bool:
        return True


def _page(identifier: str, token: str | None = None) -> str:
    token_xml = (
        f'<resumptionToken completeListSize="2">{token}</resumptionToken>'
        if token
        else ""
    )
    return f"""
    <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"
             xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <ListRecords>
        <record>
          <header>
            <identifier>{identifier}</identifier>
            <datestamp>2026-08-24T12:00:00Z</datestamp>
            <setSpec>col_1</setSpec>
          </header>
          <metadata>
            <oai_dc:dc>
              <dc:title>Título {identifier}</dc:title>
              <dc:date>2025</dc:date>
              <dc:creator>Autor</dc:creator>
              <dc:type>article</dc:type>
              <dc:rights>openAccess</dc:rights>
            </oai_dc:dc>
          </metadata>
        </record>
        {token_xml}
      </ListRecords>
    </OAI-PMH>
    """


def _identifiers_page(token: str | None = None) -> str:
    token_xml = f"<resumptionToken>{token}</resumptionToken>" if token else ""
    return f"""
    <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
      <ListIdentifiers>
        <header>
          <identifier>oai:example:active</identifier>
          <datestamp>2026-08-24</datestamp>
          <setSpec>col_1</setSpec>
        </header>
        <header status="deleted">
          <identifier>oai:example:deleted</identifier>
          <datestamp>2026-08-24</datestamp>
        </header>
        {token_xml}
      </ListIdentifiers>
    </OAI-PMH>
    """


def test_extract_identifiers_builds_manifest_with_deleted_records() -> None:
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        return_value=_Response(_identifiers_page()),
    ):
        manifest, preview = oai_extract_identifiers(
            base_url="https://example.edu/oai/",
            context="request",
            env="full",
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
        )

    assert manifest["record_id"].tolist() == [
        "oai:example:active",
        "oai:example:deleted",
    ]
    assert manifest["is_deleted"].tolist() == [False, True]
    assert manifest.loc[0, "set_id"] == ["col_1"]
    assert manifest["_source_key"].unique().tolist() == ["example"]
    assert len(preview) == 2


def test_extract_identifiers_combines_and_deduplicates_date_windows() -> None:
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        return_value=_Response(_identifiers_page()),
    ) as get_response:
        manifest, _ = oai_extract_identifiers(
            base_url="https://example.edu/oai",
            context="request",
            env="full",
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
            date_windows=[
                {"from": "2025-01-01", "until": "2025-12-31"},
                {"from": "2026-01-01", "until": "2026-12-31"},
            ],
        )

    assert get_response.call_count == 2
    assert len(manifest) == 2
    assert "from=2025-01-01&until=2025-12-31" in (
        get_response.call_args_list[0].args[0]
    )


def test_extract_records_uses_dev_limit_and_adds_provenance() -> None:
    responses = [
        _Response(_page("oai:repositorio.uca.edu.ar:1", "next-token")),
        _Response(_page("oai:repositorio.uca.edu.ar:2")),
    ]

    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        side_effect=responses,
    ) as get_response:
        records, preview = oai_extract_records(
            base_url="https://repositorio.uca.edu.ar/oai/",
            context="request",
            env="dev",
            source_key="uca",
            repository_identifier="repositorio.uca.edu.ar",
            institution_ror="https://ror.org/0422kzb24",
            metadata_prefix="oai_dc",
            dev_page_limit=2,
        )

    assert len(records) == 2
    assert len(preview) == 2
    assert get_response.call_count == 2
    assert get_response.call_args_list[0].args[0] == (
        "https://repositorio.uca.edu.ar/oai/request"
        "?verb=ListRecords&metadataPrefix=oai_dc"
    )
    assert get_response.call_args_list[1].args[0].endswith(
        "?verb=ListRecords&resumptionToken=next-token"
    )
    assert records["_source_key"].unique().tolist() == ["uca"]
    assert records["_repository_identifier"].unique().tolist() == [
        "repositorio.uca.edu.ar"
    ]
    assert records["_institution_ror"].unique().tolist() == [
        "https://ror.org/0422kzb24"
    ]
    assert records["_metadata_prefix"].unique().tolist() == ["oai_dc"]
    assert records["_extract_datetime"].notna().all()


def test_list_records_and_get_record_share_canonical_schema() -> None:
    response = _Response(_page("oai:example:1"))
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        return_value=response,
    ):
        bulk, _ = oai_extract_records(
            base_url="https://example.edu/oai",
            context="request",
            env="full",
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
        )
        recovered, errors, _ = oai_extract_records_by_identifiers(
            base_url="https://example.edu/oai",
            context="request",
            env="full",
            df_ids=pd.DataFrame({"record_id": ["oai:example:1"]}),
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
        )

    canonical_columns = [
        "record_id",
        "datestamp",
        "set_id",
        "col_id",
        "title",
        "date_issued",
        "creators",
        "description",
        "types",
        "identifiers",
        "languages",
        "subjects",
        "publishers",
        "relations",
        "rights",
        "formats",
    ]
    assert bulk[canonical_columns].to_dict("records") == recovered[
        canonical_columns
    ].to_dict("records")
    assert errors.empty
    assert recovered["_source_key"].unique().tolist() == ["example"]


def test_recover_records_audits_request_and_xml_errors() -> None:
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        side_effect=[None, _Response("<invalid")],
    ) as get_response:
        recovered, errors, preview = oai_extract_records_by_identifiers(
            base_url="https://example.edu/oai/",
            context="request",
            env="full",
            df_ids=pd.DataFrame(
                {"record_id": ["oai:example:one/two", "oai:example:bad"]}
            ),
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
        )

    assert recovered.empty
    assert preview.empty
    assert errors["error_type"].tolist() == ["request_failed", "invalid_xml"]
    assert errors["_source_key"].unique().tolist() == ["example"]
    assert "identifier=oai%3Aexample%3Aone%2Ftwo" in (
        get_response.call_args_list[0].args[0]
    )


def test_extract_records_can_resume_from_token() -> None:
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        return_value=_Response(_page("oai:example:19500")),
    ) as get_response:
        records, _ = oai_extract_records(
            base_url="https://example.edu/oai",
            context="request",
            env="full",
            source_key="example",
            repository_identifier="example.edu",
            institution_ror="https://ror.org/example",
            initial_resumption_token="oai_dc////19500",
        )

    assert records["record_id"].tolist() == ["oai:example:19500"]
    assert get_response.call_args.args[0].endswith(
        "?verb=ListRecords&resumptionToken=oai_dc////19500"
    )


def test_extract_records_fails_instead_of_saving_partial_harvest() -> None:
    with patch(
        "kedro_cic.pipelines.oai_extract.nodes.get_oai_response",
        return_value=None,
    ):
        try:
            oai_extract_records(
                base_url="https://example.edu/oai",
                context="request",
                env="full",
                source_key="example",
                repository_identifier="example.edu",
                institution_ror="https://ror.org/example",
            )
        except RuntimeError as error:
            assert "No se pudo completar la cosecha OAI" in str(error)
        else:
            raise AssertionError("La cosecha parcial debía fallar")
