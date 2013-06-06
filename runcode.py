#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imagen import ImagenArchivo, ImagenVacia
from colores import *
import sys
import random
from transformador import *
from colors import *
from filtros import *
import aplicar_algoritmos
from segmentos import SegmentoManager


def es_borde(x, y, ancho, alto):
  return not ((0 < x < ancho-1) and (0 < y < alto-1))

def run_codes(img_binaria, img_perimetros):
  """
  Genera un conjunto de segmentos a partir de una imagen binaria.
  """
  ancho, alto = img_binaria.size
  segman = SegmentoManager(ancho, alto)

  #Generamos los segmentos a partir de la imagen_binaria
  for y in range(alto):
    for x in range(ancho):
      #el pixel no es borde y es objeto
      if not es_borde(x, y, ancho, alto) and img_binaria.getpixel((x, y)) == WHITE:
        segman.add_pixel(x, y)
  #Una vez que tenemos los segmentos cargados, agregamos los perimetros
  for x in range(ancho):
    for y in range(alto):
      if not es_borde(x, y, ancho, alto) and img_perimetros.getpixel((x, y)) == WHITE:
        segman.add_pixel_perimetro(x, y)

  return segman

def pintar_segmentos(segmentos_manager, size):
  """
  Muestra los segmentos, del SegmentoManager pasado como parametro, en una imagen. Cada segmento se muestra con un
  color elegido al azar.
  """
  print "hay {0} segmentos".format(len(segmentos_manager.segmentos))
  img = ImagenVacia(size)
  for seg in segmentos_manager.segmentos:

    col = (int(random.random() * 255),int(random.random() * 255),int(random.random() * 255))
    for e in seg.get_elementos_enteros():
      img.putpixel(e, col)

    for e in seg.get_elementos_perimetro():
      img.putpixel(e, YELLOW)

  return img

def get_img_perimetros(binaria):
  erosionada = Transformador.aplicar(
      [
        AlgoritmoErosion(Filtro(UNOS, 3)),
      ],
      binaria,
      False
  )
  diferencia = Transformador.aplicar([AlgoritmoResta(binaria)], erosionada, False)
  return diferencia

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

if __name__ == '__main__':
  img_in = sys.argv[1]
  img_binaria = aplicar_algoritmos.segmentar(cargar(img_in), True)
  img_perimetros = get_img_perimetros(img_binaria)
  smanager = run_codes(img_binaria, img_perimetros)
  smanager.eliminar_extremos_verticales()
  mostrar_segmentos(smanager, img_binaria.size)
  #for s in smanager.segmentos:
  #  print s.get_area()
