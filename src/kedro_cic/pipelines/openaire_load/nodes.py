from datetime import date
import pandas as pd

_EXTRACTED_META_COLS = ["_filter_param", "_filter_value", "_extract_datetime"]

def _add_openaire_extracted_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in _EXTRACTED_META_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    return df

def _add_openaire_loaded_metadata(df: pd.DataFrame, load_datetime=None) -> pd.DataFrame:
    df = df.copy()
    if load_datetime is None:
        load_datetime = date.today()
    df["_load_datetime"] = load_datetime
    return df

def openaire_load_researchproduct(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    expected_columns = [
        'id',
        'openAccessColor',
        'publiclyFunded',
        'type',
        'language',
        'country',
        'mainTitle',
        'description',
        'publicationDate',
        'format',
        'bestAccessRight',
        'indicators',
        'isGreen',
        'isInDiamondJournal',
        'publisher',
        'source',
        'container',
        'contributor',
        'contactPerson',
        'coverage',
        'contactPerson',
        'embargoEndDate',
        'dateOfCollection',        
        '_filter_param',
        '_filter_value',
        '_extract_datetime',
    ]

    # Agregar columnas faltantes con NaN
    for col in expected_columns:
        if col not in df.columns:
            df[col] = pd.NA

    df = df.convert_dtypes()

    df_researchproduct = df[expected_columns].copy()
    df_researchproduct.reset_index(drop=True, inplace=True)

    # language
    df_researchproduct['language'] = df_researchproduct['language'].apply(
        lambda x: x if isinstance(x, dict) else {}
    )
    df_researchproduct['language_code'] = df_researchproduct['language'].apply(lambda x: x['code'])
    df_researchproduct['language_label'] = df_researchproduct['language'].apply(lambda x: x['label'])

    
    ## bestAccessRight
    df_researchproduct['bestAccessRight_label'] = df['bestAccessRight'].apply(lambda x: x['label'] if x else None)
    df_researchproduct['bestAccessRight_scheme'] = df['bestAccessRight'].apply(lambda x: x['scheme'] if x else None)

    ## indicators
    df_indicators = pd.json_normalize(df['indicators']).reset_index(drop=True)
    
    indicators_expected_columns = [
        "citationImpact.citationClass",
        "citationImpact.citationCount",
        "citationImpact.impulse",
        "citationImpact.impulseClass",
        "citationImpact.influence",
        "citationImpact.influenceClass",
        "citationImpact.popularity",
        "citationImpact.popularityClass",
        "usageCounts.downloads",
        "usageCounts.views",
    ]

    # Agregar columnas para indicators y faltantes con NaN
    for col in indicators_expected_columns:
        if col not in df_indicators.columns:
            df_indicators[col] = pd.NA

    df_researchproduct = pd.concat([df_researchproduct.drop(columns=['indicators']).reset_index(drop=True), df_indicators], axis=1)

    # TODO country
    # TODO description
    # TODO format
    # TODO instance
    # TODO container
    # TODO contributor
    # TODO contactPerson
    # TODO coverage

    ## drop de columnas procesadas en otros df
    df_researchproduct.drop(columns=[
        'country', 'bestAccessRight', 
        'language', 'format',  
        'container', 'source', 'description',
        'contributor', 'contactPerson', 'coverage'
        ], inplace=True)

    df_researchproduct = _add_openaire_loaded_metadata(df_researchproduct)

    return df_researchproduct

def openaire_load_researchproduct_authors(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_author = df[['id', 'authors', *_EXTRACTED_META_COLS]].explode('authors').reset_index(drop=True)

    df_authors = pd.json_normalize(df_research_author['authors'])

    df_research_author = pd.concat(
        [df_research_author[['id', *_EXTRACTED_META_COLS]].reset_index(drop=True), df_authors.reset_index(drop=True)],
        axis=1,
    )

    df_research_author = _add_openaire_loaded_metadata(df_research_author)

    return df_research_author

def openaire_load_researchproduct_collectedfrom(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_collectedfrom = df[['id', 'collectedFrom', *_EXTRACTED_META_COLS]].explode('collectedFrom').reset_index(drop=True)
    df_research_collectedfrom.rename(columns={'id':'researchproduct_id'}, inplace=True)

    df_collectedfrom = pd.json_normalize(df_research_collectedfrom['collectedFrom'])
    df_collectedfrom.rename(columns={'key':'datasource_id'}, inplace=True)

    df_research_collectedfrom = pd.concat(
        [
            df_research_collectedfrom[['researchproduct_id', *_EXTRACTED_META_COLS]].reset_index(drop=True),
            df_collectedfrom.loc[:,['datasource_id','value']].reset_index(drop=True),
        ],
        axis=1
    )

    df_research_collectedfrom = _add_openaire_loaded_metadata(df_research_collectedfrom)

    return df_research_collectedfrom

def openaire_load_researchproduct_contributors(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_contributor = df[['id', 'contributors', *_EXTRACTED_META_COLS]].explode('contributors').reset_index(drop=True)
    df_research_contributor.dropna(inplace=True)

    df_research_contributor = _add_openaire_loaded_metadata(df_research_contributor)

    return df_research_contributor

def openaire_load_researchproduct_descriptions(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_description = df[['id', 'descriptions', *_EXTRACTED_META_COLS]].explode('descriptions').reset_index(drop=True)

    df_research_description = _add_openaire_loaded_metadata(df_research_description)

    return df_research_description

def openaire_load_researchproduct_instances(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_instances = df[['id', 'instances', *_EXTRACTED_META_COLS]].explode('instances').reset_index(drop=True)

    df_instances = pd.json_normalize(df_research_instances['instances'])
    df_research_instances = pd.concat(
        [df_research_instances[['id', *_EXTRACTED_META_COLS]].reset_index(drop=True), df_instances.reset_index(drop=True)],
        axis=1,
    )

    df_research_instances = df_research_instances.explode('pids').reset_index(drop=True)

    df_research_instances = df_research_instances.explode('urls').reset_index(drop=True)

    df_pids = pd.json_normalize(df_research_instances['pids'])
    df_research_instances = df_research_instances.drop(columns=['pids'])

    df_research_instances = pd.concat([df_research_instances, df_pids], axis=1)

    df_research_alternateidentifiers = (
        df_research_instances[['id', 'alternateIdentifiers', *_EXTRACTED_META_COLS]]
        .dropna()
        .explode('alternateIdentifiers')
        .reset_index(drop=True)
    )
    df_alternateidentifiers = pd.json_normalize(df_research_alternateidentifiers['alternateIdentifiers'])
    df_research_alternateidentifiers = pd.concat(
        [
            df_research_alternateidentifiers[['id', *_EXTRACTED_META_COLS]].reset_index(drop=True),
            df_alternateidentifiers.reset_index(drop=True),
        ],
        axis=1,
    )

    df_research_instances.drop(columns=['alternateIdentifiers'], inplace=True)

    df_research_instances = _add_openaire_loaded_metadata(df_research_instances)
    df_research_alternateidentifiers = _add_openaire_loaded_metadata(df_research_alternateidentifiers)

    return df_research_instances, df_research_alternateidentifiers

def openaire_load_researchproduct_organizations(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_organization = df[['id', 'organizations', *_EXTRACTED_META_COLS]].explode('organizations').reset_index(drop=True)
    df_research_organization.rename(columns={'id':'researchproduct_id'}, inplace=True)

    df_organizations = pd.json_normalize(df_research_organization['organizations'])
    df_organizations.rename(columns={'id':'organization_id'}, inplace=True)

    df_research_organization = pd.concat(
        [
            df_research_organization[['researchproduct_id', *_EXTRACTED_META_COLS]].reset_index(drop=True),
            df_organizations['organization_id'].reset_index(drop=True),
        ],
        axis=1
    )

    df_organization_pid = df_organizations.loc[:, ['organization_id', 'pids']].copy()
    df_organizations.drop(columns=['pids'], inplace=True)
    df_organization_pid.dropna(inplace=True)

    df_organization_pid = df_organization_pid.explode('pids', ignore_index=True)
    df_organization_pid.loc[:, ['organization_id', 'pids']]

    df_pid = pd.json_normalize(df_organization_pid['pids'])
    df_pid.rename(columns={'scheme':'pid_scheme','value':'pid_value'}, inplace=True)

    df_organization_pid.drop(columns=['pids'], inplace=True)
    df_organization_pid = pd.concat([df_organization_pid, df_pid], axis=1)

    df_organizations = (
        df_organizations
        .drop_duplicates(subset="organization_id", keep="first")
        .reset_index(drop=True)
    )
    
    meta_vals = {
        col: (df_research_organization[col].iloc[0] if len(df_research_organization) else pd.NA)
        for col in _EXTRACTED_META_COLS
    }
    for col, val in meta_vals.items():
        df_organizations[col] = val
        df_organization_pid[col] = val

    df_organizations = _add_openaire_loaded_metadata(df_organizations)
    df_research_organization = _add_openaire_loaded_metadata(df_research_organization)
    df_organization_pid = _add_openaire_loaded_metadata(df_organization_pid)

    return df_organizations, df_research_organization, df_organization_pid

def openaire_load_researchproduct_originalid(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_originalids = df[['id', 'originalIds', *_EXTRACTED_META_COLS]]

    df_research_originalids = df_research_originalids.explode('originalIds').reset_index(drop=True)

    df_research_originalids = _add_openaire_loaded_metadata(df_research_originalids)

    return df_research_originalids

def openaire_load_researchproduct_pids(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)
    
    df_research_pid = df.loc[:,['id','pids', *_EXTRACTED_META_COLS]]
    df_research_pid.dropna(inplace=True)
    
    df_research_pid = df_research_pid.explode('pids').reset_index(drop=True)

    df_pid = pd.json_normalize(df_research_pid['pids'])
    
    df_research_pid = pd.concat(
        [df_research_pid[['id', *_EXTRACTED_META_COLS]].reset_index(drop=True), df_pid.reset_index(drop=True)],
        axis=1,
    )
    df_research_pid = _add_openaire_loaded_metadata(df_research_pid)

    return df_research_pid

def openaire_load_researchproduct_sources(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_sources = df.loc[:,['id','sources', *_EXTRACTED_META_COLS]]
    df_research_sources.dropna(inplace=True)
    
    df_research_sources = df_research_sources.explode('sources').reset_index(drop=True)

    df_research_sources = _add_openaire_loaded_metadata(df_research_sources)

    return df_research_sources

def openaire_load_researchproduct_subjects(df: pd.DataFrame)-> pd.DataFrame:
    df = _add_openaire_extracted_metadata(df)

    df_research_subjects = df.loc[:,['id','subjects', *_EXTRACTED_META_COLS]]
    df_research_subjects.dropna(inplace=True)

    df_research_subjects = df_research_subjects.explode('subjects').reset_index(drop=True)

    df_subjects = pd.json_normalize(df_research_subjects['subjects'])
    df_research_subjects = pd.concat(
        [df_research_subjects[['id', *_EXTRACTED_META_COLS]].reset_index(drop=True), df_subjects.reset_index(drop=True)],
        axis=1,
    )

    df_research_subjects = _add_openaire_loaded_metadata(df_research_subjects)

    return df_research_subjects
