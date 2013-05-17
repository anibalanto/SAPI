import Image
import tempfile

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
    """
    xy: tupla (x, y)
    Retorna el color del pixel en xy. Ignora el canal alpha.
    Solo retornamos r, g y b. Si el modo de la imagen es RGBA, la matriz tiene
    tuplas del tipo (r, g, b, a)
    """
    return self.pix[xy[0],xy[1]][0:3]

  def get_red_pixel(self, xy):
    return self.pix[xy[0],xy[1]][0]

  def putpixel(self, xy, value):
    for i in value:
      if not 0 <= i <=255:
        raise MyException(xy, value)
    try:
      self.pix[xy[0],xy[1]] = value
    except:
      print "Fuera de rango? %s" % str(xy)
      raise

  def show(self):
    self.img.show()

  def save(self, path, *args, **kwargs):
    self.img.save(path, *args, **kwargs)

  def save_temp(self, mode="bmp"):
    filename = tempfile.mktemp()
    self.img.save(filename, mode)
    return filename

  def get_img(self):
    return self.img

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
