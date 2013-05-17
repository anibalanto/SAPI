#! /usr/bin/env python

"""
Implementacion de reduccion de ruido
"""

from __future__ import division
import Image
import sys
import math
from algoritmo import Algoritmo

class AlgoritmoRuido(Algoritmo):

  def __init__(self, ancho, alto):
    self.ancho = ancho
    self.alto = alto

  def gen_matriz(self, cant_vecinos):
    """
    genera los valores de i y j para recorrer una matriz
    i va de -cant_vecinos a cant_vecinos
    j va de -cant_vecinos a cant_vecinos
    """
    for i in range(-cant_vecinos, cant_vecinos+1):
      for j in range(-cant_vecinos, cant_vecinos+1):
        yield(i,j)

class AlgoritmoPromedioSimple(Algoritmo):
  def aplicar_en_pixel(self, xx, yy, img):
    """
    aplica un promedio simple
    la matriz es de 3 x 3 con todos 1
    """
    #No hacemos nada para los bordes
    if not (0 < yy < self.alto-1):
      return img.getpixel((xx, yy))
    if not (0 < xx < self.ancho-1):
      return img.getpixel((xx, yy))

    filtro = [
        [1,1,1],
        [1,1,1],
        [1,1,1],
    ]
    total = 9
    sumar = 0.0
    sumag = 0.0
    sumab = 0.0
    for x, y in self.gen_matriz(1):
      try:
        r, g, b = img.getpixel((xx+x, yy+y))
      except:
        print xx
        print yy
        raise
      sumar += filtro[x][y] * r
      sumag += filtro[x][y] * g
      sumab += filtro[x][y] * b

    return (int(sumar/total), int(sumag/total), int(sumab/total))

class AlgoritmoMediana(AlgoritmoRuido):
  def aplicar_en_pixel(self, xx, yy, img):
    """
    retorna el valor del pixel de acuerdo a la mediana 
    ver pag 34 teoria3
    """
    #No hacemos nada para los bordes
    if not (0 < yy < self.alto-1):
      return img.getpixel((xx, yy))
    if not (0 < xx < self.ancho-1):
      return img.getpixel((xx, yy))

    r = []
    g = []
    b = []
    for x,y in self.gen_matriz(1):
      rr, gg, bb = img.getpixel((xx+x, yy+y))
      r.append(rr)
      g.append(gg)
      b.append(bb)
    r.sort()
    g.sort()
    b.sort()
    return (r[int(len(r)/2)], g[int(len(g)/2)],b[int(len(b)/2)]) 

class AlgoritmoMedianaPromedio(AlgoritmoRuido):
  def aplicar_en_pixel(self, xx, yy, img):
    """
    Calcula el promedio sin tener en cuenta a los extremos
    ver pag 34 teoria3
    """
    #No hacemos nada para los bordes
    if not (0 < yy < self.alto-1):
      return img.getpixel((xx, yy))
    if not (0 < xx < self.ancho-1):
      return img.getpixel((xx, yy))

    r = []
    g = []
    b = []
    for x,y in self.gen_matriz(1):
      rr, gg, bb = img.getpixel((xx+x, yy+y))
      r.append(rr)
      g.append(gg)
      b.append(bb)
    r.sort()
    g.sort()
    b.sort()
    r = r[1:-1]
    g = g[1:-1]
    b = b[1:-1]
    return (r[int(len(r)/2)], g[int(len(g)/2)],b[int(len(b)/2)]) 

if __name__ == "__main__":
  pass
