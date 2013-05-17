#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colors import *
from bordes import *
from filtros import *
from ruido import *
from transformador import Transformador

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s imagen_entrada" % sys.argv[0]
  else:
    img = cargar(sys.argv[1])
    lista_algos = [
        #AlgoritmoMedianaPromedio(img.size[0], img.size[1]),
        #AlgoritmoCompass([Filtro(i,3) for i in PREWITT_LIST]),
        AlgoritmoValueToGrayscale(),
        AlgoritmoGradiente(Filtro(SOBELX, 3), Filtro(SOBELY, 3))
    ]
    im = Transformador.aplicar(lista_algos, img)
