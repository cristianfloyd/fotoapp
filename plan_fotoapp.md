# Plan de trabajo de FotoApp

Desarrollaré una aplicación local para adaptar y procesar fotografías como primera parte del Proyecto 2 de Programación Python Avanzada. Organizaré el trabajo en un módulo de funciones, una interfaz en el navegador y un notebook de pruebas que ejecutaré desde VS Code.

En este documento planifico exclusivamente FotoApp. Abordaré la parte de regresión en un trabajo separado.

## 1. Objetivo y alcance

Mi objetivo es cargar una fotografía, adaptarla a un formato de red social y aplicar operaciones de contraste, filtrado y detección de bordes. Conservaré los originales y documentaré los resultados para poder explicar las decisiones y limitaciones de cada técnica.

Organizaré la solución en tres archivos principales:

| Archivo | Cómo lo utilizaré |
|---|---|
| `fotoapp.py` | Reuniré las funciones de carga, adaptación, procesamiento, validación, comparación y guardado. |
| `app.py` | Construiré el menú visual con Streamlit e importaré las funciones del módulo. |
| `fotoapp_testdev.ipynb` | Probaré las funciones, mostraré las comparaciones y redactaré mis observaciones. |

Ejecutaré la aplicación únicamente en mi computadora. No incorporaré cuentas, base de datos, publicación automática en redes sociales, procesamiento por lotes ni alojamiento en Internet.

Admitiré rutas locales y URL públicas directas a imágenes. En la interfaz también permitiré seleccionar un archivo desde la computadora. No integraré autenticación ni acceso a Drive.

## 2. Carga y adaptación de imágenes

### Formatos de salida

Utilizaré una configuración por red social:

| Red | Uso | Dimensiones | Relación de aspecto |
|---|---|---|---|
| YouTube | Miniatura de video horizontal | 3840 × 2160 píxeles | 16:9 |
| Instagram | Publicación cuadrada del feed | 1080 × 1080 píxeles | 1:1 |
| Facebook | Publicación cuadrada del feed | 1080 × 1080 píxeles | 1:1 |
| Twitter/X | Fotografía horizontal del feed | 1200 × 675 píxeles | 16:9 |

Para YouTube tomaré como referencia la ayuda oficial sobre miniaturas. Para Instagram y Facebook utilizaré el formato cuadrado que también recoge la guía de Hootsuite. En Twitter/X conservaré 1200 × 675 como elección del proyecto: comparte la proporción 16:9 de esa guía, aunque la medida que allí se recomienda es 1280 × 720.

Distinguiré las recomendaciones de las fuentes de mis decisiones de diseño. No presentaré estas medidas como requisitos únicos de las plataformas ni como especificaciones de anuncios, historias, portadas o tarjetas de enlaces.

### Conservación del encuadre

Redimensionaré cada foto manteniendo su proporción, la centraré y completaré el espacio sobrante con márgenes blancos. No recortaré ni estiraré el contenido.

Registraré las dimensiones originales, el tamaño de la fotografía redimensionada y el rectángulo que ocupa dentro del lienzo. Utilizaré ese rectángulo para separar la foto de los márgenes durante las operaciones posteriores; no intentaré reconocerlos por su color.

Si necesito ampliar una imagen pequeña, aclararé que el aumento de dimensiones no recupera detalle. Conservaré siempre el archivo original sin sobrescribirlo.

### Lectura y validación

Implementaré la función del punto 1 con dos cadenas de entrada: la ruta o URL de la imagen y el nombre de la red social. Admitiré las palabras de la consigna —`Youtube`, `Instagram`, `Twitter` y `Facebook`— sin distinguir mayúsculas y minúsculas y eliminando espacios al principio y al final.

Compartiré la lógica de lectura y validación entre archivos locales, descargas y archivos seleccionados en la interfaz. Antes de redimensionar, aplicaré la orientación indicada en los datos EXIF y normalizaré la imagen a RGB. Trabajaré inicialmente con JPEG y PNG estáticos; compondré las transparencias sobre blanco y rechazaré entradas animadas o de varias páginas.

La carga devolverá la imagen original, la adaptación y los datos necesarios para identificar su origen, la red seleccionada y el área de contenido. Validaré esta información también desde el módulo, sin depender exclusivamente de los controles de la interfaz.

## 3. Ajuste de contraste mediante el histograma

Aplicaré ecualización a la componente de luminosidad. Para ello, extraeré el área de la fotografía, la convertiré a YCbCr, ecualizaré el canal Y y conservaré Cb y Cr antes de volver a RGB. Finalmente, repondré los márgenes blancos sin modificarlos.

Con este tratamiento buscaré mejorar el contraste sin introducir deliberadamente cambios cromáticos. Tendré en cuenta que las conversiones y los límites de representación pueden producir pequeñas variaciones de color.

Probaré la función con dos fotografías diferentes: una oscura y otra con exceso de luz. Para cada una guardaré una figura que muestre:

- La imagen adaptada antes de ecualizar y su histograma de luminosidad.
- La imagen ecualizada y su histograma de luminosidad.

Calcularé los histogramas únicamente sobre el contenido de la foto, sin incluir los márgenes. Analizaré si mejora la visibilidad de los detalles, si se acentúa el ruido y si el resultado mantiene una apariencia adecuada.

No interpretaré la ecualización como una recuperación de información perdida: una zona completamente saturada o sin detalle no se reconstruye redistribuyendo intensidades.

### Comparación creativa por canales RGB

Incluiré en el notebook un experimento adicional con ecualización independiente de los canales rojo, verde y azul. Compararé la entrada, la ecualización de luminosidad y la ecualización RGB.

Desde mi experiencia como fotógrafo, distinguiré la corrección de contraste de la búsqueda de un clima visual. Evaluaré las dominantes y los cambios de saturación como posibles recursos creativos, sin asumir que el resultado será consistente entre fotos distintas. Mantendré este experimento fuera del menú principal.

## 4. Aplicación de los nueve filtros

Implementaré una función que reciba la imagen y el nombre del filtro. En el menú presentaré las opciones numeradas y convertiré la elección al nombre correspondiente.

| Número | Filtro |
|---|---|
| 1 | Blur |
| 2 | Contour |
| 3 | Detail |
| 4 | Edge Enhance |
| 5 | Edge Enhance More |
| 6 | Emboss |
| 7 | Find Edges |
| 8 | Sharpen |
| 9 | Smooth |

Aplicaré los nueve filtros sobre una misma fotografía, distinta de las usadas para contraste. Elegiré una imagen con texturas, bordes definidos y zonas uniformes.

Cada filtro partirá de la misma entrada, sin acumular efectos. Procesaré solamente el área de la fotografía y mantendré los márgenes intactos para evitar contornos artificiales en su unión con la imagen.

Guardaré nueve figuras comparativas, cada una con la entrada a la izquierda y el resultado a la derecha. Colocaré el nombre del filtro como título del segundo panel. Compararé sus efectos sobre los detalles, las texturas y los bordes, y explicaré sus posibles usos visuales.

## 5. Bocetos con Sobel y Canny

Trabajaré con el retrato de una persona y compararé dos técnicas: Sobel y Canny. Utilizaré el mismo retrato y la misma escala de procesamiento para que la comparación sea consistente.

Extraeré el contenido de la fotografía, lo convertiré a escala de grises y aplicaré un suavizado gaussiano para reducir ruido y detalles pequeños.

- Con **Sobel**, calcularé los gradientes horizontal y vertical, combinaré sus magnitudes y aplicaré un umbral para obtener las líneas.
- Con **Canny**, ajustaré los umbrales inferior y superior, manteniendo el inferior por debajo del superior.

En ambos casos representaré los contornos con líneas negras sobre fondo blanco y recompondré el resultado en el tamaño de destino, también con márgenes blancos.

Probaré dos configuraciones por técnica y registraré sus parámetros en el notebook. Después guardaré una comparación final con el retrato de entrada, el boceto Sobel y el boceto Canny.

Analizaré los rasgos faciales conservados, los contornos fragmentados o eliminados y la presencia de ruido. Elegiré los valores predeterminados de la aplicación a partir de esas observaciones, sin afirmar que una técnica es mejor para cualquier imagen.

## 6. Menú local y manejo de la imagen activa

Construiré el menú en Streamlit. Iniciaré el servidor desde la carpeta del proyecto con:

```bash
python -m streamlit run app.py --server.address 127.0.0.1
```

Mantendré el servidor limitado a la computadora local. No necesitaré un menú de consola independiente ni iniciaré acciones al importar `fotoapp.py`.

Organizaré el recorrido de la siguiente manera:

```text
Inicio
  ↓
Selecciono un archivo local o ingreso una URL
  ↓
Selecciono la red y pulso «Cargar y adaptar»
  ├─ Si falla, muestro el error y conservo la imagen activa anterior
  └─ Si funciona, establezco la nueva imagen activa
       ├─ Visualizo o guardo la adaptación
       ├─ Ajusto el contraste, comparo y guardo
       ├─ Aplico un filtro, comparo y guardo
       └─ Genero un boceto, comparo y guardo
```

Deshabilitaré las operaciones hasta completar la primera carga. Cada operación partirá de la imagen adaptada y no del resultado de una operación anterior.

Mantendré la imagen activa durante las reejecuciones de Streamlit. Cambiar un archivo, una URL o la red seleccionada no la reemplazará hasta que vuelva a pulsar «Cargar y adaptar». Identificaré claramente qué entrada está activa.

En las funciones validaré las entradas y generaré excepciones comprensibles. En la interfaz capturaré los errores esperados para informar el problema y permitir continuar. Contemplaré archivos inexistentes, contenido inválido, redes o filtros no admitidos, fallos de descarga y errores de guardado.

Para las URL estableceré tiempos de espera y un límite de descarga, y admitiré únicamente HTTP y HTTPS. Trataré el nombre de un archivo seleccionado como una etiqueta, no como una ruta de salida.

Separaré el procesamiento de la presentación. Las funciones de procesamiento devolverán imágenes; las de presentación construirán las comparaciones. Reuniré ambas tareas en funciones de uso que permitan mostrar y guardar las figuras exigidas desde el notebook y desde la aplicación, sin duplicar los algoritmos.

## 7. Fotografías y licencias

Utilizaré fotografías públicas con licencia de reutilización. Conservaré los originales y registraré los créditos y las modificaciones en `images/SOURCES.md`.

Tomaré las siguientes imágenes como selección inicial y comprobaré su adecuación visual antes de utilizarlas en las pruebas:

| Uso | Fotografía y crédito | Fuente |
|---|---|---|
| Redimensionado | Panorama de Fronalpstock; Hannes Röst | [Fronalpstock big.jpg](https://commons.wikimedia.org/wiki/File:Fronalpstock_big.jpg) |
| Evaluación para contraste | Torre Eiffel; Benh LIEU SONG | [Tour Eiffel Wikimedia Commons.jpg](https://commons.wikimedia.org/wiki/File:Tour_Eiffel_Wikimedia_Commons.jpg) |
| Evaluación para contraste | Girasol; Pudelek, edición de Yzmo | [Sunflower from Silesia2.jpg](https://commons.wikimedia.org/wiki/File:Sunflower_from_Silesia2.jpg) |
| Nueve filtros | Cascadas Hopetoun; DAVID ILIFF | [Hopetoun falls.jpg](https://commons.wikimedia.org/wiki/File:Hopetoun_falls.jpg) |
| Sobel y Canny | Retrato de Linus Torvalds; autor desconocido, fuente Linuxmag.com, diciembre de 2002 | [Linus Torvalds.jpeg](https://commons.wikimedia.org/wiki/File:Linus_Torvalds.jpeg) |

Estas páginas ofrecen la licencia [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Al distribuir las imágenes y sus adaptaciones, conservaré los créditos, el enlace a la licencia y las condiciones de compartir bajo la misma licencia o una compatible. No atribuiré la fotografía de Linus Torvalds al usuario que la subió: mantendré la indicación de autor desconocido de la fuente.

Revisaré especialmente las fotografías destinadas a contraste. Sus licencias permiten reutilizarlas, pero no demuestran que sean ejemplos de subexposición o sobreexposición. Si no presentan las características necesarias, las sustituiré por otras fotografías licenciadas que sí las tengan; no presentaré una simulación digital como una exposición real.

El retrato de Linus Torvalds tiene 600 × 819 píxeles. Comprobaré si su resolución y su fondo permiten distinguir los contornos faciales de manera adecuada, teniendo presente que ampliarlo no añade detalle.

Guardaré copias locales para repetir las pruebas sin depender de Internet y mantendré una demostración específica de carga por URL.

## 8. Entorno de desarrollo

Trabajaré con Python 3.14 y crearé un entorno virtual propio dentro de `proyecto_2/.venv`, sin modificar el entorno ni las dependencias de los otros trabajos de la materia. Utilizaré el mismo intérprete en VS Code, en el kernel del notebook y al iniciar Streamlit.

| Herramienta | Uso que le daré |
|---|---|
| Pillow | Leeré imágenes, adaptaré dimensiones, aplicaré ecualización y utilizaré los nueve filtros. |
| NumPy | Representaré y operaré con matrices de píxeles. |
| `opencv-python-headless` | Aplicaré Sobel, Canny y el suavizado previo. |
| Matplotlib | Construiré y guardaré comparaciones e histogramas. |
| Streamlit | Implementaré la interfaz local en el navegador. |
| ipykernel | Ejecutaré el notebook desde VS Code. |

Utilizaré la biblioteca estándar de Python para las descargas. Instalaré una sola variante de OpenCV y no necesitaré sus ventanas gráficas, porque mostraré los resultados en el navegador y en el notebook.

Comprobaré la compatibilidad de las dependencias en el entorno del proyecto y registraré las versiones que funcionen en `requirements.txt`. Verificaré las importaciones, la ejecución de una celda y el inicio y cierre del servidor local antes de comenzar el procesamiento.

## 9. Organización de archivos y resultados

Organizaré los entregables con esta estructura:

```text
proyecto_2/
├── PLAN_FOTOAPP.md
├── Proyecto 2 (2).pdf
├── fotoapp.py
├── app.py
├── fotoapp_testdev.ipynb
├── requirements.txt
├── README.md
├── .gitignore
├── images/
│   ├── SOURCES.md
│   └── originals/
└── results/
```

Guardaré las imágenes procesadas y las figuras comparativas en PNG. Generaré nombres que identifiquen la operación y añadan un sufijo único para evitar sobrescribir resultados anteriores.

No incorporaré compresión automática para alcanzar un peso máximo de subida a las redes. Distinguiré las dimensiones en píxeles del peso del archivo.

En el README explicaré la preparación del entorno, la ejecución del notebook y el inicio de la aplicación. Incluiré el diagrama de flujo del menú y las referencias utilizadas. Excluiré del repositorio el entorno virtual y las cachés.

## 10. Etapas de implementación y comprobación

| Etapa | Qué haré | Cómo comprobaré que está terminada |
|---|---|---|
| 1. Entorno | Prepararé el entorno aislado y seleccionaré el kernel. | Ejecutaré las importaciones, una celda de prueba y el inicio y cierre de Streamlit; registraré las versiones utilizadas. |
| 2. Fotografías | Descargaré y revisaré los originales y sus licencias. | Comprobaré encuadre, exposición, texturas y retrato; conservaré los créditos de cada imagen. |
| 3. Carga y adaptación | Implementaré la lectura y los cuatro formatos de salida. | Probaré imágenes horizontales, verticales y cuadradas, las dimensiones exactas, los márgenes y los errores de carga. |
| 4. Contraste | Implementaré la ecualización de luminosidad y el experimento RGB. | Guardaré las comparaciones de foto oscura y sobreexpuesta, revisaré sus histogramas y explicaré el efecto cromático del experimento. |
| 5. Filtros | Implementaré la selección por nombre y las comparaciones. | Aplicaré los nueve filtros sobre una misma foto y guardaré las nueve figuras con sus títulos. |
| 6. Bocetos | Implementaré Sobel y Canny y compararé sus parámetros. | Documentaré dos configuraciones por técnica y guardaré la comparación final del retrato. |
| 7. Menú local | Integraré las funciones y el estado de la imagen en Streamlit. | Intentaré procesar sin carga previa, probaré una recarga fallida y verificaré que no se acumulen efectos ni se sobrescriban archivos. |
| 8. Reproducibilidad y defensa | Completaré las explicaciones, el README y los archivos de entrega. | Reiniciaré el kernel, ejecutaré todo el notebook y recorreré la aplicación siguiendo las instrucciones del README. |

Seguiré este orden de forma secuencial. Probaré el módulo desde el notebook antes de integrar la interfaz web.

Para los comportamientos deterministas escribiré primero una prueba que falle y después implementaré lo necesario para que funcione. Comprobaré dimensiones, validaciones, conservación de los originales y mantenimiento de los márgenes mediante aserciones. Evaluaré visualmente los resultados estéticos, porque una imagen con dimensiones correctas no garantiza un buen procesamiento.

## 11. Preparación de la entrega y la defensa

Publicaré en GitHub el módulo, la interfaz, el notebook, las imágenes de prueba y los resultados, junto con las instrucciones y los créditos. Prepararé el archivo de entrega con el enlace al repositorio para Moodle.

Antes de entregar, comprobaré que cada punto de la primera parte tenga su demostración y que las figuras estén guardadas. Revisaré que el diagrama represente el menú real y que las instrucciones permitan reproducir el trabajo.

Para la defensa prepararé la explicación de las siguientes decisiones:

- Por qué conservo el encuadre mediante márgenes y qué diferencia hay entre conservar el contenido y conservar el detalle.
- Cómo utilizo el histograma y por qué separo la ecualización de luminosidad del experimento RGB.
- Qué cambia con cada filtro y qué observé sobre texturas y bordes.
- Cómo funcionan Sobel y Canny y por qué elegí sus parámetros.
- Cómo impido procesar sin cargar primero una imagen y cómo manejo los errores.

Como realizaré y presentaré el trabajo individualmente, confirmaré con la cátedra la modalidad de entrega indicada en la consigna para grupos de dos o tres integrantes.

## 12. Referencias

Consultaré y citaré estas fuentes para justificar las decisiones técnicas y las condiciones de reutilización:

1. [Ayuda oficial de YouTube: miniaturas personalizadas](https://support.google.com/youtube/answer/72431?hl=es).
2. [Hootsuite: tamaños de imágenes para redes sociales, noviembre de 2026](https://blog.hootsuite.com/social-media-image-sizes-guide/). Utilizaré las secciones de publicaciones del feed, sin confundirlas con anuncios.
3. [OpenCV: instalación y variantes del paquete](https://github.com/opencv/opencv-python#installation-and-usage).
4. [Streamlit: instalación](https://docs.streamlit.io/get-started/installation/command-line) y [ejecución de la aplicación](https://docs.streamlit.io/develop/concepts/architecture/run-your-app).
5. [Pillow: ImageOps](https://pillow.readthedocs.io/en/stable/reference/ImageOps.html) e [ImageFilter](https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html).
6. [Licencia Creative Commons Atribución-CompartirIgual 3.0](https://creativecommons.org/licenses/by-sa/3.0/), junto con las páginas de cada fotografía enlazadas en la sección 7.
