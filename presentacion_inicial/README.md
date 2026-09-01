# Presentación Inicial

Aplicación en **Streamlit** para recopilar la información de un nuevo punto comercial y generar una presentación navegable en HTML.

## Secciones principales

La aplicación está organizada en siete bloques principales:

1. **Portada**: región, nombre del proyecto, segmento, especialista, dirección y enlace de Maps.
2. **General**: ciudad, UPZ/comuna, foto de entorno y comentarios del plan rector.
3. **Entorno | Generadores Vivienda**: hasta cuatro generadores, con foto, nombre, tipo y viviendas asociadas.
4. **Entorno | Generadores Empleo**: hasta cuatro generadores, con foto, nombre, tipo y empleos asociados.
5. **Expansión | Mercado y Tráfico**: viviendas, empleos, generador principal y tráficos peatonal, vehicular y de motos.
6. **Tienda Hermana**: selección de una tienda abierta de referencia, fotografía y comentarios.
7. **Condiciones comerciales**: condiciones de negociación, renta, área, renta por m², firma, entrega y apertura.

También se conservan módulos complementarios de la referencia: solución de imagen, layout/CAPEX, Networks, viabilidad financiera, microsaturación y piloto.

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación carga `Book.xlsx` desde la raíz del proyecto. El archivo sirve como fuente de filtros, tiendas abiertas, tablas y métricas.

## Guardar y restaurar información

Desde la barra lateral se puede cargar un JSON previamente exportado. El botón **Descargar JSON de datos** guarda campos, selecciones e imágenes en un único archivo para continuar el trabajo más adelante.

## Publicar en GitHub

Crea un repositorio nuevo y sube el contenido de esta carpeta:

```bash
git init
git add .
git commit -m "Crear Presentación Inicial en Streamlit"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Para publicar la app, entra en [Streamlit Community Cloud](https://share.streamlit.io/), conecta el repositorio, selecciona `app.py` como archivo principal y despliega.

> Si `Book.xlsx` contiene información sensible, utiliza un repositorio privado y revisa los permisos antes de desplegarlo.
