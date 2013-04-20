import Image
class MyException(Exception):
  def __init__(self, xy, pix_val):
    self.pix_val = pix_val
    self.xy = xy

  def __str__(self):
    return "Valor de pixel fuera de rango: %s en la pos %s" % (str(self.pix_val), str(self.xy),)

class Imagen(object):
  def __init__(self):
    self.img = None
    self.mode = None
    self.size = None
    self.pix = None

  def getpixel(self, xy):
    return self.pix[xy[0],xy[1]]

  def putpixel(self, xy, value):
    for i in value:
      if not 0 <= i <=255:
        raise MyException(xy, value)
    self.pix[xy[0],xy[1]] = value

  def show(self):
    self.img.show()

class ImagenArchivo(Imagen):

  def __init__(self, filename):
    Imagen.__init__(self)
    self._open(filename)

  def _open(self, filename):
    self.img = Image.open(filename)
    self.mode = self.img.mode
    self.size = self.img.size
    self.pix = self.img.load()

class ImagenVacia(Imagen):

  def __init__(self, mode, size):
    Imagen.__init__(self)
    self._new(mode, size)

  def _new(self, mode, size):
    self.img = Image.new(mode, size)
    self.mode = mode
    self.size = size
    self.pix = self.img.load()
