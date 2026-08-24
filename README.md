# kedro-cic

Pipelines and notebooks to ingest, integrate, and curate scientometric/bibliometric data from open scholarly sources (Kedro 1.1.1).

## Context
This repository implements (as part of the thesis work) a data integration architecture for institutional *Open Science* analytics and decision support. From a modeling perspective, it combines:
- **Integration** using **Data Vault 2.0** (normalization, lineage/traceability, and historization).
- **Presentation/consumption** using a **dimensional model** (star-schema data marts).

Layer-wise, the typical flow is: extraction/landing (raw/`ldg_`) → integration (DV/`dv_`) → exposure (DM/`dm_`).

## Quick requirements
- Python 3.10+ and `pip`.
- Install dependencies: `pip install -r requirements.txt`
- Sensitive configuration in `conf/local/` (not versioned): tokens, credentials, DSNs, and source-specific filters.

## Running
- By default, the project runs in `dev` mode (useful to iterate faster and avoid large loads). To change it for a single run, override the corresponding `...env` parameter via `--params`.
- Run the full project: `kedro run`
- Run a specific pipeline (e.g., OAI load): `kedro run --pipeline oai_load`
- Force `dev` for a single run: `kedro run --params oai_load_options.env=dev`
- Force `prod` for a single run: `kedro run --params oai_load_options.env=prod`

## Available pipelines
Pipeline names match the modules in `src/kedro_cic/pipelines/`:
- OAI-PMH: `oai_extract`, `oai_load`
- OpenAIRE: `openaire_extract`, `openaire_load`
- OpenAlex: `openalex_extract`, `openalex_load`
- DSpace DB: `dspacedb`

Examples:
- Harvest OAI-PMH: `kedro run --pipeline oai_extract`
- Download/ingest OpenAlex: `kedro run --pipeline openalex_extract`
- Load OpenAIRE: `kedro run --pipeline openaire_load`

## Visualization (Kedro-Viz)
- Start Kedro-Viz: `kedro viz`

## OAI-PMH por fuente

El área raw conserva el último snapshot OAI descargado, independientemente de
la institución:

```text
data/01_raw/oai/identifiers.parquet
data/01_raw/oai/records.parquet
```

La configuración local define la procedencia que se incorpora a cada fila:

```yaml
# conf/local/parameters_oai_extract.yml
oai_extract_options:
  source_key: uca
  base_url: https://repositorio.uca.edu.ar/oai
  context: request
  repository_identifier: repositorio.uca.edu.ar
  institution_ror: https://ror.org/0422kzb24
  metadata_prefix: oai_dc
  dev_page_limit: 2
  env: dev
```

La prueba acotada de registros se ejecuta en dos pasos:

```bash
kedro run --pipeline oai_extract --nodes oai_extract_records
kedro run --pipeline oai_load --nodes oai_load_records
```

El modo `dev` limita la extracción a `dev_page_limit` páginas y la carga a un
máximo de 1.000 registros. La tabla landing conserva solamente el último
batch; debe procesarse aguas abajo antes de cargar otra fuente.

## Notebooks
- Start an interactive environment: `kedro jupyter lab` (or `kedro jupyter notebook`).

## Pre-merge checklist
- Ensure tokens/credentials live only in `conf/local/` (and that no secrets are hardcoded in `conf/base/`).
- Run the key pipelines or notebooks you plan to use in `main`.
- Check `git status` to confirm the changes are the expected ones before opening a PR/merging.
