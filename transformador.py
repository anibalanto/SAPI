# -*- coding: utf-8 -*-

from imagen import ImagenVacia

class Transformador(object):

  @staticmethod
  def recorrer_imagen(ancho, alto):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    """
    for x in range(1,ancho-1):
      for y in range(1,alto-1):
        yield (x,y)

  @staticmethod
  def aplicar(algoritmos, img):
    """
    Aplica los algoritmos indicados en algoritmos a la imagen img.
    """
    ancho, alto = img.size
    for algoritmo in algoritmos:
      ret = ImagenVacia(img.mode, img.size)
      for x,y in Transformador.recorrer_imagen(ancho, alto):
          ret.putpixel(
              (x, y),
              algoritmo.aplicar_en_pixel(x, y, img)
          )
      ret.show()
      img = ret
      #ret = ImagenVacia(img.mode, img.size)
      #img.show()
    return ret
