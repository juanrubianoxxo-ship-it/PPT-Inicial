import importlib.util
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location('renderer', ROOT / 'html_renderer.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

book = pd.DataFrame([{
    'MUNICIPIO': 'Bogotá', 'UPZ/COMUNA': 'Centro', 'SEG26': 'BASE', 'TIE27': 'TMCB',
    'NAME': 'Tienda prueba', 'ESTADO': 'ABIERTA', 'MESOP_NUM': 1,
    'VENTAS OUM_NUM': 100, 'RENTA UM_NUM': 20, 'AREA_NUM': 10, 'COSTO M2_NUM': 5,
}])
fields = {
    'project_name': 'Punto general', 'city': 'Bogotá', 'upz': 'Centro', 'segment': 'Base',
    'specialist': 'ANDRES DUQUE RESTREPO', 'project_rent': 1200000,
    'project_area': 100, 'project_rent_m2': 12000,
    'commercial_permanencia': 'SI', 'commercial_gracia': '60', 'commercial_ipc': '+2',
    'commercial_operacion': 'SI', 'commercial_alcohol': 'NO', 'commercial_prima': 'SI',
    'commercial_anticipo': 'NO', 'commercial_clausulas': 'SI', 'commercial_restricciones': 'NO',
    'generator_type': 'Comercial',
    'generator_cards': [{'name': 'Centro comercial', 'type': 'Comercial', 'value': 50}],
    'microsaturation_enabled': 'Sí', 'book_store': 'Tienda espejo ABC',
    'traffic_video_link': 'https://example.com/traffic',
}
images = {
    'microsaturation_image_1': b'one', 'microsaturation_image_2': b'two',
    'microsaturation_image_3': b'three', 'pilot_image_1': b'pilot-one', 'pilot_image_2': b'pilot-two',
}
html = renderer.render(fields, {'JUN': book}, images)
assert html.count('<section class="slide') == 13
assert 'Slide 7' not in html
assert 'Performance combinado' not in html
assert 'Venta promedio' in html
assert 'PPT: PUNTO POTENCIAL' in html
assert 'PR: PLAN RECTOR' in html
assert 'NF: NUEVOS FORMATOS' in html
assert 'Networks' in html
assert 'Periodo de gracia (Dias)' in html
assert 'Tienda espejo ABC' in html
assert 'Entorno | Generadores Vivienda' in html
assert 'Entorno | Generadores Empleo' in html
assert 'Expansión | Mercado y Tráfico' in html
assert 'Video tráfico' in html
assert 'Piloto 2' in html
print('OK: composición general, Microsaturación adicional y Piloto validados')
