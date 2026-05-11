# VOC Sedici

Guia de uso para la ingesta exploratoria de `voc.sedici` desde Drupal/MariaDB.

## Flujo

1. Levantar MariaDB local y restaurar el dump desde `dw-scholar/`.
2. Ejecutar `vocsedici_extract` para copiar tablas Drupal relevantes a parquet.
3. Ejecutar `vocsedici_load` para cargar esas mismas tablas en landing.
4. Modelar despues en dbt sobre `ldg_vocsedici`.

## Infra local

Desde [dw-scholar](/home/pablo/dev/scholar/kedro-scholar/dw-scholar):

```bash
make up-mariadb
make restore-voc
make up-adminer
```

Adminer queda disponible en `http://localhost:8080`.

## Pipelines Kedro

`vocsedici_extract`:
- copia tablas Drupal relevantes a `raw/voc/*.parquet`

`vocsedici_load`:
- vuelca esas tablas a `ldg/vocsedici/*`

## Tablas actuales

- `node`
- `node_field_data`
- `paragraphs_item`
- `paragraphs_item_field_data`
- `paragraph__field_persona_id`
- `paragraph__field_institucion`
- `paragraph__field_fecha_inicio`
- `paragraph__field_fecha_fin`
- `node__field_nombre`
- `node__field_apellido`
- `node__field_orcid`
- `node__field_mail`
- `node__field_dni`
- `node__field_cuit`
- `node__field_telefono`
- `node__field_direcci_n`
- `node__field_google_scholar`
- `node__field_researchgate`
- `node__field_old_id`
- `node__field_filiacion`
- `node__field_nombre_institucion`
- `node__field_nombre_institucion_variant`
- `node__field_abreviatura`
- `node__field_id_pidu`
- `node__field_id_termino`
- `node__field_padre`

## Criterio

Extract y landing conservan tablas crudas con metadata de proceso:
- `_extract_datetime`
- `_extract_date`
- `_filter_param`
- `_filter_value`
- `_source_table`
- `_load_datetime`

Los joins para `persona`, `institucion` y demas modelos quedan para dbt.

En particular, la relacion persona-institucion puede modelarse desde `paragraphs`:
- `paragraphs_item_field_data.parent_id` referencia el `nid` del nodo persona
- `paragraph__field_institucion.field_institucion_target_id` referencia el `nid` del nodo institucion
- `paragraph__field_fecha_inicio` y `paragraph__field_fecha_fin` permiten modelar vigencia
