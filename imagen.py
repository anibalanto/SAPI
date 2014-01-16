# -*- coding: utf-8 -*-
import Image
import tempfile
from PySide.QtGui import QImage, qRgb, qRed, qGreen, qBlue
import cv2

class MyException(Exception):
  def __init__(self, xy, pix_val):
    self.pix_val = pix_val
    self.xy = xy

  def __str__(self):
    return "Valor de pixel fuera de rango: %s en la pos %s" % (str(self.pix_val), str(self.xy),)

class BaseImagen(object):
  def __init__(self):
    self.img = None

  def getpixel(self, xy):
    """
    Retorna el pixel en la posicion x,y. El pixel es una tupla (R,G,B).
    """
    raise NotImplementedError

  def putpixel(self, xy, valor):
    """
    xy: tupla (x,y)
    valor: tupla (r,g,b)
    Setea el pixel en la posicion x,y con el valor.
    """
    raise NotImplementedError

  def show(self):
    """
    Muestra la imagen.
    """
    raise NotImplementedError

  def save(self, path, *args, **kwargs):
    """
    path: string
    Guarda la imagen en el archivo determinado por path.
    """
    raise NotImplementedError

  def save_temp(self):
    """
    Guarda la imagen en un archivo temporal y retorna el nombre del archivo temporal.

    """
    raise NotImplementedError

  def fromfile(self, filename):
    """
    filename: string con el nombre del archivo
    Crea una imagen a partir de un archivo.
    """
    raise NotImplementedError

  def empty(self, mode, size):
    """
    size: tupla (ancho, alto)
    Crea una imagen vacia con el tamaño indicado.
    """
    raise NotImplementedError

class ImagenQImage(BaseImagen):
  def __init__(self):
    super(ImagenQImage, self).__init__()
    self.mode = "No implementado"

  @property
  def size(self):
    return (self.img.width(), self.img.height())

  def fromfile(self, filename):
    self.img = QImage(filename)

  def empty(self, size, mode=QImage.Format_RGB888):
    self.img = QImage(size[0], size[1], mode)

  def getpixel(self, xy):
    color = self.img.pixel(xy[0], xy[1])
    return (qRed(color), qGreen(color), qBlue(color))

  def putpixel(self, xy, value):
    self.img.setPixel(xy[0], xy[1], qRgb(value[0], value[1], value[2]))

  def get_img(self):
    return self.img

  def save(self, filename):
    self.img.save(filename, format="BMP", quality=100)

  def from_opencv(self, img_opencv):
    dst = cv2.cvtColor(img_opencv, cv2.COLOR_BGR2RGB)
    qim = QImage(dst.data, dst.shape[1], dst.shape[0], dst.strides[0], QImage.Format_RGB888)
    self.img = qim.copy()

class ImagenPIL(BaseImagen):
  def __init__(self):
    super(ImagenPIL, self).__init__()
    self.mode = None
    self.pix = None

  def getpixel(self, xy):
    """
    xy: tupla (x, y)
    Retorna el color del pixel en xy. Ignora el canal alpha.
    Solo retornamos r, g y b. Si el modo de la imagen es RGBA, la matriz tiene
    tuplas del tipo (r, g, b, a)
    """
    return self.pix[xy[0],xy[1]][0:3]

  def putpixel(self, xy, value):
    #print ("x,y = %s value = %s"% (xy, value))
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

  def fromfile(self, filename):
    self.img = Image.open(filename)
    self.mode = self.img.mode
    self.size = self.img.size
    self.pix = self.img.load()

  def empty(self, size, mode="RGB"):
    self.img = Image.new(mode, size)
    self.mode = mode
    self.size = size
    self.pix = self.img.load()

  def tostring(self, arg1, arg2):
      return self.img.convert("RGBA").tostring(arg1, arg2)

def ImagenArchivo(filename):
  ret = ImagenQImage()#_cls()
  #ret = ImagenPIL()
  ret.fromfile(filename)
  return ret

def ImagenVacia(size):
  ret = ImagenQImage()#_cls()
  #ret = ImagenPIL()
  ret.empty(size)
  return ret

def ImagenOpenCV(img_opencv):
  ret = ImagenQImage()
  ret.from_opencv(img_opencv)
  return ret

if __name__ == "__main__":
  #im = ImagenVacia(ImagenQImage, (720, 720))
  im = ImagenVacia((720, 720))
  s = set()
  ty = "tiff"
  for i in range(300,500):
    for j in range(600,700):
      im.putpixel((i,j), (255,0,0))

  im.save("salidaqimage." + ty)

  im = ImagenArchivo("salidaqimage." + ty)
  for i in range(300,500):
    for j in range(600,700):
      s.add(im.getpixel((i,j)))

  print s

