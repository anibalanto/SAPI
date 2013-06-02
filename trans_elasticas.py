#! /usr/bin/env python
from __future__ import division
from imagen import ImagenArchivo, ImagenVacia
import ImageDraw
from collections import namedtuple
import sys

from PySide.QtCore import Qt
from PySide.QtCore import QPoint
from PySide.QtGui import QPolygon

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

Point = namedtuple('Point', ["x", "y"])

class Transformador(object):

  def inbounds(self, x, y, o1, o2, o3, o4):
    poly = QPolygon()
    poly << QPoint(o1.x, o1.y)
    poly << QPoint(o2.x, o2.y)
    poly << QPoint(o3.x, o3.y)
    poly << QPoint(o4.x, o4.y)
    return poly.containsPoint(QPoint(x,y), Qt.FillRule.WindingFill)

  def recorrer_imagen(self, ancho, alto, o1, o2, o3, o4):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    desde y hasta son instancias de Point
    """
    for x in range(ancho):
      for y in range(alto):
        if self.inbounds(x,y,o1,o2,o3,o4):
          yield (x,y)

  def es_borde(self, x, y, ancho, alto):
    return not ((0 < x < ancho-1) and (0 < y < alto-1))

  def aplicar(self, algoritmo, o1, o2, o3, o4, img_origen, img_destino):
    """
    Aplica el filtro a la imagen
    desde y hasta instancias de Point definen el cuadrado sobre el cual se va a aplicar el algoritmo
    """
    ancho, alto = img_origen.size
    for x,y in self.recorrer_imagen(ancho, alto, o1, o2, o3, o4):
      algoritmo.aplicar_en_pixel(x, y, img_origen, img_destino)

class Algoritmo(object):
  def aplicar_en_pixel(self, x, y, img, ret):
    raise NotImplementedError

class TransElastica(Algoritmo):
  def __init__(self, o1, o2, o3, o4, d1, d2, d3, d4):
    xA, yA = o1
    xB, yB = o2
    xC, yC = o3
    xD, yD = o4

    xDestA, yDestA = d1
    xDestB, yDestB = d2
    xDestC, yDestC = d3
    xDestD, yDestD = d4

    w1 = ((yA - yB)*(xA - xC) / (xA - xB)) - (yA - yC)
    w2 = ( ((xA*yA - xB*yB)*(xA - xD) ) / (xA - xB) ) - (xA*yA - xD*yD)
    w3 = xDestC - xDestA + ((xDestA - xDestB)*(xA - xC) / (xA - xB))
    w4 = xDestA - ((xDestA - xDestB)*(xA - xD) / (xA - xB))
    w5 = ((xA*yA - xB*yB)*(xA - xC) / (xA - xB)) - (xA*yA - xC*yC)
    w6 = ((yA - yB)*(xA - xD) / (xA - xB)) - (yA - yD)
    w7 = yDestC - yDestA + ((yDestA - yDestB)*(xA - xC) / (xA - xB))
    w8 = yDestA - ((yDestA - yDestB) * (xA - xD) / (xA - xB))

    self.C4 = (xDestD - w4 - (w6 * w3 / w1)) / (w2 - ((w5 * w6) / w1))
    self.C3 = (xDestC - xDestA + ((xDestA - xDestB)*(xA - xC) / (xA - xB)) - self.C4*w5) / w1
    self.C2 = (xDestA - xDestB - self.C3*(yA - yB) - self.C4*(xA*yA - xB*yB)) / (xA - xB)
    self.C1 = xDestA - self.C2 * xA - self.C3 * yA - self.C4 * xA * yA
    self.C8 = (yDestD - w8 - (w6*w7/w1)) / ( w2 - ((w5*w6) / w1))
    self.C7 = (yDestC - yDestA + ((yDestA - yDestB)*(xA - xC) / (xA - xB)) - self.C8*w5) / w1
    self.C6 = (yDestA - yDestB - self.C7*(yA - yB) - self.C8*(xA*yA - xB*yB)) / (xA - xB)
    self.C5 = yDestA - self.C6 * xA - self.C7 * yA - self.C8 * xA * yA

  def aplicar_en_pixel(self, x, y, origen, destino):
    x_dest = self.C1 + self.C2 * x + self.C3 * y + self.C4 * x * y
    y_dest = self.C5 + self.C6 * x + self.C7 * y + self.C8 * x * y
    try:
      destino.putpixel((int(x_dest), int(y_dest)), origen.getpixel((x, y)))
    except:
      pass
      #print int(x_dest), int(y_dest)


if __name__ == "__main__":
  """
  imagen origen
  o1 ----o2
  |        |
  |        |
  |        |
  o4-------- o3

  imagen destino
  d1 ----- d2
  |        |
  |        |
  |        |
  d4 ----- d3
  """
  origen = cargar(sys.argv[1])
  ancho, alto = origen.size
  destino = ImagenVacia("RGB", (600, 600))
  #draw = ImageDraw.Draw(destino.get_img())

  o1 = Point(268,330)
  o2 = Point(609,0)
  o3 = Point(697,511)
  o4 = Point(382,607)

  d1 = Point(0,0)
  d2 = Point(600, 0)
  d3 = Point(600, 600)
  d4 = Point(0, 600)

  algo = TransElastica(o1, o2, o3, o4, d1, d2, d3, d4)

  trans = Transformador()
  trans.aplicar(algo, o1, o2, o3, o4, origen, destino)
  #draw.polygon([d1, d2, d3, d4], outline=(0,0,255))

  destino.show()
