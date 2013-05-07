#!/usr/bin/env python
from __future__ import division
from imagen import ImagenArchivo
import matplotlib.pyplot as plt
import numpy as np
import colorsys
import sys
from collections import defaultdict

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def crear_histograma(img):
  ancho, alto = img.size

  valores_h = defaultdict(int)
  valores_s = defaultdict(int)
  valores_v = defaultdict(int)
  indices_h = set()
  indices_s = set()
  indices_v = set()
  total_pixels = 0

  histo = []

  for x in range(ancho):
    for y in range(alto):
      r, g, b = img.getpixel((x, y))
      if not (r == 0 and g == 0 and b == 0):
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        histo.append(h)
        #valores_h[int(h)] += 1
        #valores_h[s] += 1
        #valores_h[v] += 1
        #total_pixels += 1

  plt.hist(histo, bins=np.arange(0., 1., 0.001))
  plt.show()

if __name__ == '__main__':
  img = cargar(sys.argv[1])
  crear_histograma(img)


#Codigo viejo para mostrar el histograma
"""
indices = []
alturas = []
for i in valores_h.iteritems():
  indices.append(i[0])
  alturas.append(i[1] / total_pixels)


width = 0.001 #the width of the bars: can also be len(x) sequence
p1 = plt.bar(indices, alturas, width, color='r', align="center")
p2 = plt.bar(indices, alturas, width, color='b', align="center")
plt.ylabel('intensidad')
plt.xlabel('hue')
plt.show()
"""
