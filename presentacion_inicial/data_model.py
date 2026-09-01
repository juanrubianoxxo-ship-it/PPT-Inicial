from pathlib import Path
import re
import pandas as pd

SHEETS = ['JUN','Hoja3','LAST','PTM','Hoja1','EOD 071025','Hoja2']

def clean_number(v):
    if pd.isna(v): return None
    if isinstance(v,(int,float)): return float(v)
    s=str(v).replace('$','').replace('.','').replace(',','').strip()
    try: return float(s)
    except Exception: return None

def read_book(source):
    """Carga las hojas del libro y normaliza la hoja operativa JUN."""
    sheets = {s: pd.read_excel(source, sheet_name=s) for s in SHEETS}
    jun=sheets.get('JUN', pd.DataFrame()).copy()
    for c in ['VENTAS OUM','VENTAS OU6M','CONTRIBUCION UM','CONTRIBUCION U6M','RENTA UM','RENTA U6M','AREA','TRAFICO UM','TRAFICO U6M','TR15MIN','MESOP','COSTO M2']:
        if c in jun.columns:
            jun[c+'_NUM']=pd.to_numeric(jun[c].map(clean_number), errors='coerce')
    sheets['JUN']=jun
    return sheets

def values(df, column):
    if df is None or column not in df: return []
    return sorted(df[column].dropna().astype(str).str.strip().replace('',pd.NA).dropna().unique().tolist())

def filter_jun(sheets, city='', upz='', store=''):
    df=sheets.get('JUN',pd.DataFrame()).copy()
    if city and 'MUNICIPIO' in df: df=df[df['MUNICIPIO'].astype(str).str.strip()==city]
    if upz and 'UPZ/COMUNA' in df: df=df[df['UPZ/COMUNA'].astype(str).str.strip()==upz]
    if store and 'NAME' in df: df=df[df['NAME'].astype(str).str.strip()==store]
    return df

def aggregate_metrics(df):
    out={'Número de tiendas':len(df)}
    for label,col in [('Renta promedio','RENTA UM_NUM'),('Venta promedio','VENTAS OUM_NUM'),('Contribución promedio','CONTRIBUCION UM_NUM'),('Tráfico promedio','TRAFICO UM_NUM'),('Área promedio','AREA_NUM'),('Tráfico 15 min','TR15MIN_NUM')]:
        out[label]=round(float(df[col].mean()),2) if col in df and df[col].notna().any() else None
    return out

def summary_table(df, n=6):
    cols=[c for c in ['NAME','SEG26','TIE27','MESOP','VENTAS OUM_NUM','RENTA UM_NUM','AREA_NUM','GENERADOR','ESTADO','PTH','TR15MIN_NUM'] if c in df]
    x=df[cols].head(n).copy()
    # The Book mixes numeric and text store names; normalize object columns so
    # Streamlit/Arrow can serialize the preview without type inference errors.
    for column in x.select_dtypes(include=['object']).columns:
        x[column] = x[column].fillna('').astype(str)
    rename={'NAME':'Tienda','SEG26':'Segmento','TIE27':'Clasificación','MESOP':'Meses op.','VENTAS OUM_NUM':'Ventas','RENTA UM_NUM':'Renta','AREA_NUM':'Área m²','GENERADOR':'Generador','ESTADO':'Estado','PTH':'Potencial','TR15MIN_NUM':'Tráfico 15 min'}
    return x.rename(columns=rename)

def environment_summary(sheets, store=''):
    df=sheets.get('EOD 071025',pd.DataFrame()).copy()
    if 'Tienda de Estudio' in df and store:
        candidates=[store, 'BOG_'+store]
        match=df[df['Tienda de Estudio'].astype(str).isin(candidates)]
        if not match.empty: df=match
    result={}
    if '¿Qué hace en la zona?' in df and 'Radio' in df:
        p=pd.crosstab(df['¿Qué hace en la zona?'],df['Radio'])
        for activity in p.index:
            result[str(activity)]={str(k):int(v) for k,v in p.loc[activity].to_dict().items()}
    return result
