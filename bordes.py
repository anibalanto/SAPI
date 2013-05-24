#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implementacion de deteccion de bordes
"""

from __future__ import division
import sys
import math
from filtros import  *
from imagen import ImagenArchivo, ImagenVacia
from colores import *
from transformador import Transformador
from algoritmo import Algoritmo

class AlgoritmoRuido(Algoritmo):

  def __init__(self, filtro):
    self.filtro = filtro

  def aplicar_en_pixel(self, x, y, img):
    """
    Aplica el filtro en el pixel dado por img(x,y)
    devuelve la imagen ret con el pixel x,y modificado
    total = filtro.ancho * filtro.ancho
    """
    sumar = 0.0
    sumag = 0.0
    sumab = 0.0
    for columna, fila, valor in self.filtro:
      r, g, b = img.getpixel((x+columna, y+fila))
      sumar += valor * r
      sumag += valor * g
      sumab += valor * b
    return (int(sumar/total), int(sumag/total),int(sumab/total))

class AlgoritmoConvulsion(Algoritmo):
  def __init__(self, filtro):
    self.filtro = filtro

  def aplicar_en_pixel(self, x, y, img):
    """
    Devuelve la imagen ret con el pixel x,y modificado. Usa el filtro con la imagen de origen img.
    ret(x,y) = f(filtro, img)
    minimo: el minimo valor posible de la convulsion
    maximo: el maximo valor posible de la convulsion
    Tenemos que dividir por maximo * minimo y luego multiplicar por 255
    """
    minimo = abs(self.filtro.get_minimo())
    maximo = abs(self.filtro.get_maximo())
    total = minimo + maximo
    sumar = 0.0
    sumag = 0.0
    sumab = 0.0
    for columna, fila, valor in self.filtro:
      if valor == 0: continue
      r, g, b = img.getpixel((x+columna, y+fila))
      sumar += valor * r
      sumag += valor * g
      sumab += valor * b
    value = (
        int(((sumar + minimo) / total) * 255),
        int(((sumag + minimo) / total) * 256),
        int(((sumab + minimo) / total) * 255),
    )
    return value

class AlgoritmoRoberts(Algoritmo):
  """
  operador de resaltado de bordes de Roberts
  ver tp3 ejercicio 1
  usamos solo el canal R. Asumimos que la img esta en escala de grises.
  """
  def aplicar_en_pixel(self, x, y, img):

    #maximo es sqrt(255**2 + 255 ** 2)
    maximo = 360.62445840513925
    a = math.pow(img.getpixel((x,y))[0] - img.getpixel((x+1,y+1))[0], 2)
    b = math.pow(img.getpixel((x,y+1))[0] - img.getpixel((x+1,y))[0], 2)
    c = math.sqrt(a + b) / maximo
    value = int(c * 255)
    return (value, value, value)

class AlgoritmoCompass(Algoritmo):
  """
  Este algoritmo admite una serie de filtros que luego aplica.
  Se utiliza con los filtros de prewitt.
  """

  def __init__(self, filtros_list):
    """
    filtros_list: lista de filtros a aplicar
    """
    self.filtros_list = filtros_list
    maximo = 0
    for filtro in self.filtros_list:
      maximo += filtro.get_maximo()
    self.intervalo = maximo
    self.maxborde = 0

  def aplicar_en_pixel(self, x, y, img):
    """
    Aplica cada uno de los filtros.
    De todos los gradientes, nos quedamos con el maximo normalizado.
    """
    gradientes = list()

    for filtro in self.filtros_list:
      gr = 0
      for col, fil, val in filtro:
        gr += img.get_red_pixel((x+col, y+fil)) * val
      gradientes.append(abs(gr) / filtro.get_maximo())

    value = int(max(gradientes) * 255)
    if value > self.maxborde: self.maxborde = value
    #ret.putpixel((x,y), (value,value,value))
    #ret.putpixel((x,y), color)
    return (value,value,value)

class AlgoritmoGradiente(Algoritmo):
  """
  Este algoritmo es apto para utilizarlo con 2 filtros.
  Se puede probar con los filtros de sobel.
  """

  def __init__(self, filtrox, filtroy):
    self.filtrox = filtrox
    self.filtroy = filtroy

  def aplicar_en_pixel(self, x, y, img):
    gx = 0.0
    gy = 0.0
    maximo = math.sqrt(2 * math.pow(4 * 255, 2))
    maximoy = self.filtroy.get_maximo()

    for col, fil, val in self.filtrox:
      gx += img.getpixel((x+col, y+fil))[0] * val

    for col, fil, val in self.filtroy:
      gy += img.getpixel((x+col, y+fil))[0] * val

    value = math.sqrt(math.pow(gx, 2) + math.pow(gy, 2))
    value = int((value / maximo) * 255)
    return (value,value,value)

if __name__ == "__main__":
  pass
