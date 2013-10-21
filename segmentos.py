# -*- coding: utf-8 -*-
from imagen import ImagenPIL

class Segmento(object):
  def __init__(self):
    #lista de tuplas (x,y)
    self.elementos_enteros = []
    self.elementos_enteros_hash = {}
    #lista de tuplas (x,y)
    self.elementos_perimetro = []
    self.cant = 0
    self.maxx = -9999
    self.maxy = -9999
    self.minx = 99999
    self.miny = 99999

  def get_elementos_enteros(self):
    return self.elementos_enteros

  def get_elementos_enteros_hash(self):
    return self.elementos_enteros_hash

  def get_elementos_perimetro(self):
    return self.elementos_perimetro

  def add_elemento_perimetro(self, x, y):
    self.elementos_perimetro.append((x, y))

  def add_elemento_entero(self, x, y):
    self.elementos_enteros.append((x, y))
    self.elementos_enteros_hash[(x,y)] = self.cant
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

  def get_minx(self):
      return self.minx

  def get_maxx(self):
      return self.maxx

  def get_miny(self):
      return self.miny

  def get_maxy(self):
      return self.maxy


class SegmentoManager(object):
  def __init__(self, ancho, alto):
    """
    ancho: int
    alto: int
    Almacena los segmentos desde 0,0 hasta ancho,alto.
    """
    self.ancho = ancho
    self.alto = alto
    self.mat = [[None for i in range(alto)] for j in range(ancho)]
    self.segmentos = []

  def get_segmentos(self):
    return self.segmentos

  def get_cant_segmentos(self):
    return len(self.segmentos)

  def eliminar_extremos_verticales(self):
    """
    Elimina los segmentos que "tocan" el borde superior o inferior.
    Se eliminan aquellos segmentos que tengan un pixel en (x, 1)
    o en (x, alto - 2) para cualquier x.
    """
    a_borrar = []
    borde_superior = 1
    borde_inferior = self.alto - 2
    for j in self.segmentos:
      if j.miny == borde_superior or j.maxy == borde_inferior:
        a_borrar.append(j)

    for i in a_borrar:
      self.segmentos.remove(i)

  def eliminar_extremos(self):
    """
    Elimina los segmentos que "tocan" los bordes.
    """
    a_borrar = []
    borde_izquierdo = 1
    borde_derecho = self.ancho - 2
    borde_superior = 1
    borde_inferior = self.alto - 2
    for j in self.segmentos:
      if j.minx == borde_izquierdo or j.maxx == borde_derecho or j.miny == borde_superior or j.maxy == borde_inferior:
        a_borrar.append(j)

    for i in a_borrar:
      self.segmentos.remove(i)

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

  def toImage(self):
    imagen = ImagenPIL()
    for segmento in self.get_segmentos():
      for xy in segmento.get_elementos_enteros():
        imagen.putpixel(xy, (255, 255, 255))
    return imagen

  def add_pixel_perimetro(self, x, y):
    self.mat[x][y].add_elemento_perimetro(x, y)
