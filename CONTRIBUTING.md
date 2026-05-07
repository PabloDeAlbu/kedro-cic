# Contribuir

Guía corta para mantener una forma consistente de trabajar en `kedro-scholar`.

## Idea general

Este repositorio usa Kedro para extraer, transformar y cargar datos de fuentes académicas abiertas hacia capas de landing, integración y consumo analítico.

Regla práctica:

- los cambios de extracción y carga suelen vivir en `src/kedro_cic/pipelines/`
- los datasets y rutas viven en `conf/base/catalog.yml`
- los parámetros compartidos viven en `conf/base/parameters*.yml`
- las credenciales y secretos van sólo en `conf/local/`
- las notebooks sirven para explorar o prototipar lógica antes de pasarla a nodos reutilizables

## Flujo de trabajo recomendado

Para desarrollo diario:

1. hacer cambios acotados por pipeline o por fuente
2. probar con el selector más chico posible
3. pasar la lógica estable desde notebook a `nodes.py` cuando corresponda
4. revisar `git status` antes de versionar

Ejemplos:

```bash
kedro run --pipeline openalex_load
kedro run --tags gs_load
kedro jupyter lab
```

## Dónde va cada cambio

### Pipelines

Cada pipeline vive en `src/kedro_cic/pipelines/<pipeline_name>/` y normalmente incluye:

- `pipeline.py`: definición de nodos, inputs, outputs y tags
- `nodes.py`: lógica de transformación
- `__init__.py`: export del pipeline

Si agregás un pipeline nuevo, también hay que registrarlo en:

- `src/kedro_cic/pipeline_registry.py`

### Catálogo

Si una fuente nueva necesita archivos, tablas o salidas nuevas, hay que agregarlas en:

- `conf/base/catalog.yml`

La convención general del repo distingue:

- `raw/...`: archivos o datos crudos
- `intermediate/...`: salidas intermedias de trabajo
- `ldg/...`: carga landing en base de datos

### Notebooks

Las notebooks pueden usarse para:

- inspeccionar fuentes
- iterar sobre parseos o transformaciones
- validar un nodo antes de moverlo al pipeline

No conviene dejar lógica crítica sólo en notebook si después se necesita correr en Kedro.

## Criterios de modelado prácticos

- en `ldg`, priorizar la carga más simple y estable posible
- si una transformación compleja puede resolverse mejor en SQL o `dbt`, conviene preservar el dato y delegarla aguas abajo
- conservar contexto técnico cuando aplique, por ejemplo `_load_datetime` u otros metadatos de extracción
- evitar mezclar cambios no relacionados en un mismo commit

## Convención de commits

El formato buscado es:

`tipo(scope) mensaje`

Ejemplos:

- `feat(gs load) agrega pipeline para carga de html de autores de google scholar`
- `fix(openalex load) corrige tipado de author topics`
- `refactor(dspacedb load) simplifica mapeo de metadatos`
- `docs(repo) agrega guia inicial de contribucion`

Tipos sugeridos:

- `feat`: nueva funcionalidad o nuevo pipeline
- `fix`: corrección de bug
- `refactor`: cambio estructural sin cambio funcional intencional
- `docs`: documentación
- `test`: tests
- `chore`: tareas de mantenimiento

Scopes sugeridos:

- `repo`
- `dev`
- nombre de pipeline o dominio, por ejemplo `gs load`, `openalex load`, `oai extract`

## Antes de versionar

- confirmar que no haya secretos en `conf/base/`
- revisar que el commit incluya sólo el alcance buscado
- correr al menos la prueba mínima relevante del cambio
- si el cambio nació en notebook y se va a usar en ejecución real, mover la lógica final al pipeline

