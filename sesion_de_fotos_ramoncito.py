#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
La idea es mostrar los valores de los algoritmos implementados hasta ahora, usando las fotos que sacaron
en octubre de 2013.
"""

import sys
import aplicar_algoritmos
import runcode
import glob
import imagen
import medidas
import colores

def segmentar(img_original):
  """
  Segmentamos la imagen de entrada. Retornamos una tupla con la imagen segmentada, la imagen de perimetros y el
  SegmentoManager que creamos.
  """
  img_segmentada = aplicar_algoritmos.segmentar(img_original, False)
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  segman.eliminar_extremos_verticales()
  return (img_segmentada, img_perimetros, segman)

def mostrar_segmentos(segmentos, size):
  colores_list = [colores.RED, colores.BLUE, colores.WHITE, colores.YELLOW, colores.CYAN]
  imagen_segmentos = imagen.ImagenVacia(size)
  for i, seg in enumerate(segmentos):
    for xy in seg.get_elementos_enteros():
      imagen_segmentos.putpixel(xy, colores_list[i])
  imagen_segmentos.show()

def mostrar_valores(img_segmentada, img_perimetros, segman):
  """
  Mostramos las medidas de los segmentos.
  """
  img_segmentada.show()

  #Calculamos los 5 segmentos de mayor area
  cinco_mas_grandes = sorted(
      segman.get_segmentos(),
      cmp = lambda a,b: cmp(medidas.AreaSegmento(a).get_valor(), medidas.AreaSegmento(b).get_valor()),
      reverse = True
      )[0:5]

  #Mostramos los 5 segmentos mas grandes
  mostrar_segmentos(cinco_mas_grandes, img_segmentada.size)

  #Mostramos los datos
  print "areas \t centro de masa \t d. fractal"
  for i in cinco_mas_grandes:
    area =  medidas.AreaSegmento(i).get_valor()
    momentos_dicc = medidas.MomentosInvariantes(i, area).get_valor()
    dfractal = medidas.DimensionFractal(i).get_valor()
    #invariantes =
    print "{0} \t {1} \t {2} \t {3}".format(area, momentos_dicc["centro_float"], dfractal, 0)#momentos_dicc["invariantes"])
  print ""

def generar_valores(lista_imagenes):
  """
  Esta funcion muestra los valores de las 5 manchas de mayor area, de cada una de las imagenes pasadas como parametro
  """
  for img in lista_imagenes:
    img_segmentada = segmentar(img)
    mostrar_valores(*img_segmentada)

def crear_imagen(fname):
  return imagen.ImagenArchivo(fname)

def main():
  path = sys.argv[1]
  filenames = glob.glob(path+"/*.trans.bmp")
  generar_valores(map(crear_imagen, filenames))

if __name__ == "__main__":
  main()
