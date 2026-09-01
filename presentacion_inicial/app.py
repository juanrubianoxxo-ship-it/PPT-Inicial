from base64 import b64decode, b64encode
from datetime import date, datetime, timezone
import json
import math
import mimetypes
import re
from pathlib import Path

import streamlit as st

from data_model import read_book, values, filter_jun, summary_table

ROOT = Path(__file__).parent
SECTIONS = [
    'Portada',
    'General',
    'Entorno | Generadores Vivienda',
    'Entorno | Generadores Empleo',
    'Expansión | Mercado y Tráfico',
    'Tienda Hermana',
    'Condiciones comerciales',
]
SPECIALISTS = [
    'ANDRES DUQUE RESTREPO', 'JURY CAROLINA GONZALEZ GOMEZ', 'JENNY ACUNA ROJAS',
    'LINA DIAZ ORTIZ', 'MARTHA LILIANA LOPEZ CANDAMIL', 'JORGE GRANADOS',
    'CARLOS BOLAÑOS DIAZ', 'ALEJANDRA ROJAS ROMERO', 'ELVIA JAIMES VELASQUEZ',
    'LAURA SOFÍA VECINO MARRUGO',
]
GENERATOR_TYPES = ['Administrativo', 'Residencial', 'Comercial', 'Industrial', 'Educativo', 'Salud', 'Transporte masivo']
YES_NO = ['SI', 'NO']
IPC_OPTIONS = ['PLANO', '+1', '+2', '+3']
MONTHS = ['', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

st.set_page_config(page_title='Presentación Inicial', page_icon='📊', layout='wide', initial_sidebar_state='expanded')
st.markdown('''
<style>
.block-container { max-width: 1400px; padding-top: 2rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #f7f7f8; border-right: 1px solid #e5e5e5; }
.hero { padding: 1.5rem 1.8rem; border-radius: 16px; background: linear-gradient(135deg,#d71920,#99131a); color: white; margin-bottom: 1.25rem; box-shadow: 0 8px 24px rgba(100,0,0,.16); }
.hero h1 { color: white; margin: 0 0 .35rem; font-size: 2.2rem; }
.hero p { color: white; opacity: .92; margin: 0; }
div[data-testid="stExpander"] { border-radius: 12px; border: 1px solid #e0e3e7; background: white; margin-bottom: .65rem; }
</style>
<div class="hero"><h1>Presentación Inicial</h1><p>Construye, guarda y genera la presentación de un nuevo punto comercial.</p></div>
''', unsafe_allow_html=True)
st.caption('Completa únicamente las siete secciones del formulario. Book.xlsx se usa como fuente de referencia para filtros, tiendas y métricas.')

@st.cache_data
def load_book(source):
    return read_book(source)

def as_bytes(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if hasattr(value, 'getvalue'):
        return value.getvalue()
    return None

def json_safe(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)

def encode_image(value, filename='imagen'):
    raw = as_bytes(value)
    return {'name': filename, 'data_base64': b64encode(raw).decode('ascii')} if raw else None

def decode_image(value):
    encoded = value.get('data_base64', '') if isinstance(value, dict) else value
    if not encoded:
        return None
    if isinstance(encoded, bytes):
        return encoded
    if isinstance(encoded, str) and encoded.startswith('data:') and ',' in encoded:
        encoded = encoded.split(',', 1)[1]
    try:
        return b64decode(''.join(str(encoded).split()), validate=True)
    except Exception:
        return None

def build_payload(fields, images, names):
    exported = {}
    for key, value in images.items():
        item = encode_image(value, names.get(key, key))
        if item:
            exported[key] = item
    return json.dumps({
        'format': 'presentacion-inicial-streamlit',
        'version': 2,
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'fields': json_safe(fields),
        'images': exported,
    }, ensure_ascii=False, indent=2).encode('utf-8')

def restore_payload(upload):
    payload = json.loads(upload.getvalue().decode('utf-8-sig'))
    fields = payload.get('fields', {})
    if not isinstance(fields, dict):
        raise ValueError('El JSON no contiene campos válidos.')
    images, names = {}, {}
    for key, item in (payload.get('images', {}) or {}).items():
        raw = decode_image(item)
        if raw:
            images[key] = raw
            names[key] = item.get('name', key) if isinstance(item, dict) else key
    return fields, images, names

def upload_image(label, key):
    uploaded = st.file_uploader(label, type=['png', 'jpg', 'jpeg', 'webp'], key=f'upload_{key}')
    if uploaded is not None:
        st.session_state.images[key] = uploaded.getvalue()
        st.session_state.image_names[key] = uploaded.name
    if st.session_state.images.get(key):
        st.caption(f"Imagen registrada: {st.session_state.image_names.get(key, 'imagen')}")
        st.image(st.session_state.images[key], width='stretch')

def money(value):
    try:
        return f"${float(value):,.0f}".replace(',', '.')
    except Exception:
        return '—'

def number(value):
    try:
        return f"{float(value):,.0f}".replace(',', '.')
    except Exception:
        return '—'

def image_data(raw):
    if not raw:
        return ''
    mime = mimetypes.guess_type('imagen.png')[0] or 'image/png'
    return f'data:{mime};base64,{b64encode(raw).decode("ascii")}'

def html_page(fields, sheets, images):
    project = fields.get('project_name') or 'Nuevo proyecto'
    city = fields.get('new_city') if fields.get('city') == 'Ciudad nueva' else fields.get('city', '')
    upz = fields.get('new_upz') if fields.get('upz') == 'UPZ / comuna nueva' else fields.get('upz', '')
    rows = ''
    try:
        preview = summary_table(filter_jun(sheets, fields.get('city', ''), fields.get('upz', '')))
        rows = ''.join('<tr>' + ''.join(f'<td>{str(v)}</td>' for v in row) + '</tr>' for row in preview.fillna('').values.tolist())
        headers = ''.join(f'<th>{c}</th>' for c in preview.columns)
    except Exception:
        headers, rows = '', ''
    def img(key, alt='Imagen'):
        return f'<img src="{image_data(images.get(key))}" alt="{alt}">' if images.get(key) else '<div class="placeholder">Sin imagen</div>'
    def cards(group):
        return ''.join(f'''<div class="card"><h3>{c.get('name') or 'Generador sin nombre'}</h3><p><b>Tipo:</b> {c.get('type','—')} &nbsp; <b>Asociado:</b> {number(c.get('value',0))}</p></div>''' for c in fields.get(f'generator_{group}_cards', []))
    rent_m2 = fields.get('project_rent_m2', 0)
    sections = [
        ('Portada', f'<h1>Presentación Inicial</h1><h2>{project}</h2><p><b>Región:</b> {fields.get("regional", "—")} &nbsp; <b>Segmento:</b> {fields.get("segment", "—")}</p><p><b>Dirección:</b> {fields.get("address", "—")}<br><b>Especialista:</b> {fields.get("specialist", "—")}</p>'),
        ('General', f'<h2>General</h2><p><b>Ciudad:</b> {city or "—"} &nbsp; <b>UPZ / comuna:</b> {upz or "—"}</p><p>{fields.get("plan_comments", "")}</p>{img("general_environment_image", "Entorno general")}'),
        ('Entorno | Generadores Vivienda', f'<h2>Generadores Vivienda</h2>{cards("housing")}'),
        ('Entorno | Generadores Empleo', f'<h2>Generadores Empleo</h2>{cards("employment")}'),
        ('Expansión | Mercado y Tráfico', f'<h2>Mercado y Tráfico</h2><div class="metrics"><div>Viviendas a 100 m<strong>{number(fields.get("housing_100"))}</strong></div><div>Viviendas a 300 m<strong>{number(fields.get("housing_300"))}</strong></div><div>Empleos a 100 m<strong>{number(fields.get("jobs_100"))}</strong></div><div>Empleos a 300 m<strong>{number(fields.get("jobs_300"))}</strong></div></div><p><b>Tráfico peatonal:</b> {fields.get("pedestrian_15","—")} &nbsp; <b>Vehicular:</b> {fields.get("vehicle_15","—")} &nbsp; <b>Motos:</b> {fields.get("motorcycle_15","—")}</p>'),
        ('Tienda Hermana', f'<h2>Tienda Hermana</h2><p><b>Tienda espejo:</b> {fields.get("book_store", "—")}</p><p>{fields.get("similar_comments", "")}</p>{img("similar_image", "Tienda hermana")}'),
        ('Condiciones comerciales', f'<h2>Condiciones comerciales</h2><table><tr><td>Vigencia</td><td>{fields.get("commercial_vigencia","—")}</td></tr><tr><td>Permanencia</td><td>{fields.get("commercial_permanencia","—")}</td></tr><tr><td>IPC</td><td>{fields.get("commercial_ipc","—")}</td></tr><tr><td>Renta del proyecto</td><td>{money(fields.get("project_rent"))}</td></tr><tr><td>Área</td><td>{number(fields.get("project_area"))} m²</td></tr><tr><td>Renta / m²</td><td>{money(rent_m2)}</td></tr><tr><td>Firma / Entrega / Apertura</td><td>{fields.get("signature","—")} / {fields.get("delivery_date","—")} / {fields.get("opening_date","—")}</td></tr></table>'),
    ]
    body = ''.join(f'<section><div class="section-title">{i+1}. {title}</div>{content}</section>' for i, (title, content) in enumerate(sections))
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{project} | Presentación Inicial</title><style>body{{font-family:Arial,sans-serif;color:#202124;background:#f3f4f6;margin:0}}main{{max-width:1100px;margin:auto}}header{{background:#d71920;color:#fff;padding:42px 52px}}header h1{{margin:0}}section{{background:#fff;margin:22px 0;padding:30px 38px;min-height:260px;box-shadow:0 2px 10px #ddd}}.section-title{{color:#d71920;font-size:14px;font-weight:bold;text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px}}h2{{margin-top:0}}img{{max-width:100%;max-height:320px;display:block;margin-top:18px;border-radius:8px}}.placeholder{{margin-top:18px;padding:38px;background:#f1f2f4;color:#777;text-align:center;border-radius:8px}}.card{{display:inline-block;vertical-align:top;width:43%;margin:1%;padding:14px;background:#f7f7f8;border-radius:8px}}.metrics{{display:flex;gap:12px;flex-wrap:wrap}}.metrics div{{background:#f7f7f8;padding:18px;border-radius:8px;min-width:170px}}.metrics strong{{display:block;font-size:24px;margin-top:8px;color:#d71920}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:9px;text-align:left}}th{{background:#f3f3f3}}</style></head><body><header><main><h1>Presentación Inicial</h1><p>{project}</p></main></header><main>{body}{f"<section><div class=\"section-title\">Referencia de Book.xlsx</div><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></section>" if headers else ""}</main></body></html>'''

if 'fields' not in st.session_state:
    st.session_state.fields = {'created_at': date.today().strftime('%d/%m/%Y')}
if 'images' not in st.session_state:
    st.session_state.images = {}
if 'image_names' not in st.session_state:
    st.session_state.image_names = {}
f = st.session_state.fields
imgs = st.session_state.images
names = st.session_state.image_names

book_path = ROOT / 'Book.xlsx'
sheets = load_book(book_path) if book_path.exists() else {}
jun = sheets.get('JUN')

with st.sidebar:
    st.header('Presentación Inicial')
    selected = st.radio('Secciones', SECTIONS, index=0)
    st.divider()
    st.subheader('Guardar / restaurar')
    json_upload = st.file_uploader('Cargar JSON', type=['json'], key='json_import')
    if json_upload is not None and st.button('Restaurar información', use_container_width=True):
        try:
            st.session_state.fields, st.session_state.images, st.session_state.image_names = restore_payload(json_upload)
            st.rerun()
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            st.error(f'No se pudo cargar el JSON: {exc}')
    if jun is not None:
        st.success(f'Book.xlsx cargado · {len(jun):,} registros')

if selected == 'Portada':
    with st.expander('Portada', expanded=True):
        f['regional'] = st.selectbox('Región', ['Centro', 'Nororiente', 'Occidente'], index=['Centro','Nororiente','Occidente'].index(f.get('regional','Centro')) if f.get('regional','Centro') in ['Centro','Nororiente','Occidente'] else 0)
        f['project_name'] = st.text_input('Nombre del proyecto', f.get('project_name',''))
        f['segment'] = st.selectbox('Segmento', ['Receso','Base','Hogar'], index=['Receso','Base','Hogar'].index(f.get('segment','Base')) if f.get('segment','Base') in ['Receso','Base','Hogar'] else 1)
        f['specialist'] = st.selectbox('Especialista', SPECIALISTS, index=SPECIALISTS.index(f.get('specialist',SPECIALISTS[0])) if f.get('specialist',SPECIALISTS[0]) in SPECIALISTS else 0)
        f['address'] = st.text_input('Dirección', f.get('address',''))
        f['maps_link'] = st.text_input('Link de Maps', f.get('maps_link',''))
        st.caption(f"Fecha de creación: {f.get('created_at', date.today().strftime('%d/%m/%Y'))}")

elif selected == 'General':
    with st.expander('General', expanded=True):
        city_options = [''] + values(jun, 'MUNICIPIO') if jun is not None else ['']
        if 'Ciudad nueva' not in city_options: city_options.append('Ciudad nueva')
        city = st.selectbox('Ciudad / municipio', city_options, index=city_options.index(f.get('city','')) if f.get('city','') in city_options else 0)
        cdf = jun[jun['MUNICIPIO'].astype(str).str.strip() == city] if jun is not None and city and city != 'Ciudad nueva' else (None if city == 'Ciudad nueva' else jun)
        upz_options = [''] + values(cdf, 'UPZ/COMUNA') if cdf is not None else ['']
        if 'UPZ / comuna nueva' not in upz_options: upz_options.append('UPZ / comuna nueva')
        upz = st.selectbox('UPZ / comuna', upz_options, index=upz_options.index(f.get('upz','')) if f.get('upz','') in upz_options else 0)
        f['city'], f['upz'] = city, upz
        if city == 'Ciudad nueva': f['new_city'] = st.text_input('Ciudad nueva / municipio', f.get('new_city',''))
        if upz == 'UPZ / comuna nueva': f['new_upz'] = st.text_input('UPZ / comuna nueva', f.get('new_upz',''))
        upload_image('Foto de entorno general', 'general_environment_image')
        f['plan_comments'] = st.text_area('Comentarios del plan rector', f.get('plan_comments',''))
        if jun is not None: st.dataframe(summary_table(filter_jun(sheets, city, upz)), use_container_width=True, hide_index=True)

elif selected in ('Entorno | Generadores Vivienda', 'Entorno | Generadores Empleo'):
    group = 'housing' if selected.endswith('Vivienda') else 'employment'
    with st.expander(selected, expanded=True):
        st.caption('Registra hasta cuatro generadores asociados.')
        cards = f.get(f'generator_{group}_cards', [{}, {}, {}, {}])
        while len(cards) < 4: cards.append({})
        for i in range(4):
            st.markdown(f'**Generador {i+1}**')
            a, b, c = st.columns([1, 2, 2])
            with a: upload_image(f'Foto {i+1}', f'generator_{group}_image_{i+1}')
            old = cards[i] if isinstance(cards[i], dict) else {}
            with b: name = st.text_input('Nombre', old.get('name',''), key=f'{group}_name_{i}')
            with c:
                typ = st.selectbox('Tipo', GENERATOR_TYPES, index=GENERATOR_TYPES.index(old.get('type')) if old.get('type') in GENERATOR_TYPES else 0, key=f'{group}_type_{i}')
                val = st.number_input('Cantidad aproximada', min_value=0.0, value=float(old.get('value', 0) or 0), key=f'{group}_value_{i}')
            cards[i] = {'name': name, 'type': typ, 'value': val}
        f[f'generator_{group}_cards'] = cards

elif selected == 'Expansión | Mercado y Tráfico':
    with st.expander(selected, expanded=True):
        f['housing_100'] = st.number_input('Viviendas a 100 m', min_value=0.0, value=float(f.get('housing_100',0) or 0))
        f['housing_300'] = st.number_input('Viviendas a 300 m', min_value=0.0, value=float(f.get('housing_300',0) or 0))
        f['jobs_100'] = st.number_input('Empleos a 100 m', min_value=0.0, value=float(f.get('jobs_100',0) or 0))
        f['jobs_300'] = st.number_input('Empleos a 300 m', min_value=0.0, value=float(f.get('jobs_300',0) or 0))
        f['generator_type'] = st.selectbox('Tipo de generador principal', GENERATOR_TYPES, index=GENERATOR_TYPES.index(f.get('generator_type')) if f.get('generator_type') in GENERATOR_TYPES else 0)
        c1, c2, c3 = st.columns(3)
        with c1: f['pedestrian_15'] = st.text_input('Tráfico peatonal', f.get('pedestrian_15',''))
        with c2: f['vehicle_15'] = st.text_input('Tráfico vehicular', f.get('vehicle_15',''))
        with c3: f['motorcycle_15'] = st.text_input('Tráfico de motos', f.get('motorcycle_15',''))

elif selected == 'Tienda Hermana':
    with st.expander('Tienda Hermana', expanded=True):
        open_stores = values(jun[jun['ESTADO'].astype(str).str.upper().str.contains('ABIERTA', na=False)], 'NAME') if jun is not None and 'ESTADO' in jun else values(jun, 'NAME')
        options = [''] + open_stores
        f['book_store'] = st.selectbox('Tienda abierta espejo', options, index=options.index(f.get('book_store','')) if f.get('book_store','') in options else 0)
        upload_image('Foto de Tienda Hermana', 'similar_image')
        f['similar_comments'] = st.text_area('Comentarios', f.get('similar_comments',''))

elif selected == 'Condiciones comerciales':
    with st.expander('Condiciones comerciales', expanded=True):
        f['commercial_vigencia'] = st.text_input('Vigencia', f.get('commercial_vigencia',''))
        f['commercial_permanencia'] = st.selectbox('Permanencia', YES_NO, index=YES_NO.index(str(f.get('commercial_permanencia','NO')).upper()) if str(f.get('commercial_permanencia','NO')).upper() in YES_NO else 1)
        f['commercial_gracia'] = st.text_input('Periodo de gracia (días)', f.get('commercial_gracia',''))
        f['commercial_preop'] = st.text_input('Pre-operativos', f.get('commercial_preop',''))
        f['commercial_ipc'] = st.selectbox('IPC', IPC_OPTIONS, index=IPC_OPTIONS.index(f.get('commercial_ipc','PLANO')) if f.get('commercial_ipc','PLANO') in IPC_OPTIONS else 0)
        f['commercial_operacion'] = st.selectbox('Operación 24 horas', YES_NO, index=YES_NO.index(str(f.get('commercial_operacion','NO')).upper()) if str(f.get('commercial_operacion','NO')).upper() in YES_NO else 1)
        f['commercial_alcohol'] = st.selectbox('Venta de alcohol', YES_NO, index=YES_NO.index(str(f.get('commercial_alcohol','NO')).upper()) if str(f.get('commercial_alcohol','NO')).upper() in YES_NO else 1)
        f['commercial_prima'] = st.selectbox('Prima', YES_NO, index=YES_NO.index(str(f.get('commercial_prima','NO')).upper()) if str(f.get('commercial_prima','NO')).upper() in YES_NO else 1)
        f['commercial_anticipo'] = st.selectbox('Anticipo', YES_NO, index=YES_NO.index(str(f.get('commercial_anticipo','NO')).upper()) if str(f.get('commercial_anticipo','NO')).upper() in YES_NO else 1)
        f['commercial_clausulas'] = st.selectbox('Cláusulas especiales', YES_NO, index=YES_NO.index(str(f.get('commercial_clausulas','NO')).upper()) if str(f.get('commercial_clausulas','NO')).upper() in YES_NO else 1)
        f['commercial_restricciones'] = st.selectbox('Restricciones', YES_NO, index=YES_NO.index(str(f.get('commercial_restricciones','NO')).upper()) if str(f.get('commercial_restricciones','NO')).upper() in YES_NO else 1)
        f['project_rent'] = st.number_input('Renta del proyecto', min_value=0.0, value=float(f.get('project_rent',0) or 0))
        f['project_area'] = st.number_input('Área (m²)', min_value=0.0, value=float(f.get('project_area',0) or 0))
        f['project_rent_m2'] = f['project_rent'] / f['project_area'] if f['project_area'] else 0
        c1, c2, c3 = st.columns(3)
        with c1: f['signature'] = st.selectbox('Firma (mes)', MONTHS, index=MONTHS.index(f.get('signature','')) if f.get('signature','') in MONTHS else 0)
        with c2: f['delivery_date'] = st.selectbox('Entrega de local (mes)', MONTHS, index=MONTHS.index(f.get('delivery_date','')) if f.get('delivery_date','') in MONTHS else 0)
        with c3: f['opening_date'] = st.selectbox('Apertura (mes)', MONTHS, index=MONTHS.index(f.get('opening_date','')) if f.get('opening_date','') in MONTHS else 0)
        f['commercial_comments'] = st.text_area('Comentarios', f.get('commercial_comments',''))

st.divider()
col1, col2 = st.columns(2)
with col1:
    payload = build_payload(f, imgs, names)
    safe_name = re.sub(r'[^\\w.-]+', '_', str(f.get('project_name','presentacion_inicial')).strip()) or 'presentacion_inicial'
    st.download_button('Descargar JSON de datos', payload, file_name=f'{safe_name}.json', mime='application/json', use_container_width=True)
with col2:
    if st.button('Generar presentación HTML', type='primary', use_container_width=True):
        html = html_page(f, sheets, {k: as_bytes(v) for k, v in imgs.items()})
        st.session_state.generated_html = html
if st.session_state.get('generated_html'):
    st.success('Presentación generada correctamente con las siete secciones solicitadas.')
    st.download_button('Descargar presentación HTML', st.session_state.generated_html.encode('utf-8'), file_name='presentacion_inicial.html', mime='text/html', use_container_width=True)
