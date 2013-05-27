#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imagen import ImagenArchivo, ImagenVacia
from colores import *
import sys
import random

class Segmento(object):
  def __init__(self):
    self.elementos = []

  def add(self, x, y):
    self.elementos.append((x, y))

  def __str__(self):
    return "segmento: elementos: {0}".format(self.elementos)

class SegmentoManager(object):
  def __init__(self, ancho, alto):
    self.ancho = ancho
    self.alto = alto
    self.mat = [[None for i in range(alto)] for j in range(ancho)]
    self.segmentos = []

  def unir(self, seg1, seg2):
    """
    Unimos dos segmentos en uno.
    El que menos elementos tiene se suma al que mas tiene
    """
    l1 = len(seg1.elementos)
    l2 = len(seg2.elementos)
    if l1 < l2:
      menor = seg1
      mayor = seg2
    else:
      menor = seg2
      mayor = seg1

    for i in menor.elementos:
      x, y = i
      mayor.add(x, y)
      self.mat[x][y] = mayor

    #Eliminamos el segmento que menos elementos tenia
    self.segmentos.remove(menor)

  def add_pixel(self, x, y):
    """
    Agrega el pixel x,y al segmento correspondiente. Puede ser un segmento que ya existia
    o uno nuevo.
    Para decidir que hacer, analizamos la matriz de segmentos en las casillas que se indican
    con @. El pixel x, y se indica con #.
    @ @ @
    @ #
    """
    seg = None

    #Este es el unico caso donde podemos llegar a necesitar unir los segmentos 1 y 2
    # @ @ 1
    # 2 #
    s1 = self.mat[x-1][y]
    s2 = self.mat[x+1][y-1]
    if (s1 is not None) and (s2 is not None):
      if (s1 != s2):
        self.unir(s1, s2)

    #Una vez que unimos, ya podemos tomar cualquiera de los segmentos que no sea None
    segs = [
    self.mat[x-1][y],
    self.mat[x-1][y-1],
    self.mat[x][y-1],
    self.mat[x+1][y-1]
    ]
    for i in segs:
      if i is not None:
        seg = i
        break

    #Anadimos el pixel al segmento, o creamos un segmento nuevo
    if seg != None:
      seg.add(x, y)
    else:
      seg = Segmento()
      seg.add(x, y)
      self.segmentos.append(seg)

    self.mat[x][y] = seg

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def es_borde(x, y, ancho, alto):
  return not ((0 < x < ancho-1) and (0 < y < alto-1))

def run_codes(img):
  """
  Genera un conjunto de segmentos a partir de una imagen binaria.
  """
  ancho, alto = img.size
  segmentos = SegmentoManager(ancho, alto)
  for y in range(alto):
    x = 0
    while x < ancho:
      #el pixel no es borde y es objeto
      if not es_borde(x, y, ancho, alto) and img.getpixel((x, y)) == WHITE:
        segmentos.add_pixel(x, y)
      x += 1

  return segmentos

def mostrar_segmentos(segmentos, size):
  """
  Muestra los segmentos pasados como parametro en una imagen. Cada segmento se muestra con un
  color elegido al azar.
  """
  print "hay {0} segmentos".format(len(segmentos.segmentos))
  img = ImagenVacia("RGB", size)
  for seg in segmentos.segmentos:
    col = (int(random.random() * 255),int(random.random() * 255),int(random.random() * 255))
    for e in seg.elementos:
      img.putpixel(e, col)
  img.show()

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s entrada.bmp salida.bmp" % sys.argv[0]
  else:
    img_in = sys.argv[1]
    img_out = sys.argv[2]
    img = cargar(img_in)
    segmentos = run_codes(img)

