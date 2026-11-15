# -*- coding: utf-8 -*-
"""FotoApp: herramientas para editar y compartir fotos en redes sociales.

Proyecto 2 de Programación Python Avanzada.
Autores: Cristian Arenas y Álvaro Baiza.

Uso como programa (menú por consola):
    python fotoapp.py

Uso como módulo:
    import fotoapp
    imagen = fotoapp.publicar_foto('foto.jpg', 'Instagram')
    fotoapp.ecualizador(imagen)

Todos los resultados (fotos adaptadas y figuras comparativas) se guardan en la
carpeta fotos_mejoradas, ubicada junto a este archivo.
"""

from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import cv2
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image, ImageFilter, ImageOps

CARPETA_RESULTADOS = Path(__file__).resolve().parent / 'fotos_mejoradas'

# Tamaño (ancho, alto) en píxeles de cada red, en el orden del menú.
REDES = {
  'YouTube': (3840, 2160),
  'Instagram': (1080, 1080),
  'Twitter': (1200, 675),
  'Facebook': (1080, 1080),
  'TikTok': (1080, 1920),
  'Pinterest': (1000, 1500),
  'LinkedIn': (1200, 627),
  'Threads': (1080, 1080),
  'Snapchat': (1080, 1920),
}

FILTROS = [
  ('Blur', ImageFilter.BLUR),
  ('Contour', ImageFilter.CONTOUR),
  ('Detail', ImageFilter.DETAIL),
  ('Edge Enhance', ImageFilter.EDGE_ENHANCE),
  ('Edge Enhance More', ImageFilter.EDGE_ENHANCE_MORE),
  ('Emboss', ImageFilter.EMBOSS),
  ('Find Edges', ImageFilter.FIND_EDGES),
  ('Sharpen', ImageFilter.SHARPEN),
  ('Smooth', ImageFilter.SMOOTH),
]

TECNICAS = {'1': 'Canny', '2': 'Sobel', '3': 'Laplaciano', '4': 'Umbral'}


def _ruta_salida(archivo_salida, nombre_predeterminado):
  """Devuelve la ruta indicada o, si no hay una, la ruta dentro de la carpeta de resultados."""
  if archivo_salida is not None:
    return archivo_salida
  CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
  return CARPETA_RESULTADOS / nombre_predeterminado


def _nombre_red(red):
  """Convierte el nombre o número de una red en su clave de REDES."""
  if not isinstance(red, str):
    raise ValueError('Ingrese el nombre o número de una red social')
  red = red.strip().upper()
  if red == 'X':
    return 'Twitter'
  if red.isdigit() and 1 <= int(red) <= len(REDES):
    return list(REDES)[int(red) - 1]
  for nombre in REDES:
    if nombre.upper() == red:
      return nombre
  raise ValueError(f'No se puede subir la imagen a {red}')


def publicar_foto(ruta, red, archivo_salida=None):
  """Abre una foto, la adapta al tamaño de una red social y la guarda.

  ruta: archivo local (incluido Drive montado en Colab) o URL directa de una imagen.
  Se aceptan rutas entre comillas, como las que pega el sistema al copiar la ruta
  de un archivo o al arrastrarlo a la terminal.
  red: nombre o número del menú (YouTube, Instagram, Twitter o X, Facebook, TikTok,
  Pinterest, LinkedIn, Threads o Snapchat), sin distinguir mayúsculas.

  Devuelve la foto en RGB escalada con una sola proporción, sin deformarla ni
  recortarla y sin agregar márgenes: ocupa el tamaño de la red en un sentido y
  queda igual o más chica en el otro. Ampliar una foto pequeña no recupera detalle.

  La adaptación se guarda como <foto>_<red>.png en fotos_mejoradas, o en
  archivo_salida si se indica. En info registra nombre, tamano_original y
  tamano_red.
  """
  if not isinstance(ruta, str) or not ruta.strip():
    raise ValueError('Ingrese una ruta o URL de imagen válida')
  ruta = ruta.strip().strip('"\'').strip()
  red = _nombre_red(red)
  ancho, alto = REDES[red]

  if ruta.lower().startswith(('https://', 'http://')):
    respuesta = requests.get(ruta, timeout=15)
    respuesta.raise_for_status()
    origen = BytesIO(respuesta.content)
    nombre_foto = Path(urlparse(ruta).path).stem or 'imagen'
  else:
    origen = ruta
    nombre_foto = Path(ruta).stem

  with Image.open(origen) as imagen_original:
    imagen = ImageOps.exif_transpose(imagen_original).convert('RGB')

  escala = min(ancho / imagen.width, alto / imagen.height)
  nuevo_ancho = max(1, round(imagen.width * escala))
  nuevo_alto = max(1, round(imagen.height * escala))
  adaptada = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

  nombre = f'{nombre_foto}_{red.lower()}'
  adaptada.save(_ruta_salida(archivo_salida, f'{nombre}.png'))
  adaptada.info['nombre'] = nombre
  adaptada.info['tamano_original'] = imagen.size
  adaptada.info['tamano_red'] = (ancho, alto)
  return adaptada


def _validar_imagen(imagen):
  if not isinstance(imagen, Image.Image):
    raise ValueError('Primero debe cargar una imagen válida de Pillow')


def mostrar_imagen(imagen_original, imagen_modificada, titulo_modificada, archivo_salida,
                   histogramas=None):
  """Muestra la imagen original y la modificada lado a lado y guarda la figura.

  histogramas: None, o un par (valores_originales, valores_resultantes) de brillo
  entre 0 y 255; en ese caso agrega debajo el histograma de cada imagen.
  """
  filas = 1 if histogramas is None else 2
  figura, ejes = plt.subplots(filas, 2, figsize=(12, 5 if filas == 1 else 8), squeeze=False)
  try:
    for eje, imagen, titulo in ((ejes[0, 0], imagen_original, 'Imagen original'),
                                (ejes[0, 1], imagen_modificada, titulo_modificada)):
      eje.imshow(imagen, cmap='gray', vmin=0, vmax=255)
      eje.set_title(titulo)
      eje.axis('off')

    if histogramas is not None:
      for eje, valores, titulo in ((ejes[1, 0], histogramas[0], 'Brillo original'),
                                   (ejes[1, 1], histogramas[1], 'Brillo resultante')):
        eje.hist(np.asarray(valores).ravel(), bins=np.arange(257), color='gray')
        eje.set_xlim(0, 256)
        eje.set_title(titulo)
        eje.set_xlabel('Brillo (V de HSV)')
        eje.set_ylabel('Cantidad de píxeles')

    figura.tight_layout()
    figura.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.show()
  finally:
    plt.close(figura)


def ecualizador(imagen, archivo_salida=None):
  """Ajusta el contraste ecualizando el histograma del brillo y devuelve una imagen RGB.

  Convierte la foto a HSV y ecualiza solo el brillo V, conservando el tono H y
  la saturación S, de modo que mejora el contraste sin cambiar los colores. No
  reconstruye detalle perdido. Muestra y guarda la foto original, la ecualizada
  y sus histogramas en <foto>_ecualizada.png, o en archivo_salida si se indica.
  No modifica la imagen recibida.
  """
  _validar_imagen(imagen)
  hsv = cv2.cvtColor(np.array(imagen.convert('RGB')), cv2.COLOR_RGB2HSV)
  h, s, brillo = cv2.split(hsv)
  brillo_resultado = cv2.equalizeHist(brillo)
  rgb_ecualizado = cv2.cvtColor(cv2.merge((h, s, brillo_resultado)), cv2.COLOR_HSV2RGB)
  resultado = Image.fromarray(rgb_ecualizado)

  nombre = imagen.info.get('nombre', 'imagen')
  mostrar_imagen(imagen, resultado, 'Imagen ecualizada - brillo',
                 _ruta_salida(archivo_salida, f'{nombre}_ecualizada.png'),
                 histogramas=(brillo, brillo_resultado))
  return resultado


def filtros(imagen, filtro, archivo_salida=None):
  """Aplica uno de los 9 filtros de Pillow, elegido por nombre o número.

  Filtros: 1 Blur, 2 Contour, 3 Detail, 4 Edge Enhance, 5 Edge Enhance More,
  6 Emboss, 7 Find Edges, 8 Sharpen, 9 Smooth (sin distinguir mayúsculas).
  Muestra la original y la filtrada lado a lado, con el nombre del filtro como
  título, y guarda la figura en <foto>_filtro_<nombre>.png, o en archivo_salida
  si se indica. Devuelve una nueva imagen de Pillow sin modificar la original.
  """
  _validar_imagen(imagen)
  if not isinstance(filtro, str):
    raise ValueError('Ingrese el nombre o número de un filtro')

  seleccion = filtro.strip().lower()
  for numero, (nombre_filtro, filtro_pillow) in enumerate(FILTROS, start=1):
    if seleccion in (nombre_filtro.lower(), str(numero)):
      break
  else:
    raise ValueError(f'No se puede aplicar el filtro {filtro}')

  imagen_filtrada = imagen.convert('RGB').filter(filtro_pillow)

  nombre = imagen.info.get('nombre', 'imagen')
  sufijo = nombre_filtro.lower().replace(' ', '_')
  mostrar_imagen(imagen, imagen_filtrada, nombre_filtro,
                 _ruta_salida(archivo_salida, f'{nombre}_filtro_{sufijo}.png'))
  return imagen_filtrada


def boceto(image, metodo, invertir, umbral, kernel, umbral1=50, umbral2=150,
           archivo_salida=None):
  """Resalta los bordes de una foto como un boceto de líneas y devuelve un array uint8.

  metodo: Canny, Sobel, Laplaciano o Umbral, también por número (1 a 4).
  Canny usa umbral1 y umbral2 (0 <= umbral1 < umbral2 <= 255) y un núcleo de
  3, 5 o 7. Sobel y Laplaciano usan umbral y un núcleo de 1, 3, 5, 7 o 9; su
  umbral se aplica a la intensidad del borde normalizada a 0-255, por lo que
  no depende del tamaño del núcleo. Umbral usa solo umbral. invertir intercambia negro y blanco (True da líneas
  negras sobre fondo blanco). El resultado es binario (0 o 255). Muestra la
  original y el boceto lado a lado y guarda la figura en
  <foto>_boceto_<técnica>.png, o en archivo_salida si se indica.
  """
  _validar_imagen(image)
  if not isinstance(metodo, str):
    raise ValueError('Ingrese el nombre o número de una técnica')
  if not isinstance(invertir, bool):
    raise ValueError('La opción invertir debe ser True o False')

  metodo = metodo.strip().capitalize()
  metodo = TECNICAS.get(metodo, metodo)
  if metodo not in TECNICAS.values():
    raise ValueError(f'El método {metodo} no es válido')

  if metodo == 'Canny':
    if not isinstance(kernel, int) or kernel not in (3, 5, 7):
      raise ValueError('Canny requiere un núcleo de tamaño 3, 5 o 7')
    if not isinstance(umbral1, int) or not isinstance(umbral2, int):
      raise ValueError('Los umbrales de Canny deben ser números enteros')
    if not 0 <= umbral1 < umbral2 <= 255:
      raise ValueError('Canny requiere 0 <= umbral1 < umbral2 <= 255')
  else:
    if not isinstance(umbral, int) or not 0 <= umbral <= 255:
      raise ValueError('El umbral debe ser un número entero entre 0 y 255')
    if metodo != 'Umbral':
      if not isinstance(kernel, int) or kernel not in (1, 3, 5, 7, 9):
        raise ValueError('El núcleo debe tener tamaño 1, 3, 5, 7 o 9')

  gris = cv2.cvtColor(np.array(image.convert('RGB')), cv2.COLOR_RGB2GRAY)
  gris = cv2.normalize(gris, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

  if metodo == 'Canny':
    bordes = cv2.Canny(gris, umbral1, umbral2, apertureSize=kernel)
  elif metodo == 'Sobel':
    gx = cv2.Sobel(gris, cv2.CV_64F, 1, 0, ksize=kernel)
    gy = cv2.Sobel(gris, cv2.CV_64F, 0, 1, ksize=kernel)
    magnitud = np.sqrt(gx**2 + gy**2)
    magnitud = cv2.normalize(magnitud, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, bordes = cv2.threshold(magnitud, umbral, 255, cv2.THRESH_BINARY)
  elif metodo == 'Laplaciano':
    laplaciano = np.abs(cv2.Laplacian(gris, cv2.CV_64F, ksize=kernel))
    laplaciano = cv2.normalize(laplaciano, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, bordes = cv2.threshold(laplaciano, umbral, 255, cv2.THRESH_BINARY)
  else:
    _, bordes = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)

  imagen_binaria = bordes.astype(np.uint8)
  if invertir:
    imagen_binaria = cv2.bitwise_not(imagen_binaria)

  nombre = image.info.get('nombre', 'imagen')
  sufijo = '_invertido' if invertir else ''
  mostrar_imagen(image, imagen_binaria, f'Boceto - {metodo}',
                 _ruta_salida(archivo_salida, f'{nombre}_boceto_{metodo.lower()}{sufijo}.png'))
  return imagen_binaria


ERRORES_ESPERADOS = (ValueError, OSError, requests.RequestException, cv2.error)

MENU = '''
===== FOTOAPP =====
1. Cargar una imagen y adaptarla a una red social
2. Ajustar el contraste (ecualizar el histograma)
3. Aplicar un filtro
4. Resaltar bordes (boceto)
5. Salir
Seleccione una opción: '''

OPCIONES = {
  '1': '1', 'cargar': '1',
  '2': '2', 'ecualizar': '2', 'contraste': '2',
  '3': '3', 'filtro': '3', 'filtros': '3',
  '4': '4', 'boceto': '4', 'bordes': '4',
  '5': '5', 'salir': '5',
}


def _leer_entero(mensaje):
  texto = input(mensaje).strip()
  try:
    return int(texto)
  except ValueError:
    raise ValueError(f'"{texto}" no es un número entero') from None


def _mostrar_adaptacion(imagen):
  plt.figure(figsize=(6, 6))
  plt.imshow(imagen)
  plt.title(f'Imagen adaptada: {imagen.width} x {imagen.height} píxeles')
  plt.axis('off')
  plt.show()
  plt.close()


def _pedir_boceto(imagen):
  metodo = input('Técnica (1 Canny, 2 Sobel, 3 Laplaciano, 4 Umbral): ').strip().capitalize()
  metodo = TECNICAS.get(metodo, metodo)
  if metodo not in TECNICAS.values():
    raise ValueError('Ingrese una técnica válida')

  umbral, umbral1, umbral2, kernel = 0, 50, 150, 3
  if metodo == 'Canny':
    umbral1 = _leer_entero('Umbral inferior (0 a 254; recomendado 50): ')
    umbral2 = _leer_entero('Umbral superior (mayor al inferior, hasta 255; recomendado 150): ')
    kernel = _leer_entero('Tamaño del núcleo (3, 5 o 7; recomendado 3): ')
  else:
    umbral = _leer_entero('Umbral (0 a 255): ')
    if metodo != 'Umbral':
      kernel = _leer_entero('Tamaño del núcleo (1, 3, 5, 7 o 9; recomendado 3): ')

  respuesta = input('¿Líneas negras sobre fondo blanco? (Sí/No): ').strip().lower()
  if respuesta not in ('sí', 'si', 'no'):
    raise ValueError('Responda Sí o No')
  boceto(imagen, metodo, respuesta in ('sí', 'si'), umbral, kernel, umbral1, umbral2)


def main(ruta=None):
  """Menú por consola de FotoApp.

  Exige cargar y adaptar una imagen (opción 1) antes de las demás operaciones.
  Cada operación parte de la imagen adaptada, sin acumular efectos, y guarda su
  resultado en fotos_mejoradas. Si una carga falla se conserva la imagen anterior.
  ruta, opcional, se usa como ruta de la primera carga.
  """
  imagen = None
  while True:
    try:
      opcion = OPCIONES.get(input(MENU).strip().lower())
      if opcion is None:
        raise ValueError('Ingrese una opción válida')
      if opcion == '5':
        print('FotoApp finalizada.')
        return

      if opcion == '1':
        ruta_imagen = ruta if ruta is not None else input('Ruta local o URL directa de la imagen: ').strip()
        ruta = None
        redes = ', '.join(f'{numero} {red}' for numero, red in enumerate(REDES, start=1))
        red = input(f'Red social ({redes}): ').strip()
        imagen = publicar_foto(ruta_imagen, red)
        print(f'Imagen adaptada a {imagen.width} x {imagen.height} píxeles '
              f'y guardada en {CARPETA_RESULTADOS.name}.')
        _mostrar_adaptacion(imagen)
        continue

      if imagen is None:
        raise ValueError('Primero debe cargar y adaptar una imagen con la opción 1')

      if opcion == '2':
        ecualizador(imagen)
      elif opcion == '3':
        nombres = ', '.join(f'{numero} {nombre}' for numero, (nombre, _) in enumerate(FILTROS, start=1))
        filtros(imagen, input(f'Filtro ({nombres}): ').strip())
      else:
        _pedir_boceto(imagen)
      print(f'Comparación guardada en {CARPETA_RESULTADOS.name}.')

    except ERRORES_ESPERADOS as error:
      print(f'Error: {error}. Puede volver a intentarlo desde el menú.')
    except (EOFError, KeyboardInterrupt):
      print('\nFotoApp finalizada.')
      return


if __name__ == '__main__':
  main()
