#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colors
import transformador
import runcode
import histograma
import medidas
from imagen import ImagenArchivo
from filtros import UNOS, Filtro
from colores import BLUE
import csv
import sys
#import numpy as np
#import ImageDraw


def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def mostrar_histo(imagen):
  histograma.crear_histograma_grayscale(imagen)

def cargar_medidas(rgb, hsv):
  """
  rgb: list. Lista con los valores rgb obtenidas de generar medidas.
  hsv: list. Lista con los valores hsv obtenidas de generar medidas.
  """
  meds = dict()

  meds["media_rgb"] = medidas.MediaRGB(rgb)
  meds["media_hsv"] = medidas.MediaHSV(hsv)
  meds["mediana_rgb"] = medidas.MedianaRGB(rgb)
  meds["mediana_hsv"] = medidas.MedianaHSV(hsv)
  meds["moda_rgb"] = medidas.ModaRGB(rgb)
  meds["moda_hsv"] = medidas.ModaHSV(hsv)

  meds["var_rgb"] = medidas.VarianzaRGB(rgb, meds["media_rgb"].get_valor())
  meds["var_hsv"] = medidas.VarianzaHSV(hsv, meds["media_hsv"].get_valor())

  return meds

def generar_csv(img_original, filename, gen_csv_imagen, gen_csv_segmentos, mostrar_proc):
  """
  mostrar_proc: bool. Si es true, se muestran los pasos del procesamiento.
  Genera las imagenes segmentadas y de perimetros para luego llamar a generar los csv
  de imagen y de segmentos.
  Por ultimo, guarda la imagen con los segmentos pintados.
  """
  img_segmentada = segmentar(img_original, mostrar_proc)
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  segman.eliminar_extremos_verticales()
  if gen_csv_imagen:
    generar_csv_imagen(img_original, segman, filename + ".medidas_imagen.csv")
  if gen_csv_segmentos:
    generar_csv_segmentos(img_original, segman, filename + ".medidas_segmento.csv")

  img_segmentos_pintados = runcode.pintar_segmentos(segman, (600,600))
  img_segmentos_pintados.save(filename + ".segmentos.bmp")

def generar_csv_imagen(img_original, segman, filename):
  """
  img_original: Imagen. Imagen rgb original.
  segman: SegmentoManager. SegmentoManager con los segmentos de la imagen segmentada.
  filename: string. Nombre del archivo donde guardar el csv.
  Genera un csv con las diferentes medidas de la imagen.
  """

  vectores = medidas.GenMedidasImagen().get_valor(img_original, medidas.no_azul)
  hsv = (vectores["h"], vectores["s"], vectores["v"])
  rgb = (vectores["r"], vectores["g"], vectores["b"])
  meds = cargar_medidas(rgb, hsv)

  fields = meds.keys()
  fields.sort()

  salida = dict((k,v.get_valor()) for k,v in meds.iteritems())

  fields.append("cant_segmentos")
  salida["cant_segmentos"] = segman.get_cant_segmentos()

  f = open(filename, "w")
  cdw = csv.DictWriter(f, fields)
  cdw.writeheader()
  cdw.writerow(salida)
  f.close()

def generar_csv_segmentos(img_original, segman, filename):
  """
  img_original: Imagen. Imagen original.
  segman: SegmentoManager. SegmentoManager con los segmentos de la imagen segmentada.
  filename: string. Nombre del archivo donde guardar el csv.
  Genera un csv con las diferentes medidas de los segmentos.
  """
  f = open(filename, "w")
  fields = ["area", "perimetro", "media_hsv","media_rgb", "mediana_hsv", "mediana_rgb", "moda_hsv","moda_rgb", "var_hsv", "var_rgb"]
  cdw = csv.DictWriter(f, fields)
  cdw.writeheader()

  for pos, segmento in enumerate(segman.get_segmentos()):

    vectores = medidas.GenMedidasSegmento().get_valor(img_original, segmento, medidas.no_azul)
    hsv = (vectores["h"], vectores["s"], vectores["v"])
    rgb = (vectores["r"], vectores["g"], vectores["b"])
    meds = cargar_medidas(rgb, hsv)

    cdw.writerow({fields[0]: "segmento #%s" % (pos,)})

    salida = dict((k,v.get_valor()) for k,v in meds.iteritems())
    salida["area"] = medidas.AreaSegmento(segmento).get_valor()
    salida["perimetro"] = medidas.PerimetroSegmento(segmento).get_valor()

    cdw.writerow(salida)

  f.close()

def probar_perimetro(img):
  erosionada = transformador.Transformador.aplicar([colors.AlgoritmoErosion(Filtro(UNOS, 3)),], img, True)
  diferencia = transformador.Transformador.aplicar([colors.AlgoritmoResta(img)], erosionada, True)
  segman = runcode.run_codes(diferencia)
  for i in segman.segmentos:
    print medidas.AreaSegmento(i.elementos).get_valor()

def diferencia(img, imgResta):
    return transformador.Transformador.aplicar([colors.AlgoritmoResta(img)], imgResta, True)

def borrar(img, imgResta):
    return transformador.Transformador.aplicar([colors.AlgoritmoBorrar(img)], imgResta, False)

def segmentar(img_original, mostrar_pasos):
  """
  img_original: Imagen. Imagen rgb a segmentar.
  mostrar_pasos: bool. Si es true. se muestran todos los pasos de la segmentacion.

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
  grayscale = transformador.Transformador.aplicar([colors.AlgoritmoValueToGrayscaleIgnoreBlue(), ], img_original, mostrar_pasos)
  histo = histograma.crear_histograma_no_normalizado(grayscale)
  umbralada = transformador.Transformador.aplicar([colors.AlgortimoUmbralAutomatico(histo, grayscale.size[0], grayscale.size[1]),],
      grayscale, mostrar_pasos)
  opening = transformador.Transformador.aplicar(
      [
        colors.AlgoritmoErosion(Filtro(UNOS, 3)),
        colors.AlgoritmoErosion(Filtro(UNOS, 3)),
        colors.AlgoritmoDilatacion(Filtro(UNOS, 3)),
        colors.AlgoritmoDilatacion(Filtro(UNOS, 3)),
      ],
      umbralada,
      mostrar_pasos
  )
  if mostrar_pasos:
    #mostramos la diferencia entre la umbralada y el opening
    transformador.Transformador.aplicar([colors.AlgoritmoResta(umbralada)], opening, mostrar_pasos)

  return opening

def ver_segmentos(img_segmentada, img_perimetros):
  """
  Muestra los diferentes segmentos de la imagen binaria pasada como parametro
  """
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  runcode.mostrar_segmentos(segman, img_segmentada.size)

"""
def probar_momentos(img_original):
  img_segmentada = segmentar(img_original, False)
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  segman.eliminar_extremos_verticales()
  centros = []
  momentos = []
  for i in segman.get_segmentos():
    area = medidas.AreaSegmento(i).get_valor()
    val = medidas.MomentosInvariantes(i, area).get_valor()
    centros.append((val["centro"], val["angulo"], i.maxx))
    momentos.append((val["centrales"], val["momentos"], val["normalizados"], area))
    #momentos.append((val["centrales"], area))

  for p, ang, maxx in centros:
    img_segmentada.putpixel(p,BLUE)
    img_segmentada.putpixel(p + (-1,-1),BLUE)
    img_segmentada.putpixel(p + (0,-1),BLUE)
    img_segmentada.putpixel(p + (1,-1),BLUE)

    img_segmentada.putpixel(p + (-1,1),BLUE)
    img_segmentada.putpixel(p + (0,1),BLUE)
    img_segmentada.putpixel(p + (1,1),BLUE)

    img_segmentada.putpixel(p + (0,1),BLUE)
    img_segmentada.putpixel(p + (0,-1),BLUE)

    dx = 40 * np.cos(ang)
    dy = 40 * np.sin(ang)

    dr = ImageDraw.Draw(img_segmentada.get_img())
    #dr.line([p[0],p[1],maxx,y], fill=BLUE)
    dr.line([p[0],p[1],p[0] + int(dx), p[1] - int(dy)], fill=BLUE)

  img_segmentada.show()

  print "los momentos son: "
  for h, k, i, j in sorted(momentos, key=lambda x: x[3]):
    print "centrales \n{}\n momentos \n{}\n normalizados \n{}\n{}\n".format(h,k,i,j)
"""
def probar_dimension_fractal(img_original):
  img_segmentada = segmentar(img_original, False)
  img_segmentada.show()
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  img_perimetros.show()
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  segman.eliminar_extremos()
  #segman.toImage().show()
  centros = []
  centrales = []
  dimensiones = []
  for i in segman.get_segmentos():
    area = medidas.AreaSegmento(i).get_valor()
    val = medidas.MomentosInvariantes(i, area).get_valor()
    d = medidas.DimensionFractal(i).get_valor()
    centros.append(val["centro"])
    img_segmentada.putpixel(val["centro"],BLUE)
    centrales.append(val["centrales"])
    dimensiones.append(d)
    print (dimensiones)
    print (centros)
  img_segmentada.show()

def probar_superficie_ocupada(img_original, img_sup_total):
  img_perimetros_sup_total = runcode.get_img_perimetros(img_sup_total)
  segman_sup_total = runcode.run_codes(img_sup_total, img_perimetros_sup_total)
  area_sup_total = medidas.AreaSegmento(segman_sup_total.get_segmentos()[0]).get_valor()

  img_segmentada = segmentar(img_original, False)
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  segman.eliminar_extremos()
  area_sum = 0
  total_manchas = 0
  for i in segman.get_segmentos():
    area = medidas.AreaSegmento(i).get_valor()
    area_sum = area_sum + area
    total_manchas = total_manchas + 1
    #val = medidas.MomentosInvariantes(i, area).get_valor()
    #d = medidas.DimensionFractal(i).get_valor()
    #centros.append(val["centro"])
    #img_segmentada.putpixel(val["centro"],BLUE)
    #centrales.append(val["centrales"])
    #dimensiones.append(d)
    #print (dimensiones)
    #print (centros)
  #img_segmentada.show()
  print (total_manchas)
  print (area_sum)
  factor_sup_ocup = float(area_sum) / float(area_sup_total)
  print (factor_sup_ocup)
  print (factor_sup_ocup * 2/3)
  area_cota = area_sup_total * factor_sup_ocup * 2/3
  print (area_cota)
  area_aux = 0
  cant_manchas = 0
  for i in segman.get_segmentos():
    area = medidas.AreaSegmento(i).get_valor()
    area_aux = area_aux + area
    cant_manchas = cant_manchas + 1
    if area_aux > area_cota:
        print (cant_manchas)
        print (area_aux)
        return
  superficie_ocupada = float(area_sum) / float(area_sup_total)

"""
def mostrar_segmentada(img):
  i = img.get_img()
  ancho, alto = img.size

  dr = ImageDraw.Draw(i)
  dr.line([(int(ancho/3),0), (int(ancho/3),alto)], fill=BLUE)
  dr.line([(int(2 * ancho/3),0), (int( 2 * ancho/3),alto)], fill=BLUE)

  dr.line([(0, int(alto/3)), (ancho, int(alto/3))], fill=BLUE)
  dr.line([(0, int(2*alto/3)), (ancho, int(2*alto/3))], fill=BLUE)

  i.show()
"""


def calcular_regiones(img_original):
  """
  Retornamos la imagen segmentada + el vector de regiones en una tupla (imagen, vector)
  """
  img_segmentada = segmentar(img_original, False)
  img_perimetros = runcode.get_img_perimetros(img_segmentada)
  segman = runcode.run_codes(img_segmentada, img_perimetros)
  regiones = medidas.MedidaAreasPorRegiones(segman, img_original).get_valor()
  superficie_ocupada = medidas.SuperficieOcupada(segman, img_original).get_valor()
  #mostrar_segmentada(img_segmentada)
  print "Las regiones son:"
  print regiones
  return img_segmentada, regiones, superficie_ocupada

def main():
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s imagen_entrada" % sys.argv[0]
  else:
    original = cargar(sys.argv[1])
    #probar_perimetro(original)
    #generar_csv(original, sys.argv[1], True, True, False)
    #probar_momentos(original)
    #probar_areas_regiones(original)
    #segmentada = segmentar(original, True)
    #ver_segmentos(segmentada, runcode.get_img_perimetros(segmentada))

if __name__ == "__main__":
  main()

