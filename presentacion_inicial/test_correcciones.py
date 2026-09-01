import ast
import base64
import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent

spec = importlib.util.spec_from_file_location('html_renderer', ROOT / 'html_renderer.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

colors = dict(renderer.CONVENTION_COLORS)
assert colors['PR: PLAN RECTOR'] == '#D8B4FE'
assert colors['NF: NUEVOS FORMATOS'] == '#FACC15'
assert colors['PPT: PUNTO POTENCIAL'] == '#7E3E96'
assert colors['CERRADA'] == '#808080'
assert colors['FIRMADA'] == '#000000'
legend = renderer.convention_legend()
for color in ('#D8B4FE', '#FACC15', '#7E3E96', '#808080', '#000000'):
    assert f'background:{color}' in legend

sample = b'fake-image-bytes'
encoded = base64.b64encode(sample).decode('ascii')
assert base64.b64decode(encoded.encode('ascii'), validate=True) == sample

app_tree = ast.parse((ROOT / 'app.py').read_text(encoding='utf-8'))
needed = {'as_bytes', 'json_safe', 'encode_image', 'decode_image', 'build_json_payload', 'restore_images', 'populate_form_widget_state', '_nonnegative_float'}
constants = {'SPECIALISTS', 'GENERATOR_TYPES', 'YES_NO', 'IPC_OPTIONS', 'FORM_WIDGET_DEFAULTS', 'COMMERCIAL_WIDGET_DEFAULTS', 'NUMERIC_WIDGET_DEFAULTS'}
app_nodes = [node for node in app_tree.body if isinstance(node, (ast.Import, ast.ImportFrom)) or (isinstance(node, ast.FunctionDef) and node.name in needed) or (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in constants for target in node.targets))]
app_namespace = {'__name__': 'app_test'}
exec(compile(ast.Module(body=app_nodes, type_ignores=[]), str(ROOT / 'app.py'), 'exec'), app_namespace)
payload = json.loads(app_namespace['build_json_payload']({'project_name': 'Punto 01', 'city': 'Bogotá'}, {'cover': sample}, {'cover': 'foto.png'}))
assert payload['fields']['project_name'] == 'Punto 01'
assert payload['fields']['city'] == 'Bogotá'
assert 'JUN' not in payload and 'rows' not in payload and 'book_data' not in payload
assert app_namespace['decode_image'](payload['images']['cover']) == sample
restored_images, restored_names = app_namespace['restore_images']({
    'layout_image': payload['images']['cover'],
    'legacy_image': encoded,
})
assert restored_images['layout_image'] == sample
assert restored_names['layout_image'] == 'foto.png'
assert restored_images['legacy_image'] == sample

class FakeStreamlit:
    def __init__(self):
        self.session_state = {}

app_namespace['st'] = FakeStreamlit()
app_namespace['populate_form_widget_state']({
    'project_name': 'Punto restaurado',
    'city': 'Bogotá',
    'commercial_vigencia': '20',
    'project_rent': 123456,
    'generator_cards': [{'type': 'Educativo', 'value': 42}],
})
restored = app_namespace['st'].session_state
assert restored['s1_project'] == 'Punto restaurado'
assert restored['book_city'] == 'Bogotá'
assert restored['s10_commercial_vigencia'] == '20'
assert restored['s10_project_rent'] == 123456.0
assert restored['s5_type1'] == 'Educativo' and restored['s5_val1'] == 42.0

book = pd.DataFrame([{
    'MUNICIPIO': 'Bogotá', 'UPZ/COMUNA': 'Centro', 'SEG26': 'BASE',
    'TIE27': 'TMCB', 'NAME': 'Tienda prueba', 'MESOP_NUM': 1,
    'VENTAS OUM_NUM': 100, 'RENTA UM_NUM': 20, 'COSTO M2_NUM': 5,
    'AREA_NUM': 10, 'ESTADO': 'ABIERTA',
}])
html = renderer.render({'city': '', 'upz': '', 'segment': 'BASE', 'microsaturation_enabled': 'No', 'generator_cards': [{'name': 'Universidad Central', 'type': 'Empleo', 'value': 42}]}, {'JUN': book}, {})
assert html.startswith('<!doctype html>')
assert '#D8B4FE' in html and '#FACC15' in html and '#808080' in html and '#000000' in html
assert 'Tienda Hermana' in html
assert 'Universidad Central' in html
assert 'single-asset-layout' in html
assert 'Book.xlsx' not in html
print('OK: sintaxis, convenciones, HTML y Base64')
