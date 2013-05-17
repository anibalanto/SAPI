#! /usr/bin/env python

from __future__ import division
from imagen import Imagen, ImagenArchivo, ImagenVacia
import ImageDraw
import sys
import colorsys
import histograma
from transformador import Transformador
from colores import *
from algoritmo import Algoritmo

class AlgoritmoRojisidad(Algoritmo):
  def rojisidad (self, r, g, b):
    res = int(r-(g + b)/2)
    if (res < 0): 
      return 0
    return res

  def aplicar_en_pixel(self, x, y, img):
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

  def aplicar_en_pixel(self, x, y, img):
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

  def aplicar_en_pixel(self, x, y, img):
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

  def aplicar_en_pixel(self, x, y, img):
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = (h + self.offset) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

class AlgoritmoHSVtoGrayscale(Algoritmo):
  """
  Convierte una imagen a escala de grises. Los valores de h mas cercanos al, hmax pasado al contructor,
  se mapean a la intensidad 255. Cuanto mas lejos del hmax, los valores de h se traducen en intensidades
  cercanas al 0.
  """

  def __init__(self, centro):
    """
    El centro indica el valor de h que queremos mapear a la intensidad maxima de gris.
    0.0 <= centro <= 1.0
    """
    self.centro = centro
    self.centro2 = centro + 1.0

  def calc_distancia(self, h, centro, seg_centro):
    return min(abs(centro - h), abs(seg_centro - h))

  def aplicar_en_pixel(self, x, y, img):
    #TODO: agregar filtro por s y v
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    intensidad = 255
    if (s > 0.4 and v > 0.4):
      distancia = self.calc_distancia(h, self.centro, self.centro2)
      intensidad = int(distancia * 255)
    return (intensidad,intensidad,intensidad)

class AlgoritmoValueToGrayscale(Algoritmo):
  def aplicar_en_pixel(self, x, y, img):
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    value = int(v * 255)
    return (value,value,value,)

if __name__ == "__main__":
  pass
