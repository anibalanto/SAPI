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

class Captura(Base):
  __tablename__ = 'captura'

  id = Column(Integer, primary_key=True)
  individuo_id = Column(Integer, ForeignKey('individuo.id'))
  imagen = deferred(Column(LargeBinary))
  area_por_region = Column(PickleType)#lista con la cantidad de area por region

  def __init__(self, imagen, area_por_region):
    self.imagen = imagen
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

def calc_distancia(vector_captura, vector_origen):
  pass

def get_top5(session, vector_origen):
  mejores = []
  for cap in session.query(Captura).all():
    mejores.append((calc_distancia(cap.area_por_region, vector_origen), cap))
  mejores.sort(key=lambda a: a[0])
  return mejores[:5]

def probar(session):
  image = QtGui.QImage("../misimagenes/ramoncito/ramon.1.trans.bmp")

  ba = QtCore.QByteArray()
  buff = QtCore.QBuffer(ba)
  buff.open(QtCore.QIODevice.WriteOnly)
  image.save(buff, "JPG")

  arr = np.array([1.2,345,33.4])

  ind = Individuo("pepe")

  c1 = Captura(ba, arr)
  c2 = Captura(ba, arr)

  ind.capturas.append(c1)
  ind.capturas.append(c2)

  session.add(ind)
  session.commit()

def iniciarAlchemy():
  engine = create_engine(DBPATH)
  Session = sessionmaker(bind=engine)
  session = Session()
  return session, engine

def crear_tablas(engine):
  #Creamos la tabla
  Base.metadata.create_all(engine)#Las tablas que ya existen no se tocan

def main():
  session, engine = iniciarAlchemy()
  crear_tablas(engine)
  probar(session)

if __name__ == "__main__":
  main()
