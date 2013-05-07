#! /usr/bin/env python

from __future__ import division
from imagen import Imagen, ImagenArchivo, ImagenVacia
import ImageDraw
import sys
import colorsys
import histograma

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

class Transformador(object):

  def recorrer_imagen(self, ancho, alto):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    """
    for x in range(1,ancho-1):
      for y in range(1,alto-1):
        yield (x,y)

  def aplicar(self, algoritmo, img):
    """
    Aplica el filtro a la imagen
    """
    ret = ImagenVacia(img.mode, img.size)
    ancho, alto = img.size
    for x,y in self.recorrer_imagen(ancho, alto):
        algoritmo.aplicar_en_pixel(x, y, img, ret)
    return ret

class Algoritmo(object):
  def aplicar_en_pixel(self, x, y, img, ret):
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
    ret.putpixel((x, y), (self.rojisidad(r,g,b), self.rojisidad(r,g,b), self.rojisidad(r,g,b)))

class AlgoritmoUmbralHSV(Algoritmo):

  def __init__(self, h_h, h_l, v_h, v_l, s_h, s_l):
    self.hh = h_h
    self.hl = h_l
    self.vh = v_h
    self.vl = v_l
    self.sh = s_h
    self.sl = s_l

  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Devuelve blanco si esta por arriba del umbral y negro si esta por debajo
    """
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = h * 359
    s = s * 100
    v = v * 100

    val = 0
    if (((0 <= h <= self.hh) or (self.hl <= h <= 359)) and (self.vl <= v <= self.vh) and (self.sl <= s <= self.sh)):
      val = 255

    ret.putpixel((x, y), (val, val, val))

class AlgoritmoCombinar(Algoritmo):
  def __init__(self, original):
    self.original = original

  def aplicar_en_pixel(self, x, y, img, ret):
    if (img.getpixel((x, y)) == WHITE):
      ret.putpixel((x, y), BLUE)
    else:
      ret.putpixel((x, y), self.original.getpixel((x, y)))

class AlgoritmoRotacion(Algoritmo):
  def __init__(self, grados):
    self.offset = grados / 360

  def aplicar_en_pixel(self, x, y, img, ret):
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = h + self.offset % 359
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    ret.putpixel((x, y), (int(r * 255), int(g * 255), int(b * 255)))

if __name__ == "__main__":
  origen = cargar(sys.argv[1])
  origen.show()

  trans = Transformador()

  #algoritmo = AlgoritmoUmbral(0.17)
  algoritmo = AlgoritmoRotacion(40)
  destino = trans.aplicar(algoritmo, origen)
  destino.show()

  histograma.crear_histograma(destino)
