#!/usr/bin/env python

#Se importa sqlalchemy
from sqlalchemy import *
from sqlalchemy.types import LargeBinary
from sqlalchemy.orm import relationship, backref, sessionmaker, deferred
from sqlalchemy.ext.declarative import declarative_base
from PySide import QtCore, QtGui
import Image
import os

#Se crea la instancia del motor de la base de datos y se asocia con un
#archivo
engine = create_engine('sqlite:///sapitoserrano.db')

metadata = MetaData(engine)
Base = declarative_base(metadata=metadata)

class Sapito(Base):
	__tablename__ = 'sapito'
	id = Column(Integer, primary_key=True)
	n = Column(String(100))
	n2 = deferred(Column(LargeBinary))

	def __init__(self, name, img):
		self.n = name
		self.n2 = img

	def __repr__(self):
		return "<Sapito('%s')>" % (self.name)

metadata.create_all()

Session = sessionmaker(bind=engine)
session = Session()

image = QtGui.QImage("panzas/IMG_0237.JPG")

ba = QtCore.QByteArray()
buff = QtCore.QBuffer(ba)
buff.open(QtCore.QIODevice.WriteOnly)
image.save(buff, "JPG")

session.add(Sapito("Saparala", ba))
session.commit()
"""session.add_all({
	Contact("Ramirez Pedro", groups={groups[1],groups[3],groups[4]}),
        Contact("Antonelli Anibal", groups=[groups[4],groups[0]]),
        Contact("Perebundo Raul", groups=[groups[1],groups[2]]),
        Contact("Jolito Jose", groups=[groups[1],groups[2],groups[3]]),
        Contact("Jeronimes Jeronimo", groups=[groups[1]])})

"""
"""
#Se inserta datos en la tabla grupos.
i = grupos.insert()
i.execute(grupo='Guacara',descripcion='Ciudad de Carabobo')
i.execute({'grupo':'Valencia','descripcion':'Capital de Carabobo'},
    {'grupo':'Maracay','descripcion':'Capital de Aragua'},
    {'grupo':'Merida','descripcion':'Capital de Merida'})

#Se inserta datos en la tabla contactos    
u = contactos.insert()
u.execute(nombre='Ernesto Crespo',telefono='04155673029',grupo_id=1)
u.execute(nombre='Pedro Perez',telefono='0295212223',grupo_id=2)
u.execute(nombre='Jhon Doe',telefono='04184488484',grupo_id=2)
u.execute(nombre='Jane Doe',telefono='04184488482',grupo_id=1)
u.execute(nombre='Pepito de los palotes',telefono='04184588484',grupo_id=3)

#Se hace consulta de la tabla contactos
s = contactos.select()
rs = s.execute()

#Se hace consultas de la tabla grupos.
t = grupos.select()
ts = t.execute()

#Se muestra la tabla grupos
print "GRUPOS"
print "-------------------------------------"
for fila in ts:
    print "id: %s,Grupo: %s, Descripcion:%s" %(fila[0],fila[1],fila[2])
print "--------------------------------------"

del fila
#Se muestra la tabla contactos.
print "CONTACTOS"
print "-------------------------------------"
for fila in rs:
    print "Nombre: %s, telefono %s, Grupo %s" %(fila[1],fila[2],fila[3]) 
print "--------------------------------------"

#Se borra la fila del id 1 de la tabla grupos
t = grupos.delete(text("id=1"))
t.execute()

#Se realiza una consulta de la tabla grupos
q = grupos.select()
qs = q.execute()

#Se muestra la tabla grupos, 
#ahora no tiene la fila del grupo Guacara.
print "GRUPOS"
print "-------------------------------------"
for fila in qs:
    print "id: %s,Grupo: %s, Descripcion:%s" %(fila[0],fila[1],fila[2])
print "--------------------------------------"


#Se muestra los contactos del grupo 2.
print "Mostrar contactos del grupo 2"
del q
del qs
q = contactos.select(text("grupo_id=2"))
qs = q.execute()
print "-------------------------------------"
for fila in qs:
    print "Nombre: %s, telefono %s, Grupo %s" %(fila[1],fila[2],fila[3]) 
print "--------------------------------------"
"""
