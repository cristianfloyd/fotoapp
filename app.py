"""Menú visual de FotoApp con Streamlit.

Ejecutar desde la carpeta del proyecto:
    python -m streamlit run app.py --server.address 127.0.0.1

Todas las operaciones parten de la imagen adaptada por publicar_foto, que
debe cargarse primero. Las figuras se guardan en la carpeta indicada por la
variable de entorno FOTOAPP_SALIDA (por defecto, results/app).
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use('Agg')

import cv2
import requests
import streamlit as st

from fotoapp import boceto, ecualizador, filtros, publicar_foto

REDES = {
  'YouTube': 'YOUTUBE',
  'Instagram': 'INSTAGRAM',
  'Twitter / X': 'TWITTER',
  'Facebook': 'FACEBOOK',
  'TikTok': 'TIKTOK',
  'Pinterest': 'PINTEREST',
  'LinkedIn': 'LINKEDIN',
  'Threads': 'THREADS',
  'Snapchat': 'SNAPCHAT',
}
FILTROS = ['Blur', 'Contour', 'Detail', 'Edge Enhance', 'Edge Enhance More',
           'Emboss', 'Find Edges', 'Sharpen', 'Smooth']
TECNICAS = ['Canny', 'Sobel', 'Laplaciano', 'Umbral']
ERRORES_ESPERADOS = (ValueError, OSError, requests.RequestException, cv2.error)


def carpeta_salida():
  carpeta = Path(os.environ.get('FOTOAPP_SALIDA', Path(__file__).with_name('results') / 'app'))
  carpeta.mkdir(parents=True, exist_ok=True)
  return carpeta


def ruta_salida(prefijo):
  """Genera un nombre único para no reemplazar figuras anteriores."""
  marca = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
  return str(carpeta_salida() / f'{prefijo}_{marca}.png')


def nombre_archivo(texto):
  return texto.lower().replace(' / ', '_').replace(' ', '_')


def inicializar_estado():
  st.session_state.setdefault('imagen_activa', None)
  st.session_state.setdefault('entrada_activa', None)
  st.session_state.setdefault('red_activa', None)
  st.session_state.setdefault('resultados', {})


def cargar_desde_archivo(archivo, red):
  """Guarda la subida en un temporal; su nombre solo se usa como etiqueta."""
  sufijo = Path(archivo.name).suffix.lower()
  with tempfile.NamedTemporaryFile(suffix=sufijo, delete=False) as temporal:
    temporal.write(archivo.getvalue())
    ruta = temporal.name
  try:
    return publicar_foto(ruta, red)
  finally:
    os.remove(ruta)


def cargar_imagen(origen, archivo, url, red):
  if origen == 'Archivo local':
    if archivo is None:
      raise ValueError('Seleccione un archivo de imagen')
    imagen = cargar_desde_archivo(archivo, REDES[red])
    etiqueta = archivo.name
  else:
    imagen = publicar_foto(url, REDES[red])
    etiqueta = url.strip()

  st.session_state['imagen_activa'] = imagen
  st.session_state['entrada_activa'] = f'{etiqueta} · {red}'
  st.session_state['red_activa'] = red
  st.session_state['resultados'] = {}


def ejecutar(operacion, clave, accion):
  """Ejecuta una operación y registra la figura guardada o informa el error."""
  try:
    ruta = accion()
  except ERRORES_ESPERADOS as error:
    st.error(f'No se pudo {operacion}: {error}')
  else:
    st.session_state['resultados'][clave] = str(ruta)


def mostrar_resultado(clave):
  ruta = st.session_state['resultados'].get(clave)
  if ruta:
    st.image(ruta, width='stretch')
    st.caption(f'Guardado en {ruta}')


def panel_carga():
  st.sidebar.header('1. Cargar imagen')
  origen = st.sidebar.radio('Origen', ['Archivo local', 'URL'], key='origen')
  archivo, url = None, ''
  if origen == 'Archivo local':
    archivo = st.sidebar.file_uploader('Imagen', type=['jpg', 'jpeg', 'png'], key='archivo')
  else:
    url = st.sidebar.text_input('URL directa de la imagen', key='url')
  red = st.sidebar.selectbox('Red social', list(REDES), key='red')

  if st.sidebar.button('Cargar y adaptar', key='cargar', type='primary'):
    try:
      cargar_imagen(origen, archivo, url, red)
    except ERRORES_ESPERADOS as error:
      st.sidebar.error(f'No se pudo cargar la imagen: {error}')
    else:
      st.sidebar.success('Imagen cargada y adaptada')

  if st.session_state['entrada_activa']:
    st.sidebar.info(f"Imagen activa: {st.session_state['entrada_activa']}")


def pestana_adaptacion(imagen, sin_imagen):
  if imagen is not None:
    st.image(imagen, caption=f'{imagen.width} × {imagen.height} píxeles', width='stretch')
  if st.button('Guardar adaptación', key='guardar_adaptacion', disabled=sin_imagen):
    def guardar():
      ruta = ruta_salida(f"adaptada_{nombre_archivo(st.session_state['red_activa'])}")
      imagen.save(ruta)
      return ruta
    ejecutar('guardar la adaptación', 'adaptacion', guardar)
  ruta = st.session_state['resultados'].get('adaptacion')
  if ruta:
    st.caption(f'Guardado en {ruta}')


def pestana_contraste(imagen, sin_imagen):
  st.write('Ecualiza la luminosidad usando el histograma de la foto.')
  if st.button('Ecualizar', key='ecualizar', disabled=sin_imagen):
    def ecualizar():
      ruta = ruta_salida('ecualizada')
      ecualizador(imagen, archivo_salida=ruta)
      return ruta
    ejecutar('ecualizar la imagen', 'contraste', ecualizar)
  mostrar_resultado('contraste')


def pestana_filtros(imagen, sin_imagen):
  filtro = st.selectbox('Filtro', FILTROS, key='filtro')
  if st.button('Aplicar filtro', key='aplicar_filtro', disabled=sin_imagen):
    def aplicar():
      ruta = ruta_salida(f'filtro_{nombre_archivo(filtro)}')
      filtros(imagen, filtro, archivo_salida=ruta)
      return ruta
    ejecutar('aplicar el filtro', 'filtro', aplicar)
  mostrar_resultado('filtro')


def pestana_boceto(imagen, sin_imagen):
  tecnica = st.selectbox('Técnica', TECNICAS, key='tecnica')
  umbral, umbral1, umbral2, kernel = 127, 50, 150, 3
  if tecnica == 'Canny':
    umbral1 = st.slider('Umbral inferior', 0, 255, 50, key='umbral1')
    umbral2 = st.slider('Umbral superior', 0, 255, 150, key='umbral2')
    kernel = st.selectbox('Tamaño del núcleo', [3, 5, 7], key='kernel_canny')
  else:
    umbral = st.slider('Umbral', 0, 255, 127, key='umbral')
    if tecnica != 'Umbral':
      kernel = st.selectbox('Tamaño del núcleo', [1, 3, 5, 7, 9], index=1, key='kernel')
  invertir = st.checkbox('Invertir blanco y negro', key='invertir')

  if st.button('Generar boceto', key='generar_boceto', disabled=sin_imagen):
    def generar():
      ruta = ruta_salida(f'boceto_{nombre_archivo(tecnica)}')
      boceto(imagen, tecnica, invertir, umbral, kernel, umbral1, umbral2, archivo_salida=ruta)
      return ruta
    ejecutar('generar el boceto', 'boceto', generar)
  mostrar_resultado('boceto')


def main():
  st.set_page_config(page_title='FotoApp', layout='wide')
  inicializar_estado()
  st.title('FotoApp')
  panel_carga()

  imagen = st.session_state['imagen_activa']
  sin_imagen = imagen is None
  if sin_imagen:
    st.info('Primero cargue y adapte una imagen desde el panel lateral.')

  adaptacion, contraste, filtro, bocetos = st.tabs(
    ['Adaptación', 'Contraste', 'Filtros', 'Boceto'])
  with adaptacion:
    pestana_adaptacion(imagen, sin_imagen)
  with contraste:
    pestana_contraste(imagen, sin_imagen)
  with filtro:
    pestana_filtros(imagen, sin_imagen)
  with bocetos:
    pestana_boceto(imagen, sin_imagen)


main()
