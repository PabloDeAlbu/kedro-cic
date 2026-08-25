# Cosecha y carga OAI-PMH

Este documento describe el flujo reproducible para cosechar un repositorio
OAI-PMH, conservar el último snapshot en el área raw y cargarlo en el data
warehouse.

## Alcance

El pipeline trabaja actualmente con `metadataPrefix: oai_dc`. Recupera los
encabezados OAI y los metadatos Dublin Core expuestos por el repositorio. No
descarga bitstreams, archivos PDF ni metadatos internos que el proveedor OAI
no publique.

El área `data/01_raw/oai/` es temporal: una nueva ejecución reemplaza el
snapshot anterior. La identificación de la fuente viaja en las columnas de
procedencia y la historización corresponde al data warehouse.

## Configuración de una fuente

Los valores versionados de `conf/base/parameters_oai_extract.yml` funcionan
como ejemplo. Para trabajar con otra institución, crear el archivo ignorado
por Git `conf/local/parameters_oai_extract.yml`:

```yaml
oai_extract_options:
  source_key: example
  base_url: https://repositorio.example.edu/oai
  context: request
  repository_identifier: repositorio.example.edu
  institution_ror: https://ror.org/000000000
  metadata_prefix: oai_dc
  env: dev
```

`conf/local` pisa solamente los valores declarados allí. Los demás parámetros
se heredan de `conf/base` mediante la estrategia de mezcla `soft`.

Parámetros de control:

- `env`: en `dev` se aplican los límites de prueba; cualquier otro valor
  ejecuta con los límites completos.
- `dev_page_limit`: cantidad máxima de páginas por ventana en `dev`.
- `page_limit`: límite por ventana fuera de `dev`; `null` cosecha hasta agotar
  el `resumptionToken`.
- `dev_identifier_limit`: cantidad máxima de recuperaciones `GetRecord` en
  `dev`.
- `identifier_limit`: límite de recuperaciones fuera de `dev`; `null` intenta
  todos los faltantes.
- `initial_resumption_token`: permite reanudar manualmente una cosecha sin
  ventanas múltiples.
- `date_windows`: divide la consulta en intervalos independientes.

Cuando un proveedor falla siempre en una página, las ventanas temporales
evitan que el problema bloquee años o períodos independientes. Deben ser
adyacentes y no superponerse para facilitar la interpretación. Por ejemplo:

```yaml
oai_extract_options:
  env: full
  date_windows:
    - from: '2025-01-01'
      until: '2025-12-31'
    - from: '2026-01-01'
      until: '2026-12-31'
```

## Prueba acotada

Mantener `env: dev` y ejecutar:

```bash
kedro run --pipeline oai_extract
```

En este modo se cosechan como máximo `dev_page_limit` páginas por ventana y se
intentan como máximo `dev_identifier_limit` recuperaciones individuales. Sirve
para validar el endpoint, el XML, la forma de los datos y la procedencia; no
representa una cosecha completa.

## Cosecha completa

Definir en `conf/local/parameters_oai_extract.yml`:

```yaml
oai_extract_options:
  env: full
  page_limit: null
  identifier_limit: null
```

Luego ejecutar:

```bash
kedro run --pipeline oai_extract
```

El pipeline realiza estos pasos:

1. `ListIdentifiers` construye el manifiesto, incluidos los encabezados
   marcados como eliminados.
2. `ListRecords` recupera los registros por ventana.
3. Se comparan los registros obtenidos contra los identificadores activos.
4. Cada faltante se intenta recuperar mediante `GetRecord`.
5. Se consolidan la cosecha masiva y las recuperaciones individuales, sin
   duplicados por `record_id`.
6. Las páginas y registros que siguen fallando quedan auditados.

## Archivos producidos

| Archivo | Contenido |
| --- | --- |
| `identifiers.parquet` | Manifiesto global, estado de borrado y sets. |
| `records.parquet` | Snapshot consolidado que consume `oai_load`. |
| `missing_record_identifiers.parquet` | Faltantes detectados después de `ListRecords`. |
| `records_recovered.parquet` | Faltantes recuperados mediante `GetRecord`. |
| `record_page_errors.parquet` | Páginas de `ListRecords` que no pudieron procesarse. |
| `record_errors.parquet` | Identificadores que no pudieron recuperarse individualmente. |
| `*_dev.csv` | Muestras legibles para inspección manual. |

Todos se guardan bajo `data/01_raw/oai/` y no deben versionarse.

Los datasets principales incorporan las columnas `_source_key`,
`_repository_identifier`, `_institution_ror`, `_base_url`,
`_metadata_prefix`, `_context` y `_extract_datetime`.

## Controles posteriores

Este ejemplo calcula cobertura, duplicados y fallas sin modificar los datos:

```bash
python - <<'PY'
import pandas as pd

path = "data/01_raw/oai/"
identifiers = pd.read_parquet(path + "identifiers.parquet")
records = pd.read_parquet(path + "records.parquet")
errors = pd.read_parquet(path + "record_errors.parquet")

active = identifiers.loc[~identifiers["is_deleted"].fillna(False), "record_id"]
missing = active.loc[~active.isin(records["record_id"])]

print("identificadores:", len(identifiers))
print("activos:", len(active))
print("registros:", len(records))
print("duplicados:", records["record_id"].duplicated().sum())
print("faltantes finales:", len(missing))
print("errores auditados:", len(errors))
PY
```

Una cosecha puede considerarse utilizable aunque existan errores auditados,
siempre que se mida la cobertura y se conserve la lista de excepciones. Un
HTTP 500 de `GetRecord` es un problema del proveedor que debe investigarse en
el repositorio; no conviene inventar un registro ni descartarlo silenciosamente.

## Carga al data warehouse

Antes de cargar, verificar que `records.parquet` sea el snapshot esperado y
que las credenciales `dw` apunten al entorno correcto. Para cargar todos los
registros:

```bash
kedro run --pipeline oai_load --params oai_load_options.env=full
```

Con `oai_load_options.env=dev`, la carga de registros queda limitada a los
primeros 1.000. El pipeline normaliza las columnas multivaluadas y escribe las
tablas landing bajo `ldg_oai`. Los datasets usan reemplazo controlado del lote
landing; la historización debe continuar en las capas posteriores del data
warehouse antes de cosechar otra fuente.

## Contrato de entrega a dbt

Kedro entrega un único batch OAI al esquema PostgreSQL `ldg_oai`. Este esquema
es una zona de aterrizaje temporal: no conserva historia ni separa físicamente
las instituciones. Cada ejecución completa de `oai_load` trunca y repuebla las
tablas de forma independiente.

La separación lógica de fuentes se sostiene con `record_id` y las columnas de
procedencia. La historización comienza cuando el proyecto `dbt-scholar`
transforma este batch desde `models/01_ldg/oai/` y lo incorpora al Data Vault
de `models/02_dv/oai/`.

Las 14 tablas entregadas son:

| Tabla `ldg_oai` | Granularidad y función |
| --- | --- |
| `identifiers` | Una fila por encabezado OAI; incluye activos y eliminados. |
| `map_identifier_set` | Una fila por relación entre identificador y set. |
| `records` | Una fila por registro activo recuperado. |
| `map_record_creator` | Una fila por valor de autoría del registro. |
| `map_record_description` | Una fila por descripción. |
| `map_record_type` | Una fila por tipo documental. |
| `map_record_identifier` | Una fila por identificador publicado en Dublin Core. |
| `map_record_language` | Una fila por idioma. |
| `map_record_subject` | Una fila por materia o palabra clave. |
| `map_record_publisher` | Una fila por editor. |
| `map_record_relation` | Una fila por relación. |
| `map_record_right` | Una fila por declaración de derechos. |
| `map_record_format` | Una fila por formato. |
| `map_record_set` | Una fila por relación entre registro y set. |

Columnas que forman parte del contrato:

- `record_id` identifica el encabezado o registro dentro del proveedor OAI.
- `extract_datetime` conserva el instante de extracción originado en raw.
- `_source_key`, `_repository_identifier`, `_institution_ror`, `_base_url`,
  `_metadata_prefix` y `_context` describen la procedencia en las tablas
  principales `identifiers` y `records`.
- `_load_datetime` en las tablas del manifiesto, y `load_datetime` en las de
  registros, identifican la carga landing. Esta diferencia de nombres es parte
  del contrato actual y debe normalizarse en `models/01_ldg/oai/`.
- Las tablas multivaluadas pueden estar vacías si la fuente no publica ese
  elemento Dublin Core.

El orden operativo obligatorio es:

1. cosechar y reconciliar con `oai_extract`;
2. validar cobertura, duplicados, procedencia y errores;
3. cargar el batch en `ldg_oai` con `oai_load`;
4. ejecutar y validar los modelos OAI de `dbt-scholar` hasta el Data Vault;
5. recién entonces cosechar otra fuente o reemplazar raw y landing.

No debe iniciarse el paso 5 solamente porque `oai_load` terminó: primero hay
que comprobar que dbt incorporó el batch al Data Vault. Además, como las 14
escrituras landing no forman una única transacción, una falla intermedia puede
dejar tablas pertenecientes a cargas diferentes. Después de cada ejecución se
deben contrastar conteos, procedencia y timestamps antes de ejecutar dbt.

Control mínimo en PostgreSQL:

```sql
select
    count(*) as records,
    count(distinct record_id) as unique_records,
    min(extract_datetime) as min_extract_datetime,
    max(extract_datetime) as max_extract_datetime,
    min(load_datetime) as min_load_datetime,
    max(load_datetime) as max_load_datetime,
    string_agg(distinct _source_key, ', ') as sources
from ldg_oai.records;

select
    count(*) as identifiers,
    count(*) filter (where is_deleted) as deleted,
    count(*) filter (where not is_deleted) as active,
    count(*) filter (
        where not is_deleted and records.record_id is null
    ) as active_without_record
from ldg_oai.identifiers
left join ldg_oai.records using (record_id);
```

Los faltantes activos deben coincidir con `record_errors.parquet`. Cualquier
diferencia indica una carga incompleta o una mezcla accidental de batches.

## Reanudar y diagnosticar

Para ejecutar solamente un nodo y sus dependencias persistidas se pueden usar
`--nodes` o `--from-nodes`. La ejecución normal recomendada sigue siendo el
pipeline completo, porque la consolidación depende del manifiesto y de la
cosecha masiva de la misma ejecución.

Ejemplos:

```bash
kedro run --pipeline oai_extract --nodes oai_extract_identifiers
kedro run --pipeline oai_extract --from-nodes oai_extract_records
```

`initial_resumption_token` es una herramienta de diagnóstico o reanudación.
No puede combinarse con más de una ventana temporal, porque cada ventana tiene
su propia secuencia de tokens.

## Notebooks de desarrollo

Los notebooks de `notebooks/sources/oai/` permiten ejecutar las funciones por
separado, inspeccionar sus resultados y ensayar cambios antes de trasladarlos
a `nodes.py`. No escriben en PostgreSQL y se versionan sin outputs ni
contadores de ejecución.

Extracción:

- `01_extract/oai_extract_get_oai_response.ipynb` prueba el cliente HTTP.
- `01_extract/oai_extract_identifiers.ipynb` prueba el manifiesto.
- `01_extract/oai_extract_records.ipynb` prueba la cosecha masiva.
- `01_extract/oai_extract_records_by_identifiers.ipynb` prueba `GetRecord`.
- `01_extract/oai_reconcile_records.ipynb` prueba faltantes y consolidación.

Carga:

- `02_load/oai_load_identifiers.ipynb` muestra las dos tablas del manifiesto.
- `02_load/oai_load_records.ipynb` muestra las doce tablas de registros.

Cada definición ocupa una celda propia y debe coincidir con su implementación
en `nodes.py`. Los notebooks de extracción se regeneran desde ese código con:

```bash
python notebooks/sources/oai/sync_notebooks.py
```

El regenerador sirve para restablecer la sincronía y limpiar todas las celdas.
Como sobrescribe los notebooks activos de extracción, cualquier experimento
que deba conservarse tiene que trasladarse primero a `nodes.py` y sus tests.
