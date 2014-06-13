# -*- coding: utf-8 -*-

from imagen import ImagenVacia

class Transformador(object):

  @staticmethod
  def recorrer_imagen(ancho, alto):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    for x in range(1,ancho-1):
      for y in range(1,alto-1):
        yield (x,y)
    """
    for x in range(*ancho):
      for y in range(*alto):
        yield (x,y)

  @staticmethod
  def aplicar(algoritmos, img, show=True):
    """
    Aplica los algoritmos indicados en algoritmos a la imagen img.
    """
    ancho, alto = img.size
    for algoritmo in algoritmos:
      ret = ImagenVacia(img.size)
      for x,y in Transformador.recorrer_imagen(algoritmo.ancho(img.size), algoritmo.alto(img.size)):
          ret.putpixel(
              (x, y),
              algoritmo.aplicar_en_pixel(x, y, img)
          )
      show and ret.show()
      img = ret
    return ret
