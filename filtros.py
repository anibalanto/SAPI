class Filtro(object):
  def __init__(self, matriz, ancho):
    self.matriz = matriz
    self.ancho = ancho
    self.current = 0
    self.offsets = [
        (-1,-1),(0,-1),(1,-1),
        (-1,0),(0,0),(1,0),
        (-1,1),(0,1),(1,1),
    ]

  def get_minimo(self):
    """
    el minimo valor posible que puede dar la funcion de convulsion para este filtro
    """
    ret = 0
    for i in self.matriz:
      val = 0
      if i < 0:
        val = i * 255
      ret += val
    return int(ret)

  def get_maximo(self):
    """
    el maximo valor posible que puede dar la funcion de convulsion para este filtro
    """
    ret = 0
    for i in self.matriz:
      val = 0
      if i > 0:
        val = i * 255
      ret += val
    return int(ret)

  def __iter__(self):
    self.current = 0
    return self

  def __repr__(self):
    return repr(self.matriz)

  def next(self):
    if self.current < (self.ancho * self.ancho):
      ret = self.offsets[self.current][0], self.offsets[self.current][1], self.matriz[self.current]
      self.current += 1
      return ret
    else:
      raise StopIteration()

UNOS = [1,1,1,1,1,1,1,1,1]
BORDE_H = [
    0,0,0,
    -1,1,0,
    0,0,0,
]

BORDE_V = [
    0,-1,0,
    0,1,0,
    0,0,0,
]

BORDE_DIAG_ASC = [
    0,-1,0,
    1,0,0,
    0,0,0,
]

BORDE_DIAG_DESC = [
    -1,0,0,
    0,1,0,
    0,0,0,
]

LINEAS_VERT = [
    -1,2,-1,
    -1,2,-1,
    -1,2,-1
]

LINEAS_HOR = [
    -1, -1, -1,
    2, 2, 2,
    -1, -1, -1,
]

#diagonal ascendente /
LINEAS_DIAG_ASC = [
    -1, -1, +2,
    -1, +2, -1,
    +2, -1, -1,
]

#diagonal descendente \
LINEAS_DIAG_DESC = [
    +2, -1, -1,
    -1, +2, -1,
    -1, -1, +2,
]

#Sobel
SOBEL = [
    -1, 0, +1,
    -2, 0, +2,
    -1, 0, +1,
]

#Sobel eje horizontal
SOBELX = [
    -1, -2, -1,
     0,  0,  0,
    +1, +2, +1,
]

#Sobel eje vertical
SOBELY = [
    -1,  0, +1,
    -2,  0, +2,
    -1,  0, +1,
]
