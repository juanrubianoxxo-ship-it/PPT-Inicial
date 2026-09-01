# OXXO · Generador de presentación con impacto

La aplicación usa HTML y CSS como formato maestro. Cada slide tiene tamaño fijo 16:9, márgenes controlados por CSS, tipografía Aptos/Arial, tablas con anchos definidos y exportación a HTML navegable.

## Flujo de datos

El archivo `Book.xlsx` incluido en el proyecto se carga automáticamente y alimenta los filtros de ciudad, UPZ/comuna, tiendas abiertas, tablas y métricas. El espacio de carga de la barra lateral está reservado para el archivo JSON de una presentación previamente guardada.

El botón **Descargar JSON de datos** guarda en un único archivo los campos, selecciones, valores numéricos, estado de microsaturación y las imágenes cargadas codificadas en Base64. El botón **Cargar información del JSON** restaura esa información en la app y vuelve a completar los campos registrados, incluidas las imágenes. Las imágenes recuperadas se muestran como vista previa dentro de cada casilla y también se conservan para la generación HTML. El `Book.xlsx` continúa siendo únicamente la base de información de referencia para filtros, tiendas, tablas y métricas, y no se duplica dentro del JSON.

## Correcciones incluidas

El Slide 1 solicita dirección y link de Maps, y el Especialista se selecciona desde un desplegable estandarizado en mayúsculas y con el nombre antes de los apellidos. Los contenidos de los antiguos Slides 2 y 3 se combinaron en **Slide 2 - General**, que conserva la foto de entorno, los selectores de ciudad/municipio y UPZ/comuna desde Book, la opción de ciudad nueva y la métrica **Venta promedio**. El antiguo Slide 3 ya no se genera.

El Slide 4 usa las etiquetas **Foto inicial local** y **Foto solución de imagen**; ya no solicita link de ubicación ni Street View y conserva únicamente el link de video de tráfico. El Slide 5 permite registrar hasta cuatro generadores, con nombre editable y tipo principal o individual entre Administrativo, Residencial, Comercial, Industrial, Educativo, Salud y Transporte masivo. El Slide 6 utiliza una sola casilla para la foto de layout / CAPEX. El Slide 7 fue retirado. El Slide 8 se titula **Tienda Hermana**, elimina la foto de tienda operando y destaca el nombre de la tienda espejo. El Slide 9 se titula **Networks**. El Slide 10 contiene condiciones comerciales con selectores SI/NO, IPC desplegable, área, renta del proyecto y cálculo automático de Renta/m², además de Firma, Entrega de local y Apertura.

El Slide 11 ahora es una diapositiva regular de **Viabilidad financiera**, con título, numeración, marco de presentación y la foto dentro del layout. Ya no se muestra como una imagen aislada a página completa. Si no se carga una imagen, se conserva un marcador estable dentro de la slide.

Las convenciones de tienda se muestran únicamente como **muestras de color** y sus etiquetas: no se insertan logos ni imágenes de la carpeta `CONVENCIONES/` en la presentación. Los colores son: **PR morado claro**, **NF amarillo**, **CERRADA gris** y **FIRMADA negro**; TMCB, EXP, OBRA y PPT conservan sus colores existentes.

La opción **¿Hay microsaturación?** permite cargar hasta cinco fotos y las acomoda automáticamente según la cantidad. Microsaturación se genera como una slide adicional sin número visible. La sección **Slide 12 · Piloto** permite cargar dos fotos y se genera con numeración 12. La Viabilidad financiera continúa como Slide 11.

## Ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```

En la app, carga un JSON si quieres restaurar una presentación anterior, ajusta los datos y pulsa **Generar presentación**. Después podrás descargar el HTML navegable. El PDF fue retirado del flujo.
