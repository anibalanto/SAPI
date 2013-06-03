#! /usr/bin/env python
from __future__ import division
from imagen import ImagenArchivo, ImagenVacia
from collections import namedtuple
import sys
import numpy as np

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

Point = namedtuple('Point', ["x", "y"])

class Transformador(object):

  def recorrer_imagen(self, ancho, alto):
    for x in range(600):
      for y in range(600):
          yield (x,y)

  def es_borde(self, x, y, ancho, alto):
    return not ((0 < x < ancho-1) and (0 < y < alto-1))

  def aplicar(self, algoritmo, img_origen, img_destino):
    """
    Aplica el filtro a la imagen
    desde y hasta instancias de Point definen el cuadrado sobre el cual se va a aplicar el algoritmo
    """
    ancho, alto = img_origen.size
    for x,y in self.recorrer_imagen(ancho, alto):
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

    """
     * c00*xi + c01*yi + c02
    * ui = ---------------------
    * c20*xi + c21*yi + c22
    *
    * c10*xi + c11*yi + c12
    * vi = ---------------------
    * c20*xi + c21*yi + c22
    *
    * Coefficients are calculated by solving linear system:
    * / x0 y0 1 0 0 0 -x0*u0 -y0*u0 \ /c00\ /u0\
    * | x1 y1 1 0 0 0 -x1*u1 -y1*u1 | |c01| |u1|
    * | x2 y2 1 0 0 0 -x2*u2 -y2*u2 | |c02| |u2|
    * | x3 y3 1 0 0 0 -x3*u3 -y3*u3 |.|c10|=|u3|,
    * | 0 0 0 x0 y0 1 -x0*v0 -y0*v0 | |c11| |v0|
    * | 0 0 0 x1 y1 1 -x1*v1 -y1*v1 | |c12| |v1|
    * | 0 0 0 x2 y2 1 -x2*v2 -y2*v2 | |c20| |v2|
    * \ 0 0 0 x3 y3 1 -x3*v3 -y3*v3 / \c21/ \v3/
    """

    a = np.array([
      [xA, yA, 1, 0, 0, 0, -xA*xDestA, -yA*xDestA],
      [xB, yB, 1, 0, 0, 0, -xB*xDestB, -yB*xDestB],
      [xC, yC, 1, 0, 0, 0, -xC*xDestC, -yC*xDestC],
      [xD, yD, 1, 0, 0, 0, -xD*xDestD, -yD*xDestD],
      [0, 0, 0, xA, yA, 1, -xA*yDestA, -yA*yDestA],
      [0, 0, 0, xB, yB, 1, -xB*yDestB, -yB*yDestB],
      [0, 0, 0, xC, yC, 1, -xC*yDestC, -yC*yDestC],
      [0, 0, 0, xD, yD, 1, -xD*yDestD, -yD*yDestD],
    ])

    b = [xDestA, xDestB, xDestC, xDestD, yDestA, yDestB, yDestC, yDestD,]
    #solve nos da x de la ecuacion a.x = b
    x = np.linalg.solve(a,b)

    self.C1, self.C2, self.C3, self.C4, self.C5, self.C6, self.C7, self.C8 = x

    mat = np.array([
      [self.C1, self.C2, self.C3],
      [self.C4, self.C5, self.C6],
      [self.C7, self.C8, 1],
    ])

    self.inversa = np.linalg.inv(mat)

  def aplicar_en_pixel(self, x, y, origen, destino):
    x_dest = (self.inversa[0,0] * x + self.inversa[0,1] * y + self.inversa[0,2])/(self.inversa[2,0] * x + self.inversa[2,1] * y + self.inversa[2,2])
    y_dest = (self.inversa[1,0] * x + self.inversa[1,1] * y + self.inversa[1,2])/(self.inversa[2,0] * x + self.inversa[2,1] * y + self.inversa[2,2])
    destino.putpixel((x, y), origen.getpixel((int(x_dest), int(y_dest))))
    """
    try:
      destino.putpixel((int(x), int(y)), origen.getpixel((int(x_dest), int(y_dest))))
    except:
      pass
    """

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
  trans.aplicar(algo, origen, destino)

  destino.show()
