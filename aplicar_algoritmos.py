#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colors import *
from bordes import *
from filtros import *
from ruido import *
from transformador import Transformador
from runcode import mostrar_segmentos, run_codes
from histograma import crear_histograma_grayscale, crear_histograma_no_normalizado
from medidas import *


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
    """
    im = Transformador.aplicar([AlgoritmoValueToGrayscale(), ], original, False)

    histograma = crear_histograma_no_normalizado(im)

    umbralada = Transformador.aplicar([AlgortimoUmbralAutomatico(histograma, im.size[0], im.size[1]),], im, False)

    erosionada_dilatada = Transformador.aplicar(
        [ AlgoritmoErosion(Filtro(UNOS, 3)),
          AlgoritmoDilatacion(Filtro(UNOS, 3)), ],
        umbralada,
        False
    )

    diferencia = Transformador.aplicar([AlgoritmoResta(umbralada)], erosionada_dilatada, False)

    segmentos = run_codes(erosionada_dilatada)
    mostrar_segmentos(segmentos, erosionada_dilatada.size)

    """
    prom_hsv, prom_rgb = PromedioHSV(), PromedioRGB()
    mediana_rgb, mediana_hsv = MedianaRGB(), MedianaHSV()
    GenMedidasImagen.generar([prom_hsv, prom_rgb, mediana_hsv, mediana_rgb], original)
    print prom_hsv.get_valor()
    print prom_rgb.get_valor()
    print mediana_hsv.get_valor()
    print mediana_rgb.get_valor()
