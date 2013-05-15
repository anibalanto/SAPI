from imagen import Imagen, ImagenArchivo, ImagenVacia

class Transformador(object):

  def recorrer_imagen(self, ancho, alto):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    """
    for x in range(1,ancho-1):
      for y in range(1,alto-1):
        yield (x,y)

  def aplicar(self, algoritmo, img):
    """
    Aplica el filtro a la imagen
    """
    ret = ImagenVacia(img.mode, img.size)
    ancho, alto = img.size
    for x,y in self.recorrer_imagen(ancho, alto):
        ret.putpixel(
            (x, y),
            algoritmo.aplicar_en_pixel(x, y, img)
        )
    return ret
