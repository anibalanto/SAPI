#!/usr/bin/env python
# -*- coding: utf-8 -*-

from imagen import ImagenArchivo, ImagenVacia
from colores import *
import sys
import random
from transformador import *
from colors import *
from filtros import *

class Segmento(object):
  def __init__(self):
    self.elementos_enteros = []
    self.elementos_perimetro = []
    self.cant = 0
    self.maxx = -9999
    self.maxy = -9999
    self.minx = 99999
    self.miny = 99999

  def get_elementos_enteros(self):
    return self.elementos_enteros

  def get_elementos_perimetro(self):
    return self.elementos_perimetro

  def add_elemento_perimetro(self, x, y):
    self.elementos_perimetro.append((x, y))

  def add_elemento_entero(self, x, y):
    self.elementos_enteros.append((x, y))
    self.cant += 1

    if (self.maxx < x):
      self.maxx = x
    else:
      if (self.minx > x):
        self.minx = x

    if (self.maxy < y):
      self.maxy = y
    else:
      if (self.miny > y):
        self.miny = y

  def __str__(self):
    return "segmento: elementos: {0}".format(self.elementos)

class SegmentoManager(object):
  def __init__(self, ancho, alto):
    self.ancho = ancho
    self.alto = alto
    self.mat = [[None for i in range(alto)] for j in range(ancho)]
    self.segmentos = []

  def get_segmentos(self):
    return self.segmentos

  def unir(self, seg1, seg2):
    """
    Unimos dos segmentos en uno.
    El que menos elementos tiene se suma al que mas tiene
    """
    l1 = len(seg1.get_elementos_enteros())
    l2 = len(seg2.get_elementos_enteros())
    if l1 < l2:
      menor = seg1
      mayor = seg2
    else:
      menor = seg2
      mayor = seg1

    for i in menor.get_elementos_enteros():
      x, y = i
      mayor.add_elemento_entero(x, y)
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
      seg.add_elemento_entero(x, y)
    else:
      seg = Segmento()
      seg.add_elemento_entero(x, y)
      self.segmentos.append(seg)

    self.mat[x][y] = seg

  def add_pixel_perimetro(self, x, y):
    self.mat[x][y].add_elemento_perimetro(x, y)

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

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

def mostrar_segmentos(segmentos_manager, size):
  """
  Muestra los segmentos, del SegmentosManager pasado como parametro, en una imagen. Cada segmento se muestra con un
  color elegido al azar.
  """
  print "hay {0} segmentos".format(len(segmentos_manager.segmentos))
  img = ImagenVacia("RGB", size)
  for seg in segmentos_manager.segmentos:

    col = (int(random.random() * 255),int(random.random() * 255),int(random.random() * 255))
    for e in seg.get_elementos_enteros():
      img.putpixel(e, col)

    for e in seg.get_elementos_perimetro():
      img.putpixel(e, YELLOW)

  img.show()

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

if __name__ == '__main__':
  img_in = sys.argv[1]
  img_binaria = cargar(img_in)
  img_perimetros = get_img_perimetros(img_binaria)
  smanager = run_codes(img_binaria, img_perimetros)
  mostrar_segmentos(smanager, img_binaria.size)
  #for s in smanager.segmentos:
  #  print s.get_area()
