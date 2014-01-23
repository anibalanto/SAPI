#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, LargeBinary, PickleType, ForeignKey
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import numpy as np

from PySide import QtCore, QtGui

DBPATH = "sqlite:///database.db"
Base = declarative_base()

class ManagerBase(object):
  def __init__(self):
    self.engine = create_engine(DBPATH)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()
    Base.metadata.create_all(self.engine)#Las tablas que ya existen no se tocan

  def crear_individuo(self, img_original, img_transformada, img_segmentada, vector_regiones, dicc_datos):
    """ Las imagenes son del tipo QImage """
    nuevo_individuo = Individuo(dicc_datos["nombre"])
    #TODO: pasar otros parametros del dicc
    captura = Captura(
        self.imagen_a_bytes(img_original),
        self.imagen_a_bytes(img_transformada),
        self.imagen_a_bytes(img_segmentada),
        vector_regiones
        )
    nuevo_individuo.capturas.append(captura)
    self.session.add(nuevo_individuo)
    self.session.commit()

  def crear_captura(self, id_individuo, img_original, img_transformada, img_segmentadas, vector_regiones, dicc_datos):
    #TODO: dicc_datos no se usa para nada todavia
    nueva_captura = Captura(
          self.imagen_a_bytes(img_original),
          self.imagen_a_bytes(img_transformada),
          self.imagen_a_bytes(img_segmentadas),
          vector_regiones
          )
    individuo = self.get_individuo(id_individuo)
    individuo.capturas.append(nueva_captura)
    self.session.commit()

  def get_individuo(self, individuo_id):
    """
    Retorna un Individuo o None
    """
    return self.session.query(Individuo).get(individuo_id)

  def get_datos_individuo(self, individuo_id):
    """
    Este metodo nos devuelve los datos de un individuo, listos para ser usados por algun
    widget de listado. El widget no necesita conocer Individuo.
    """
    ind = self.get_individuo(individuo_id)
    capturas = ind.capturas
    if not ind is None:
      return {
          "imagenes_transformadas": [self.bytes_a_imagen(x.imagen_transformada) for x in capturas],
          "nombre": ind.nombre
          }
    else:
      None

  def bytes_a_imagen(self, datos_imagen):
    """ Crea un QImage a partir de un LargeBinary/QByteArray """
    ba = QtCore.QByteArray(datos_imagen)
    image = QtGui.QImage.fromData(ba)
    return image

  def imagen_a_bytes(self, imagen):
    """Crea un QByteArray desde un QImage"""
    ba = QtCore.QByteArray()
    buff = QtCore.QBuffer(ba)
    buff.open(QtCore.QIODevice.WriteOnly)
    #TODO: Ojo con JPG!!
    imagen.save(buff, "JPG")
    return ba

  def calc_distancia(self, v1, v2):
    #TODO: que no haga falta pasar a array
    return np.linalg.norm(np.array(v1)-np.array(v2))

  def similares(self, vector_origen):
    """
    Retorna los individuos asociados a las 5 capturas mas cercanas a vector_origen
    estructura de retorno: {id: {dicc_datos: datos del individuo, capturas: lista de QImage de las capturas}}
    """
    mejores = []
    for cap in self.session.query(Captura).all():
      mejores.append((self.calc_distancia(cap.area_por_region, vector_origen), cap))
    mejores.sort(key=lambda a: a[0])
    ret = {}
    for i in mejores:
      if not ret.has_key(i[1].individuo.id):
        ret[i[1].individuo.id] = {
            "imagen" : self.bytes_a_imagen(i[1].imagen_transformada),
            #todas las capturas del individuo asociado a la captura
            "lista_imagenes" : [self.bytes_a_imagen(j.imagen_transformada) for j in i[1].individuo.capturas],
            "dicc_datos" : {"nombre" : i[1].individuo.nombre},
            }
    return ret

  def all_individuos(self):
    """
    Retorna todos los individuos.
    Estructura de retorno:
    {id:
      {
        dicc_datos: datos del individuo,
        imagen: imagen a mostrar tipo thumbnail,
        lista_imagenes: lista de QImage de las capturas
      }
    }
    """
    ret = {}
    for individuo in self.session.query(Individuo).all():
      ret[individuo.id] = {
          "imagen" : self.bytes_a_imagen(individuo.capturas[0].imagen_transformada),
          #todas las capturas del individuo asociado a la captura
          "lista_imagenes" : [self.bytes_a_imagen(j.imagen_transformada) for j in individuo.capturas],
          "dicc_datos" : {"nombre" : individuo.nombre},
          }
    return ret

class Captura(Base):
  __tablename__ = 'captura'

  id = Column(Integer, primary_key=True)
  individuo_id = Column(Integer, ForeignKey('individuo.id'))
  imagen_original = deferred(Column(LargeBinary))
  imagen_transformada = deferred(Column(LargeBinary))
  imagen_segmentada = deferred(Column(LargeBinary))
  area_por_region = Column(PickleType)#lista con la cantidad de area por region
  #TODO: agregar otros atributos
  #ubicacion
  #hora de captura

  def __init__(self, img_original, img_trans, img_segmentada, area_por_region):
    self.imagen_original = img_original
    self.imagen_transformada = img_trans
    self.imagen_segmentada = img_segmentada
    self.area_por_region = area_por_region

  def __repr__(self):
    return "<Captura('%s')>" % (self.id)

class Individuo(Base):
  __tablename__ = 'individuo'

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100))
  capturas = relationship("Captura", backref="individuo")

  def __init__(self, nombre):
    self.nombre = nombre

  def __repr__(self):
    return "<Individuo('%s')>" % (self.nombre)
