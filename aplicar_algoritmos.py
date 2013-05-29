#!/usr/bin/env python
# -*- coding: utf-8 -*-

from colors import *
from bordes import *
from filtros import *
from ruido import *
from transformador import Transformador
from runcode import *
from histograma import crear_histograma_grayscale, crear_histograma_no_normalizado
from medidas import *
import csv


def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def mostrar_histo(imagen):
  crear_histograma_grayscale(imagen)

def generar_csv(img, filename):
  medidas = dict()
  vectores = GenMedidasImagen.generar(img)

  hsv = (vectores["h"], vectores["s"], vectores["v"])
  rgb = (vectores["r"], vectores["g"], vectores["b"])

  medidas["media_rgb"] = MediaRGB(rgb)
  medidas["media_hsv"] = MediaHSV(hsv)
  medidas["mediana_rgb"] = MedianaRGB(rgb)
  medidas["mediana_hsv"] = MedianaHSV(hsv)
  medidas["moda_rgb"] = ModaRGB(rgb)
  medidas["moda_hsv"] = ModaHSV(hsv)

  medidas["var_rgb"] = VarianzaRGB(rgb, medidas["media_rgb"].get_valor())
  medidas["var_hsv"] = VarianzaHSV(hsv, medidas["media_hsv"].get_valor())

  fields = medidas.keys()
  fields.sort()

  salida = dict((k,v.get_valor()) for k,v in medidas.iteritems())

  #dicc_segmentos = get_dicc_segmentos(img)

  f = open(filename, "w")
  cdw = csv.DictWriter(f, fields)
  cdw.writeheader()
  cdw.writerow(salida)
  f.close()

def get_dicc_segmentos(img):
  pass

def probar_perimetro(img):
  erosionada = Transformador.aplicar([AlgoritmoErosion(Filtro(UNOS, 3)),], img, True)
  diferencia = Transformador.aplicar([AlgoritmoResta(img)], erosionada, True)
  segman = run_codes(diferencia)
  for i in segman.segmentos:
    print AreaSegmento(i.elementos).get_valor()

def segmentar(img_original, mostrar_dif):
  """
  Los pasos de la segmentacion son los siguientes:
    1 - Se transforma la imagen a escala de grises a partir del componente v, de hsv.
    2 - Se crea el histograma de intensidades de gris de la imagen 1.
    3 - Se crea una imagen binaria utilizando el metodo de Otsu para encontrar el umbral. Para esto se
    usa el histograma de la etapa 2.
    4 - Se realiza un opening (erosion seguida de dilatacion) para eliminar los puntos pequeños que
    pueden haber quedado.
    5 - Se muestra la diferencia entre la imagen binaria de 3 y la imagen luego del opening. De esta
    forma se ve que se removio cuando se realizo el opening.
  """
  grayscale = Transformador.aplicar([AlgoritmoValueToGrayscale(), ], img_original, False)
  histograma = crear_histograma_no_normalizado(img_original)
  umbralada = Transformador.aplicar([AlgortimoUmbralAutomatico(histograma, grayscale.size[0], grayscale.size[1]),],
      grayscale, False)
  opening = Transformador.aplicar(
      [
        AlgoritmoErosion(Filtro(UNOS, 3)),
        AlgoritmoDilatacion(Filtro(UNOS, 3)),
      ],
      umbralada,
      True
  )
  diferencia = Transformador.aplicar([AlgoritmoResta(umbralada)], opening, False)
  if mostrar_dif:
    diferencia.show()

  return opening

def ver_segmentos(img_segmentada):
  """
  Muestra los diferentes segmentos de la imagen binaria pasada como parametro
  """
  segman = run_codes(img_segmentada)
  mostrar_segmentos(segman)

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s imagen_entrada" % sys.argv[0]
  else:
    original = cargar(sys.argv[1])
    #probar_perimetro(original)
    #generar_csv(original, "salida.csv")
    segmentada = segmentar(original, False)
    #ver_segmentos(segmentada)
