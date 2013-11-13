# -*- coding: utf-8 -*-
from __future__ import division
import colorsys
from collections import Counter
from colores import BLUE
import numpy as np

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

class EjeCentralSegmento(MedidaSegmento):
  """
  Retorna el punto x,y del perimetro, mas lejano al centro pasado como parametro.
  """
  def __init__(self, segmento, centro):
    super(EjeCentralSegmento, self).__init__(segmento)
    self.centro = centro

  def get_valor(self):
    maxval = None
    distancia_max = -9999
    for elem in self.segmento.get_elementos_perimetro():
      d = np.linalg.norm(np.array(elem) - np.array(self.centro))#calculamos la distancia euclidea
      if d > distancia_max:
        maxval = elem
        distancia_max = d
    return maxval

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
    #orden 0
    self.m00 = momento_00

    #orden 1
    self.m10 = self.get_momento(self.segmento, lambda x: x[0])
    self.m01 = self.get_momento(self.segmento, lambda x: x[1])

    #orden 2
    self.m11 = self.get_momento(self.segmento, lambda x: x[0] * x[1])
    self.m20 = self.get_momento(self.segmento, lambda x: x[0] ** 2)
    self.m02 = self.get_momento(self.segmento, lambda x: x[1] ** 2)

    #orden 3
    self.m12 = self.get_momento(self.segmento, lambda x: x[0] * (x[1] ** 2))
    self.m21 = self.get_momento(self.segmento, lambda x: (x[0] ** 2) * x[1])
    self.m30 = self.get_momento(self.segmento, lambda x: x[0] ** 3)
    self.m03 = self.get_momento(self.segmento, lambda x: x[1] ** 3)

    self.x_centro = self.m10 / self.m00
    self.y_centro = self.m01 / self.m00

    self.u = self.calc_centrales()
    self.n = self.normalizar(self.u)
    self.invariantes = self.calc_invariantes(self.n)
    self.angulo = self.calc_angulo(self.u)
    self.eccen = self.calc_eccentricity(self.u)


  def get_momento(self, segmento, f):
    """
    sum x sum y x^p * y^q * b(x,y)
    """
    return sum(map(f, segmento.get_elementos_enteros()))

  def calc_centrales(self):
    #calculamos los momentos centrales
    return {
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

  def normalizar(self, u):
    """
    Normalizamos los momentos centrales.
    """
    u00 = u["u00"]
    gamma = lambda p, q: ((p + q) / 2) + 1
    norm = lambda x, y, z: x / (y ** z)
    """
    estos no se calculan
    "n00" : norm(u["u00"], u00, gamma(0,0)),
    "n10" : norm(u["u10"], u00, gamma(1,0)),
    "n01" : norm(u["u01"], u00, gamma(0,1)),
    """
    return {
        "n11" : norm(u["u11"], u00, gamma(1,1)),
        "n20" : norm(u["u20"], u00, gamma(2,0)),
        "n02" : norm(u["u02"], u00, gamma(0,2)),
        "n12" : norm(u["u12"], u00, gamma(1,2)),
        "n21" : norm(u["u21"], u00, gamma(2,1)),
        "n30" : norm(u["u30"], u00, gamma(3,0)),
        "n03" : norm(u["u03"], u00, gamma(0,3)),
    }

  def calc_invariantes(self, n):
    """
    Calculamos los 7 momentos invariantes.
    Lo copiamos de aca: https://github.com/Itseez/opencv/blob/913e6833d5e28d0c308bb8e8ffdc718dd42e4cfc/modules/imgproc/src/moments.cpp
    """
    hu = []

    t0 = n["n30"] + n["n12"]
    t1 = n["n21"] + n["n03"]
    q0 = t0 ** 2
    q1 = t1 ** 2
    n4 = 4 * n["n11"]
    s = n["n20"] + n["n02"]
    d = n["n20"] - n["n02"]

    #momento 1
    hu.append(s)

    #momento 2
    hu.append(d * d + n4 + n["n11"])

    #momento 3
    hu.append(q0 + q1)

    #momento 4
    hu.append(d * (q0 - q1) + n4 * t0 * t1)

    t0 *= q0 - 3 * q1
    t1 *= 3 * q0 - q1
    q0 = n["n30"] - 3 * n["n12"]
    q1 = 3 * n["n21"] - n["n03"]

    #momento 5
    hu.append(q0 * q0 + q1 * q1)

    #momento 6
    hu.append(q0 * t0 + q1 * t1)

    #momento 7
    hu.append(q1 * t0 - q0 * t1)
    return hu

  def calc_angulo(self, u):
    """
    Calculamos el angulo en radianes.
    Ver image moments en wikipedia.
    http://public.cranfield.ac.uk/c5354/teaching/dip/opencv/SimpleImageAnalysisbyMoments.pdf
    """
    up20 = u["u20"]# / u["u00"]
    up02 = u["u02"] #/ u["u00"]
    up11 = u["u11"] #/ u["u00"]
    divisor = (up20 - up02)

    if divisor == 0.0:
      if up11 == 0.0:
        return 0.0
      elif up11 > 0.0:
        return np.pi / 4.0 #45 grados
      elif up11 < 0.0:
        return np.pi / -4.0 #-45 grados

    return 0.5 * np.arctan((2 * up11) / divisor)

  def calc_eccentricity(self, u):
    """
    Para calcular la excentricidad, usamos la formula: e = ((u20 - u02) ^ 2 + 4u11) / m00
    Lo sacamos de aca: "http://www.cs.uu.nl/docs/vakken/ibv/reader/chapter8.pdf para un circulo deberia dar 0.
    """
    return ((u["u20"] - u["u02"]) ** 2 + 4 * u["u11"]) / self.m00


  def get_valor(self):
    return {
        "invariantes" : self.invariantes,
        "centro" : (int(self.x_centro), int(self.y_centro)),
        "centro_float" : (self.x_centro, self.y_centro),
        "angulo" : self.angulo,
        "excentricidad" : self.eccen,
        "centrales" : self.u,
        "normalizados" : self.n,
        "momentos" : {
          "m00" : self.m00,
          "m01" : self.m01,
          "m10" : self.m10,
          "m11" : self.m11,
          "m20" : self.m20,
          "m02" : self.m02,
          "m21" : self.m21,
          "m12" : self.m12,
          "m30" : self.m30,
          "m03" : self.m03,
          },
        }


class DimensionFractal(MedidaSegmento):
  """
  Retorna el numero de pixels que componen el perimetro.
  """
  size = 5

  def get_valor(self):
    box_count =  0
    M = 0
    N = 0
    i = self.segmento.get_minx()
    j = self.segmento.get_miny()

    #print "DimensionFractal.get_valor: minx: %s miny: %s maxx: %s maxy: %s"% (self.segmento.get_minx(), self.segmento.get_miny(), self.segmento.get_maxx(), self.segmento.get_maxy())
    for i in xrange(self.segmento.get_minx(), self.segmento.get_maxx(), self.size):
        for j in xrange(self.segmento.get_miny(), self.segmento.get_maxy(), self.size):
            #print "DimensionFractal.get_valor: ", (i, j)
            if self.tiene_borde(i, j):
                box_count += 1
            M += 1
        N += 1
    return self.calcular_dimension(box_count, M * N)

  def tiene_borde(self, i, j):
    for k in xrange(i, i + self.size):
        for l in xrange(j, j + self.size):
            if (k, l) in self.segmento.get_elementos_enteros_hash():
                return True
    return False

  def calcular_dimension(self, box_count, tot_count):
    return np.abs(np.log(box_count) / np.log(1 / tot_count))




class MedidaAreasPorRegiones(object):
  """
  Calculamos la suma de las areas de los segmentos que caen en las 9 regiones definidas.
  Para ver donde cae un segmento, usamos su centro de masa.
  """
  def __init__(self, segman, img_trans):
    """
    img_trans: es la imagen de destino. La que ya fue transformada/proyectada.
    segman: el SegmentosManager de la imagen
    """
    self.regiones = [0 for i in range(9)]
    self.centros = []
    ancho, alto = img_trans.size
    for segmento in segman.get_segmentos():
      for pixel in segmento.get_elementos_enteros():
        self.sumar_a_region(pixel, ancho, alto)

    superficie = (ancho*alto) / 9
    self.porcentajes = []
    for i in self.regiones:
      self.porcentajes.append(i/superficie)

  def sumar_a_region(self, pixel, ancho, alto):
    off_x = int(3 * pixel[0] / ancho)
    off_y = int(3 * pixel[1] / alto)
    self.regiones[3 * off_y + off_x] += 1

  def get_valor(self):
    return self.porcentajes
