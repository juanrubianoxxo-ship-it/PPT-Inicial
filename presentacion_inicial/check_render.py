import pandas as pd
from html_renderer import render, render_expansion

book = pd.DataFrame([{
    'MUNICIPIO': 'Bogotá', 'UPZ/COMUNA': 'Centro', 'SEG26': 'BASE',
    'TIE27': 'TMCB', 'NAME': 'Tienda prueba', 'ESTADO': 'ABIERTA',
}])
fields = {
    'project_name': 'Punto', 'city': 'Bogotá', 'upz': 'Centro', 'segment': 'Base',
    'maps_link': 'https://maps.example', 'location_link': 'https://maps.example',
    'traffic_video_link': 'https://video.example', 'streetview_link': 'https://street.example',
    'housing_300': 100, 'jobs_300': 50,
    'pedestrian_15': '20', 'vehicle_15': '30', 'motorcycle_15': '10',
    'generator_housing_cards': [{'name': 'Conjunto A', 'type': 'Residencial', 'value': 80}],
    'generator_employment_cards': [{'name': 'Oficinas B', 'type': 'Administrativo', 'value': 40}],
}
html = render(fields, {'JUN': book}, {})
expansion = render_expansion(fields, {})
assert 'Ubicación' in html and 'Video tráfico' in html and 'Street View' in html
assert 'Entorno | Generadores Vivienda' in html and 'Entorno | Generadores Empleo' in html
assert '80' in html and '40' in html
assert '66,7%' in expansion and '33,3%' in expansion and 'Mercado total' in expansion
print('OK: render adicional y enlaces validados')

