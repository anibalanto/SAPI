
class Algoritmo(object):
  def aplicar_en_pixel(self, x, y, img):
    """
    Llamado por Transformador.aplicar.
    Debe devolver una tupla con los valores de r, g y b
    ej: return (34, 233, 10)
    """
    raise NotImplementedError

  def ancho(self, size):
    return (0,size[0])

  def alto(self, size):
    return (0, size[1])
