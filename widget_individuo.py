#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore

class WidgetIndividuo(QtGui.QWidget):

  def __init__(self, parent=None):
    super(WidgetIndividuo, self).__init__(parent)
    self.iniciar_ui()

  def iniciar_ui(self):
    self.setWindowFlags(QtCore.Qt.Window)
    self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Galeria de imagenes para un individuo")
    self.crear_layout()
    self.show()

  def crear_layout(self):
    vertical_lay = QtGui.QVBoxLayout()
    vertical_lay.addWidget(WidgetDatos())

    horizontal_lay = QtGui.QHBoxLayout()
    horizontal_lay.addWidget(WidgetGaleria())
    horizontal_lay.addLayout(vertical_lay)

    self.setLayout(horizontal_lay)

class WidgetBotones(QtGui.QWidget):
  """
  Este widget muestra un par de botones tipo adelante/atras
  """
  def __init__(self, parent=None):
    super(WidgetBotones, self).__init__(parent)
    self.iniciar_ui()

  def iniciar_ui(self):
    #Botones
    self.boton_atras = QtGui.QPushButton('Atras', self)
    self.boton_adelante = QtGui.QPushButton('Adelante', self)
    self.boton_adelante.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
    self.boton_atras.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)

    #Layout
    horizontal_lay = QtGui.QHBoxLayout()
    horizontal_lay.addWidget(self.boton_atras)
    horizontal_lay.addWidget(self.boton_adelante)

    self.setLayout(horizontal_lay)

class WidgetImagen(QtGui.QWidget):
  """
  Este widget muestra una galeria de imagenes para un invididuo dado.
  La idea es usar un QLabel para mostrar las imagenes. Los botones van en una subclase.
  """
  def __init__(self, image, lista_imagenes=None, parent=None):
    super(WidgetImagen, self).__init__(parent)
    self.iniciar_ui()
    self.set_imagen(image)
    self.indice_imagenes = 0
    self.lista_imagenes = lista_imagenes

  def iniciar_imagenes(self):
    #TODO La lista de imagenes la tenemos que obtener de la bd o nos las tendrian que pasar al constructor mejor
    self.lista_imagenes = [
        QtGui.QImage("/home/siko/facultad/pdi/misimagenes/ramoncito/ramon_1_trans.png"),
        QtGui.QImage("/home/siko/facultad/pdi/misimagenes/ramoncito/ramon.2.trans.bmp"),
        QtGui.QImage("/home/siko/facultad/pdi/misimagenes/ramoncito/ramon.3.trans.bmp"),
        ]
    self.set_imagen(self.lista_imagenes[0])

  def iniciar_ui(self):
    #Label
    self.image_label = QtGui.QLabel()
    self.image_label.setBackgroundRole(QtGui.QPalette.Base)
    self.image_label.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)
    self.image_label.setScaledContents(True)

    #Scroll area
    self.scroll_area = QtGui.QScrollArea()
    self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark);
    self.scroll_area.setWidget(self.image_label)
    self.scroll_area.setWidgetResizable(True)

    #Layout
    self.vertical_lay = QtGui.QVBoxLayout()
    self.vertical_lay.addWidget(self.scroll_area)

    #Seteamos el layout para el widget
    self.setLayout(self.vertical_lay)

  def set_imagen(self, image):
    self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))

  def set_lista_imagenes(self, lista_imagenes):
    self.lista_imagenes = lista_imagenes

  def atras(self):
    """
    Mostramos la imagen anterior
    """
    self.indice_imagenes = (self.indice_imagenes - 1) % len(self.lista_imagenes)
    if (self.indice_imagenes < 0): self.indice_imagenes = len(self.lista_imagenes) - 1
    self.set_imagen(self.lista_imagenes[self.indice_imagenes])

  def adelante(self):
    """
    Mostramos la siguiente imagen
    """
    self.indice_imagenes = (self.indice_imagenes + 1) % len(self.lista_imagenes)
    self.set_imagen(self.lista_imagenes[self.indice_imagenes])

class WidgetGaleria(WidgetImagen):
  """
  Extiende WidgetImagen agregandole 2 botones para avanzar y retroceder la galeria.
  """
  def __init__(self, parent=None):
    super(WidgetGaleria, self).__init__(parent)
    self._iniciar_ui()

  def _iniciar_ui(self):
    #Botones para pasar de imagen
    botones = WidgetBotones()
    botones.boton_atras.clicked.connect(self.adelante)
    botones.boton_adelante.clicked.connect(self.atras)

    self.vertical_lay.addWidget(botones)

class WidgetDatos(QtGui.QWidget):
  """
  La idea de este widget es mostrar un grid con los datos de un individuo, onda key value.
  """
  def __init__(self, parent=None):
    super(WidgetDatos, self).__init__(parent)
    #TODO dicc para probar
    self.labels = [("nombre", "pepe"), ("edad", "28"), ("nacionalidad", "polaco")]
    self.iniciar_ui()

  def iniciar_ui(self):
    """
    La ui es un gridlayout con labels tipo key value
    """
    grid_lay = QtGui.QGridLayout()
    idx = 0
    policy = QtGui.QSizePolicy.Minimum
    for k,v in self.labels:
      l1 = QtGui.QLabel(k)
      l1.setSizePolicy(policy, policy)
      grid_lay.addWidget(l1, idx, 0)

      l2 = QtGui.QLabel(v)
      l2.setSizePolicy(policy, policy)
      grid_lay.addWidget(l2, idx, 1)

      idx += 1

    #Hack horrible para que la ultima fila ocupe el mayor espacio posible
    l1 = QtGui.QLabel("")
    l1.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
    grid_lay.addWidget(l1, idx, 0)

    self.setLayout(grid_lay)


class WidgetListaIndividuos(QtGui.QWidget):
  def __init__(self, similares = {}, parent=None):
    super(WidgetListaIndividuos, self).__init__(parent)
    self.iniciar_ui(similares)

  def iniciar_ui(self, similares, addRadio = True):
    vertical_lay = QtGui.QVBoxLayout()
    for key,value in similares.iteritems():
      horizontal_lay = QtGui.QHBoxLayout()
      print value
      value.save("hectorcarlone.jpg")
      if (addRadio):
        radio = QtGui.QRadioButton()
        radio.id_individuo = key
        horizontal_lay.addWidget(radio)
      horizontal_lay.addWidget(WidgetImagen(value))
      boton_mostrar = QtGui.QPushButton("Mostrar individuo")
      boton_mostrar.clicked.connect(self.launch)
      boton_mostrar.id_individuo = key
      horizontal_lay.addWidget(boton_mostrar)
      vertical_lay.addLayout(horizontal_lay)
    self.setLayout(vertical_lay)

  def launch(self):
    print self.sender().id_individuo
    WidgetIndividuo(self)

class WidgetBotones(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetBotones, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def iniciar_ui(self):
    horizontal_layout = QtGui.QHBoxLayout()
    self.botonNuevo = QtGui.QPushButton("Nuevo")
    self.botonAgrCaptura = QtGui.QPushButton("Agregar Captura")
    horizontal_layout.addWidget(self.botonNuevo)
    horizontal_layout.addWidget(self.botonAgrCaptura)

    self.botonNuevo.clicked.connect(self.launch)

    self.setLayout(horizontal_layout)

  def launch(self):
    WidgetNuevoIndividuo(self)

  def save(self, attr):
    self.parent.save(attr)

class WidgetNuevoIndividuo(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetNuevoIndividuo, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def iniciar_ui(self):
    self.labeln = QtGui.QLabel("Nombre: ")
    self.labelz = QtGui.QLabel("Zona: ")
    self.editn = QtGui.QLineEdit()
    self.editz = QtGui.QLineEdit()

    qgridLayout = QtGui.QGridLayout()

    qgridLayout.addWidget(self.labeln, 0, 0)
    qgridLayout.addWidget(self.editn, 0, 1)
    qgridLayout.addWidget(self.labelz, 1, 0)
    qgridLayout.addWidget(self.editz, 1, 1)

    self.setLayout(qgridLayout)
    self.setWindowFlags(QtCore.Qt.Window)
    self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Formulario para agregar nuevo individuo")

    botonGuardar = QtGui.QPushButton("Guardar")

    botonGuardar.clicked.connect(self.save)

    qgridLayout.addWidget(botonGuardar, 2, 1)

    self.show()

  def save(self):
    self.parent.save({ "nombre" : self.editn.text(), "zona" : self.editz.text()})

def main():
  app = QtGui.QApplication(sys.argv)
  #ex = WidgetIndividuo()
  ex = WidgetListaIndividuos()
  sys.exit(app.exec_())


if __name__ == '__main__':
    main()
