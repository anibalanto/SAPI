# -*- coding: utf-8 -*-
from __future__ import division
import colorsys
from collections import Counter
from colores import BLUE

def no_azul(r, g, b, h, s, v):
  """
  h: 0 - 359
  s: 0 - 100
  v: 0 - 100
  """
  return not (r, g, b) == BLUE

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

class MomentosInvariantes(MedidaSegmento):
  """
  Ver digital image processing pag. 700.
  El centro de masa se calcula así: (x, y) = (M10/M00, M01/M00)
  donde Mpq es el momento de orden p+q.
  El momento M00, es igual al area del segmento. Es decir la cantidad
  de pixels que componen el area.
  """
  def __init__(self, segmento, momento_00):
    super(MomentosInvariantes, self).__init__(segmento)
    self.m00 = momento_00
    self.m10 = self.get_momento(self.segmento, lambda x: x[0])
    self.m01 = self.get_momento(self.segmento, lambda x: x[1])
    self.x_centro = self.m10 / self.m00
    self.y_centro = self.m01 / self.m00
    self.m11 = self.get_momento(self.segmento, lambda x: x[0] * x[1])

    self.m20 = self.get_momento(self.segmento, lambda x: x[0] ** 2)
    self.m02 = self.get_momento(self.segmento, lambda x: x[1] ** 2)

    self.m12 = self.get_momento(self.segmento, lambda x: x[0] * (x[1] ** 2))
    self.m21 = self.get_momento(self.segmento, lambda x: (x[0] ** 2) * x[1])

    self.m30 = self.get_momento(self.segmento, lambda x: x[0] ** 3)
    self.m03 = self.get_momento(self.segmento, lambda x: x[1] ** 3)

    self.invariantes = self.calc_invariantes()

  def get_momento(self, segmento, f):
    """
    sum x sum y x^p * y^q * b(x,y)
    """
    return sum(map(f, segmento.get_elementos_enteros()))

  def calc_invariantes(self):
    #u11 = m11 - ymed * m10
    u = {
    "u00" : self.m00,
    "u10" : 0,
    "u01" : 0,
    "u11" : self.m11 - self.y_centro * self.m10,
    "u20" : self.m20 - self.x_centro * self.m10,
    "u02" : self.m02 - self.y_centro * self.m01,
    "u30" : self.m30 - 3 * self.x_centro * self.m20 + 2 * (self.x_centro ** 2) * self.m10,
    "u03" : self.m03 - 3 * self.y_centro * self.m02 + 2 * (self.y_centro ** 2) * self.m01,
    "u21" : self.m21 - 2 * self.x_centro * self.m11 - self.y_centro * self.m20 + 2 * (self.x_centro ** 2) * self.m01,
    "u12" : self.m12 - 2 * self.y_centro * self.m11 - self.x_centro * self.m02 + 2 * (self.y_centro ** 2) * self.m10,
    }
    norm = self.normalizar(u)
    return self.calc_desde_norm(norm)

  def normalizar(self, u):
    u00 = u["u00"]
    gamma = lambda p, q: ((p + q) / 2) + 1
    norm = lambda x, y, z: x / (y ** z)
    n = {
        "n00" : norm(u["u00"], u00, gamma(0,0)),
        "n10" : norm(u["u10"], u00, gamma(1,0)),
        "n01" : norm(u["u01"], u00, gamma(0,1)),
        "n11" : norm(u["u11"], u00, gamma(1,1)),
        "n20" : norm(u["u20"], u00, gamma(2,0)),
        "n02" : norm(u["u02"], u00, gamma(0,2)),
        "n12" : norm(u["u12"], u00, gamma(1,2)),
        "n21" : norm(u["u21"], u00, gamma(2,1)),
        "n30" : norm(u["u30"], u00, gamma(3,0)),
        "n03" : norm(u["u03"], u00, gamma(0,3)),
    }
    return n

  def calc_desde_norm(self, n):
    ret = [
        n["n20"] + n["n02"],
        (n["n20"] - n["n02"]) ** 2 + 4 * (n["n11"] ** 2),
        (n["n30"] - 3 * n["n12"]) ** 2 + (3 * n["n21"] - n["n03"]) ** 2
    ]
    return ret

  def get_valor(self):
    return [self.invariantes, (int(self.x_centro), int(self.y_centro))]
