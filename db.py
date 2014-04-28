#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, LargeBinary, PickleType, ForeignKey, DateTime, Float, Text
from sqlalchemy import func
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import numpy as np

from PySide import QtCore, QtGui

#DBPATH = "sqlite:///database.db"
DBPATH = "postgresql+psycopg2://postgres:postgres@localhost:5432/sapitosierra"

Base = declarative_base()

class ManagerBase(object):
  def __init__(self):
    self.engine = create_engine(DBPATH)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()
    Base.metadata.create_all(self.engine)#Las tablas que ya existen no se tocan


  #TODO: refactorizar la forma de crear individuos
  def crear_individuo_ret_id(self, sexo, observaciones_individuo):
    """
    Creamos un nuevo Individuo y retorna el id del mismo
    """
    nuevo_individuo = Individuo(sexo, observaciones_individuo)
    self.session.add(nuevo_individuo)
    self.session.commit()
    return nuevo_individuo.id

  #TODO: refactorizar la forma de crear individuos
  def crear_individuo(self, img_original, img_transformada, img_segmentada, vector_regiones, \
      sexo, observaciones_individuo,\
      fecha, lat, lon, acompaniantes, observaciones_captura, nombre_imagen, puntos, angulos, largos,\
      nombre, apellido, email):
    """
    Creamos un nuevo Individuo y una Captura asociada a este, a partir de las imagenes que recibimos como
    parametros.
    Las imagenes son del tipo QImage.
    """
    nuevo_individuo = Individuo(sexo, observaciones_individuo)
    captura = self.crear_captura(
        nuevo_individuo,
        img_original,
        img_transformada,
        img_segmentada,
        vector_regiones,
        fecha,
        lat,
        lon,
        acompaniantes,
        observaciones_captura,
        nombre_imagen,
        puntos,
        angulos,
        largos,
        nombre,
        apellido,
        email
        )
    nuevo_individuo.capturas.append(captura)
    self.session.add(nuevo_individuo)
    self.session.commit()

  def crear_captura(self, individuo_id, img_original, img_transformada, img_segmentadas, vector_regiones,\
      fecha, lat, lon, acompaniantes, observaciones_captura, nombre_imagen, puntos, angulos, largos,\
      fotografo_id, zona_id):
    #TODO: dicc_datos no se usa para nada todavia
    nueva_captura = Captura(
          self.imagen_a_bytes(img_original),
          self.imagen_a_bytes(img_transformada),
          self.imagen_a_bytes(img_segmentadas),
          vector_regiones,
          fecha,
          lat,
          lon,
          acompaniantes,
          observaciones_captura,
          nombre_imagen,
          puntos,
          angulos,
          largos
          )
    fotografo = self.session.query(Fotografo).get(fotografo_id)
    individuo = self.session.query(Individuo).get(individuo_id)
    zona = self.session.query(Zona).get(zona_id)
    fotografo.capturas.append(nueva_captura)
    individuo.capturas.append(nueva_captura)
    zona.capturas.append(nueva_captura)
    self.session.add(nueva_captura)
    self.session.commit()
    return nueva_captura

  def get_individuo(self, individuo_id):
    """
    Retorna un Individuo o None
    """
    return self.session.query(Individuo).get(individuo_id)

  def get_fotografo(self, fotografo_id):
    """
    Retorna un Individuo o None
    """
    return self.session.query(Fotografo).get(fotografo_id)

  def get_zona(self, zona_id):
    """
    Retorna un Individuo o None
    """
    return self.session.query(Zona).get(zona_id)

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
          "sexo": ind.sexo,
          "observaciones": ind.observaciones
          }
    else:
      return None

  def bytes_a_imagen(self, datos_imagen):
    """ Crea un QImage a partir de un LargeBinary/QByteArray """
    ba = QtCore.QByteArray.fromBase64(datos_imagen)
    image = QtGui.QImage.fromData(ba)
    return image

  def imagen_a_bytes(self, imagen):
    """Crea un QByteArray desde un QImage"""
    ba = QtCore.QByteArray()
    buff = QtCore.QBuffer(ba)
    buff.open(QtCore.QIODevice.WriteOnly)
    #TODO: Ojo con JPG!!
    imagen.save(buff, "JPG")
    return ba.toBase64().data()

  def calc_distancia(self, v1, v2):
    #TODO: que no haga falta pasar a array
    return np.linalg.norm(np.array(v1)-np.array(v2))

  def similares(self, vector_origen):
    """
    Retorna los individuos asociados a las 5 capturas mas cercanas a vector_origen
    estructura de retorno: es una lista donde cada posicion tiene:
    {
    id: id individuo,
    imagen: primer captura a mostrar del individuo
    lista_imagenes: lista de QImage de las capturas
    sexo: el sexo del individuo
    observaciones: las observaciones del individuo
    }
    """
    mejores = []
    for cap in self.session.query(Captura).all():
      mejores.append((self.calc_distancia(cap.area_por_region, vector_origen), cap))
    mejores.sort(key=lambda a: a[0])
    ret = [] #Lista de retorno
    agregados = set()#Guardamos los ids que ya agregamos
    idx = 0
    while idx < len(mejores) and len(agregados) < 10:
      i = mejores[idx]
      if not i[1].individuo.id in agregados:
        agregados.add(i[1].individuo.id)
        ret.append(
            {
              "id" : i[1].individuo.id,
              "imagen" : self.bytes_a_imagen(i[1].imagen_transformada),
              #todas las capturas del individuo asociado a la captura
              "lista_imagenes" : [self.bytes_a_imagen(j.imagen_transformada) for j in i[1].individuo.capturas],
              "dicc_datos" : {"sexo" : i[1].individuo.sexo, "observaciones": i[1].individuo.observaciones},
              }
        )
      idx += 1
    return ret

  def nuevo_fotografo(self, nombre, apellido, email):
    f = Fotografo(nombre, apellido, email)
    self.session.add(f)
    self.session.commit()
    return f

  def all_fotografos(self):
    return self.session.query(Fotografo).all()

  def nueva_zona(self, nombre, lat, lon):
    z = Zona(nombre, lat, lon)
    self.session.add(z)
    self.session.commit()
    return z

  def all(self, type):
    return self.session.query(type).order_by(type.order())
  
  def all_zonas(self):
    return self.session.query(Zona).all()

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
          "dicc_datos" : {"sexo" : individuo.sexo, "observaciones": individuo.observaciones},
          }
    return ret

  def buscar_capturas(self, individuo_id, captura_id, date_time_inic, date_time_fin, zona_id, fotografo_id,\
                        cant_sapitos_min, cant_sapitos_max, observaciones, archivo):
    """
    busca capturas en base a los campos de una captura
    """
    query = self.session.query(Captura)
    if individuo_id:
      query = query.filter(Captura.individuo_id == individuo_id)
    if captura_id:
      query = query.filter(Captura.id == captura_id)
    if date_time_inic:
      query = query.filter(Captura.fecha > date_time_inic)
    if date_time_fin:
      query = query.filter(Captura.fecha < date_time_fin)
    if zona_id:
      query = query.filter(Captura.zona_id == zona_id)
    if fotografo_id:
      query = query.filter(Captura.fotografo_id == fotografo_id)
    if cant_sapitos_min:
      query = query.filter(Captura.cantidad_acompaniantes > cant_sapitos_min)
    if cant_sapitos_min:
      query = query.filter(Captura.cantidad_acompaniantes < cant_sapitos_max)
    if observaciones:
      query = query.filter(Captura.observaciones.contains(observaciones))
    if archivo:
      query = query.filter(Captura.nombre_imagen.contains(archivo))
    print(query)
    return query

class Captura(Base):
  __tablename__ = 'captura'

  id = Column(Integer, primary_key=True)
  individuo_id = Column(Integer, ForeignKey('individuo.id'))
  imagen_original = deferred(Column(LargeBinary))
  imagen_transformada = deferred(Column(LargeBinary))
  imagen_segmentada = deferred(Column(LargeBinary))
  area_por_region = Column(PickleType)#lista con la cantidad de area por region
  fecha = Column(DateTime)
  lat = Column(Float)
  lon = Column(Float)
  fotografo_id = Column(Integer, ForeignKey('fotografo.id'))
  zona_id = Column(Integer, ForeignKey('zona.id'))
  cantidad_acompaniantes = Column(Integer)
  observaciones = Column(Text)
  nombre_imagen = Column(String)
  puntos = Column(PickleType)
  angulos = Column(PickleType)
  largos = Column(PickleType)

  def __init__(self, img_original, img_trans, img_segmentada, area_por_region,\
      fecha, lat, lon, acompaniantes, observaciones, nombre_imagen, puntos, angulos, largos):
    self.imagen_original = img_original
    self.imagen_transformada = img_trans
    self.imagen_segmentada = img_segmentada
    self.area_por_region = area_por_region
    self.fecha = fecha
    self.lat = lat
    self.lon = lon
    self.cantidad_acompaniantes = acompaniantes
    self.observaciones = observaciones
    self.nombre_imagen = nombre_imagen
    self.puntos = puntos
    self.angulos = angulos
    self.largos = largos

  def __repr__(self):
    return "<Captura('%s')>" % (self.id)

class Fotografo(Base):
  __tablename__ = 'fotografo'

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100))
  apellido = Column(String(100))
  email = Column(String(100))
  capturas = relationship("Captura", backref="fotografo")

  def __init__(self, nombre, apellido, email):
    self.nombre = nombre
    self.apellido = apellido
    self.email = email

  def __repr__(self):
    return "<Fotografo('%s','%s','%s')>" % (self.nombre, self.apellido, self.email)

  def description(self):
    return self.apellido + " " + self.nombre

  @classmethod
  def order(cls):
    return "apellido"

class Zona(Base):
  __tablename__ = 'zona'

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100))
  lat = Column(Float)
  lon = Column(Float)
  capturas = relationship("Captura", backref="zona")

  def __init__(self, nombre, lat, lon):
    self.nombre = nombre
    self.lat = lat
    self.lon = lon

  def __repr__(self):
    return "<Zona('%s')>" % (self.nombre)

  def description(self):
    return self.nombre

  @classmethod
  def order(cls):
    return "nombre"

class Individuo(Base):
  __tablename__ = 'individuo'

  id = Column(Integer, primary_key=True)
  capturas = relationship("Captura", backref="individuo")
  sexo = Column(String)
  observaciones = Column(Text)

  def __init__(self, sexo, observaciones):
    self.sexo = sexo
    self.observaciones = observaciones

  def __repr__(self):
    return "<Individuo('%s')>" % (self.id)
