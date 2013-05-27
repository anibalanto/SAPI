# -*- coding: utf-8 -*-
from __future__ import division
import colorsys

class GenMedidasImagen(object):
  @staticmethod
  def generar(medidores, img):
    ancho, alto = img.size
    for x in range(ancho):
      for y in range(alto):
        for medidor in medidores:
          medidor.procesar(img.getpixel((x, y)))

class Medida(object):
  def procesar(pixel):
    raise NotImplementedError

  def rgb_to_hsv(self, pixel):
    h, s, v = colorsys.rgb_to_hsv(pixel[0]/255, pixel[1]/255, pixel[2]/255)
    h = h * 359
    s = s * 100
    v = v * 100
    return (h,s,v)

class Promedio(Medida):
  def __init__(self):
    self.a = float()
    self.b = float()
    self.c = float()
    self.cant = 0

  def procesar(self, pixel):
    self.a += pixel[0]
    self.b += pixel[1]
    self.c += pixel[2]
    self.cant += 1

  def get_valor(self):
    return (self.a/self.cant, self.b/self.cant, self.c/self.cant)

class PromedioRGB(Promedio):
  def get_nombre(self):
    return "Promedio de rojo, verde y azul."

class PromedioHSV(Promedio):
  def get_nombre(self):
    return "Promedio de hue, value y saturation."

  def procesar(self, pixel):
    super(PromedioHSV, self).procesar(self.rgb_to_hsv(pixel))

class Mediana(Medida):

  def __init__(self):
    self.valoresa = []
    self.valoresb = []
    self.valoresc = []
    self.cant = 0


  def procesar(self, pixel):
    a, b, c = pixel
    self.valoresa.append(a)
    self.valoresb.append(b)
    self.valoresc.append(c)
    self.cant += 1

  def get_valor(self):
    mitad = int(self.cant / 2)
    if (self.cant % 2 == 0):
      return (
          (self.valoresa[mitad] + self.valoresa[mitad+1]) / 2,
          (self.valoresb[mitad] + self.valoresb[mitad+1]) / 2,
          (self.valoresc[mitad] + self.valoresc[mitad+1]) / 2,
      )
    else:
      return (self.valoresa[mitad], self.valoresb[mitad], self.valoresc[mitad])

class MedianaRGB(Mediana):
  def get_nombre(self):
    return "Mediana de rojo, verde y azul."

class MedianaHSV(Mediana):
  def get_nombre(self):
    return "Mediana de hue, value y saturation."

  def procesar(self, pixel):
    super(MedianaHSV, self).procesar(self.rgb_to_hsv(pixel))

