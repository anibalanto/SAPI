#! /usr/bin/env python

from __future__ import division
from imagen import Imagen, ImagenArchivo, ImagenVacia
import ImageDraw
import sys
import colorsys
import histograma
from transformador import Transformador
from colores import *


def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

class Algoritmo(object):
  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Llamado por Transformador.aplicar.
    Debe devolver una tupla con los valores de r, g y b
    ej: return (34, 233, 10)
    """
    raise NotImplementedError

class AlgoritmoRojisidad(Algoritmo):
  def rojisidad (self, r, g, b):
    res = int(r-(g + b)/2)
    if (res < 0): 
      return 0
    return res

  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Devuelve el nivel de rojo que tiene cada pixel
    """
    (r,g,b,i) = img.getpixel((x, y))
    return (self.rojisidad(r,g,b), self.rojisidad(r,g,b), self.rojisidad(r,g,b))

class AlgoritmoUmbralHSV(Algoritmo):
  """
  Crea una imagen binaria donde los pixels que caen dentro del intervalo indicado en el constructor,
  se muestran como blancos y el resto como negros.
  """

  def __init__(self, h_h, h_l, v_h, v_l, s_h, s_l):
    self.hh = h_h
    self.hl = h_l
    self.vh = v_h
    self.vl = v_l
    self.sh = s_h
    self.sl = s_l

  def en_intervalo_hue(self, h, hl, hh):
    #Existen casos en los que h low es menor que h high. Esto se puede dar cuando queremos
    #un intervalo de hue que cae sobre el comienzo de la rueda.
    if (hh < hl):
      return not (hh <= h <= hl)
    else:
      return (hl <= h <= hh)

  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Devuelve blanco si esta por arriba del umbral y negro si esta por debajo
    """
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = h * 359
    s = s * 100
    v = v * 100

    col = BLACK
    if (self.en_intervalo_hue(h, self.hl, self.hh) and (self.vl <= v <= self.vh) and (self.sl <= s <= self.sh)):
      col = WHITE

    return col

class AlgoritmoCombinar(Algoritmo):
  """
  Aplica algo similar al operador and entre original y la imagen a la que se le aplica el algoritmo.
  """
  def __init__(self, original):
    self.original = original

  def aplicar_en_pixel(self, x, y, img, ret):
    if (img.getpixel((x, y)) == WHITE):
      return BLUE
    else:
      return self.original.getpixel((x, y))

class AlgoritmoRotacion(Algoritmo):
  """
  Rota los colores de hue de la imagen tantos grados como se indica en el constructor.
  """
  def __init__(self, grados):
    self.offset = grados / 360
    print self.offset

  def aplicar_en_pixel(self, x, y, img, ret):
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = (h + self.offset) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

if __name__ == "__main__":
  origen = cargar(sys.argv[1])
  origen.show()

  trans = Transformador()

  #algoritmo = AlgoritmoUmbral(0.17)
  algoritmo = AlgoritmoRotacion(40)
  destino = trans.aplicar(algoritmo, origen)
  destino.show()

  #histograma.crear_histograma(destino)
