# -*- coding: utf-8 -*-
from __future__ import division
import colorsys
from collections import Counter

def no_azul(r, g, b, h, s, v):
  return not (0.5 < h < 0.8)

def cualquier_color(*args):
  return True

class GeneradorMedidas(object):
  def generar(self, img, gen_xy, chequeo_color):
    valoresr, valoresg, valoresb = [], [], []
    valoresh, valoress, valoresv = [], [], []
    ancho, alto = img.size
    for x,y in gen_xy:
      r, g, b = img.getpixel((x, y))
      h, s, v = rgb_to_hsv((r, g, b))
      if chequeo_color(r,g,b,h,s,v):

        valoresr.append(r)
        valoresg.append(g)
        valoresb.append(b)

        valoresh.append(h)
        valoress.append(s)
        valoresv.append(v)
    return {
        "r": valoresr,
        "g": valoresg,
        "b": valoresb,
        "h": valoresh,
        "s": valoress,
        "v": valoresv,
        }

class GenMedidasImagen(GeneradorMedidas):
  def get_valor(self, img, chequeo_color):
    a = self.gen_xy(img.size)
    return super(GenMedidasImagen, self).generar(img, a, chequeo_color)

  def gen_xy(self, (ancho, alto)):
    for x in range(ancho):
      for y in range(alto):
        yield (x, y)

class GenMedidasSegmento(GeneradorMedidas):
  def get_valor(self, img, segmento, chequeo_color):
    return super(GenMedidasSegmento, self).generar(img, segmento.get_elementos_enteros(), chequeo_color)

class Medida(object):
  def __init__(self, nombre, valores):
    self.valoresa = valores[0]
    self.valoresb = valores[1]
    self.valoresc = valores[2]
    self.cant = len(self.valoresa)
    self.nombre = nombre

  def get_nombre(self):
    return self.nombre

  def get_fields(self):
    raise NotImplementedError

  def get_valor(self):
    raise NotImplementedError

  def get_valor_dict(self):
    raise NotImplementedError

class Mediana(Medida):
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

class Moda(Medida):
  def get_valor(self):
    modaa = Counter(self.valoresa).most_common(1)[0][0]
    modab = Counter(self.valoresb).most_common(1)[0][0]
    modac = Counter(self.valoresc).most_common(1)[0][0]
    return (modaa,modab,modac)

class Varianza(Medida):
  def __init__(self, nombre, valores, medias):
    super(Varianza, self).__init__(nombre, valores)
    self.mediaa, self.mediab, self.mediac = medias

  def get_varianza(self, vector, media):
    suma = float()
    for i in vector:
      suma += (i - media) ** 2
    return suma / self.cant

  def get_valor(self):
    vara = self.get_varianza(self.valoresa, self.mediaa)
    varb = self.get_varianza(self.valoresb, self.mediab)
    varc = self.get_varianza(self.valoresc, self.mediac)
    return (vara, varb, varc)

class Media(Mediana):
  def get_valor(self):
    return (
        sum(self.valoresa) / self.cant,
        sum(self.valoresb) / self.cant,
        sum(self.valoresc) / self.cant,
        )

def rgb_to_hsv(pixel):
  h, s, v = colorsys.rgb_to_hsv(pixel[0]/255, pixel[1]/255, pixel[2]/255)
  h = h * 359
  s = s * 100
  v = v * 100
  return (h,s,v)

def MediaRGB(vals):
  return Media("Media de rojo, verde y azul.", vals)

def MediaHSV(vals):
  return Media("Media de hue, value y saturation.", vals)

def MedianaRGB(vals):
  return Mediana("Mediana de rojo, verde y azul.", vals)

def MedianaHSV(vals):
  return Mediana("Mediana de hue, value y saturation.", vals)

def VarianzaRGB(vals, medias):
  return Varianza("Mediana de rojo, verde y azul.", vals, medias)

def VarianzaHSV(vals, medias):
  return Varianza("Mediana de hue, value y saturation.", vals, medias)

def ModaRGB(vals):
  return Moda("Moda de rojo, verde y azul.", vals)

def ModaHSV(vals):
  return Moda("Moda de hue, saturation, value.", vals)

class MedidaSegmento(object):
  def __init__(self, segmento):
    self.segmento = segmento

class AreaSegmento(MedidaSegmento):
  """
  Retorna el numero de pixels que componen el area. Incluye todos los pixels que componen
  el segmento.
  """
  def get_valor(self):
    return len(self.segmento.get_elementos_enteros())

class PerimetroSegmento(MedidaSegmento):
  """
  Retorna el numero de pixels que componen el perimetro.
  """
  def get_valor(self):
    return len(self.segmento.get_elementos_perimetro())

