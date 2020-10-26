#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import colorsys
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

class AlgoritmoAplicarMascara(Algoritmo):
  """
  Aplica la mascara a la imagen original
  La mascara debe ser una imagen binaria blanco y negro.
  """
  def __init__(self, original, mascara):
    self.original = original
    self.mascara = mascara

  def aplicar_en_pixel(self, x, y, img):
    if (self.mascara.getpixel((x, y)) != WHITE):
      return self.original.getpixel((x, y))
    else:
      return (42, 183, 242)

class AlgoritmoRotacion(Algoritmo):
  """
  Rota los colores de hue de la imagen tantos grados como se indica en el constructor.
  """
  def __init__(self, grados):
    self.offset = grados / 360
    print (self.offset)

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

class AlgoritmoValueToGrayscaleIgnoreBlue(Algoritmo):
  def aplicar_en_pixel(self, x, y, img):
    r, g, b = img.getpixel((x, y))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    if (0.5 < h < 0.8):
      return BLACK
    else:
      value = int(v * 255)
      return (value,value,value,)

class AlgortimoUmbralAutomatico(Algoritmo):
  """
  Encuentra el threshold de una imagen en escala de grises, utilizando
  el método de Otsu.
  Ver:
    http://en.wikipedia.org/wiki/Otsu%27s_method
    http://www.labbookpages.co.uk/software/imgProc/otsuThreshold.html
  """
  def __init__(self, histo, ancho, alto):
    self.histo = histo
    self.umbral = self.get_umbral(histo, ancho, alto)

  def get_umbral(self, histo, ancho, alto):
    total = ancho * alto
    suma = float()
    for i in range(0,256):
      suma += (i * histo[i])

    suma_b = float()
    w_b = int()
    w_f = int()
    var_max = float()
    threshold = 0

    for t in range(0, 256):
      w_b += histo[t] # weight background
      if (w_b == 0): continue

      w_f = total - w_b #weight foreground
      if(w_f == 0): break

      suma_b += float(t * histo[t])

      m_b = float() #mean background
      m_f = float() #mean foreground

      m_b = suma_b / w_b
      m_f = (suma - suma_b) / w_f

      var_between = float()
      var_between = float(w_b) * float(w_f) * (m_b - m_f) * (m_b - m_f)

      if (var_between > var_max):
        var_max = var_between
        threshold = t

    return threshold


  def aplicar_en_pixel(self, x, y, img):
    r, g, b = img.getpixel((x, y))
    if (r < self.umbral):
      return BLACK
    else:
      return WHITE

class AlgoritmoErosion(Algoritmo):

  def __init__(self, str_elem):
    """
    str_elem: Filtro para erosionar. Tambien se lo llama elemento estructurante.
    """
    self.str_elem = str_elem

  def ancho(self, size):
    return (1, size[0]-1)

  def alto(self, size):
    return (1, size[1]-1)

  def aplicar_en_pixel(self, x, y, img):
    r, _, _ = img.getpixel((x, y))
    #Si es fondo, lo dejamos como esta.
    if (r == 0):
        return BLACK
    else:
      #Si al menos uno de los pixels que rodean al x,y es fondo, el pixel en x,y es fondo.
      for xx, yy, _ in self.str_elem:
        if (img.getpixel((x + xx, y + yy))[0] == 0):
          return BLACK
    return WHITE

class AlgoritmoDilatacion(Algoritmo):

  def __init__(self, str_elem):
    """
    str_elem: Filtro para erosionar. Tambien se lo llama elemento estructurante.
    """
    self.str_elem = str_elem

  def ancho(self, size):
    return (1, size[0]-1)

  def alto(self, size):
    return (1, size[1]-1)

  def aplicar_en_pixel(self, x, y, img):
    r, _, _ = img.getpixel((x, y))
    #Si es objeto, lo dejamos como esta.
    if (r == 255):
        return WHITE
    else:
      #Si al menos uno de los pixels que rodean al x,y es objeto, el pixel en x,y es objeto.
      for xx, yy, _ in self.str_elem:
        if (img.getpixel((x + xx, y + yy))[0] == 255):
          return WHITE
    return BLACK

class AlgoritmoResta(Algoritmo):
  """
  En cada pixel que es diferente entre original e img, se pone el de img.
  La operacion es img - original.
  Los pixeles que coinciden entre las dos imagenes, se pasan a negro.
  """
  def __init__(self, original):
    self.original = original

  def aplicar_en_pixel(self, x, y, img):
    pix_otra = self.original.getpixel((x, y))
    if (img.getpixel((x, y)) == pix_otra):
      return BLACK
    else:
      return pix_otra

class AlgoritmoBorrar(Algoritmo):
  """
  En cada pixel de color negro en la imagen original
  es eliminado de la imagen.
  """
  def __init__(self, original):
    self.original = original

  def aplicar_en_pixel(self, x, y, img):

    """img es monocromatica"""
    if (img.getpixel((x, y)) == BLACK ):
      return BLACK
    else:
      return self.original.getpixel((x, y))


if __name__ == "__main__":
  pass
