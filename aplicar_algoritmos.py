#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colors import *
from bordes import *
from filtros import *
from ruido import *
from transformador import Transformador
from histograma import crear_histograma_grayscale, crear_histograma_no_normalizado


def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def mostrar_histo(imagen):
  crear_histograma_grayscale(imagen)

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s imagen_entrada" % sys.argv[0]
  else:
    original = cargar(sys.argv[1])
    im = Transformador.aplicar([AlgoritmoValueToGrayscale(), ], original)
    histograma = crear_histograma_no_normalizado(im)
    umbralada = Transformador.aplicar(
        [
          AlgortimoUmbralAutomatico(histograma, im.size[0], im.size[1]),
        ],
        im
    )
    erosionada_dilatada = Transformador.aplicar(
        [
          AlgoritmoErosion(Filtro(UNOS, 3)),
          AlgoritmoDilatacion(Filtro(UNOS, 3)),
        ],
        umbralada
    )
    final = Transformador.aplicar([AlgoritmoResta(umbralada)], erosionada_dilatada)
    """
    #umbralada.save("mascara.bmp")
    final = Transformador.aplicar(
        [AlgoritmoAplicarMascara(original, umbralada)],
        ImagenVacia("RGBA", original.size)
    )
    """
