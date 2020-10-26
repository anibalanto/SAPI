#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import traceback
from PySide2 import QtWidgets, QtCore, QtGui
from db import ManagerBase, Fotografo, Zona
from widget_table import *

sexo = ["Macho", "Hembra", "No determinado"]


class WidgetAgregarZona(QtWidgets.QWidget):

  def __init__(self, parent, widget_extend = None):
    super(WidgetAgregarZona, self).__init__(parent, QtCore.Qt.Window)
    self.parent = parent
    self.setLayout(self.iniciar_ui())
    self.show()
    self.widget_extend = widget_extend

  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text()
    la = self.lat_input.text() if self.lat_input.text() != '' else None
    lo = self.lon_input.text() if self.lon_input.text() != '' else None
    if (n):
      zona = db_man.nueva_zona(n, la, lo)
      self.close()
      if self.widget_extend != None:
        self.widget_extend.extend(zona)
      return True
    return False

  def iniciar_ui(self):
    #labels, inputs y boton guardar
    self.setWindowTitle("Nueva Zona")
    self.name_label = QtWidgets.QLabel("Nombre")
    self.name_input = QtWidgets.QLineEdit()
    self.lat_label = QtWidgets.QLabel("Latitud")
    self.lat_input = QtWidgets.QLineEdit()
    self.lon_label = QtWidgets.QLabel("Longitud")
    self.lon_input = QtWidgets.QLineEdit()
    save_button = QtWidgets.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtWidgets.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lat_label, 1, 0)
    lay.addWidget(self.lat_input, 1, 1)
    lay.addWidget(self.lon_label, 2, 0)
    lay.addWidget(self.lon_input, 2, 1)
    lay.addWidget(save_button, 3, 1)
    return lay

class WidgetAgregarZonaRefreshTable(WidgetAgregarZona):

  def __init__(self, parent, widget_extend = None):
    super(WidgetAgregarZonaRefreshTable, self).__init__(parent, widget_extend)

  def guardar(self):
    if (super(WidgetAgregarZonaRefreshTable, self).guardar()):
      self.parent.refresh()

class WidgetAgregarFotografo(QtWidgets.QWidget):
  def __init__(self, parent, widget_extend = None):
    super(WidgetAgregarFotografo, self).__init__(parent, QtCore.Qt.Window)
    self.parent = parent
    self.setLayout(self.iniciar_ui())
    self.show()
    self.widget_extend = widget_extend

  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text()
    ln = self.lastname_input.text()
    em = self.email_input.text()
    if (n and ln and em):
      fotografo = db_man.nuevo_fotografo(n, ln, em)
      self.close()
      if self.widget_extend != None:
        self.widget_extend.extend(fotografo)
      return True
    return False

  def iniciar_ui(self):
    #labels, inputs y boton guardar
    self.setWindowTitle("Nuevo Fotografo")
    self.name_label = QtWidgets.QLabel("Nombre")
    self.name_input = QtWidgets.QLineEdit()
    self.lastname_label = QtWidgets.QLabel("Apellido")
    self.lastname_input = QtWidgets.QLineEdit()
    self.email_label = QtWidgets.QLabel("e-mail")
    self.email_input = QtWidgets.QLineEdit()
    save_button = QtWidgets.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtWidgets.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lastname_label, 1, 0)
    lay.addWidget(self.lastname_input, 1, 1)
    lay.addWidget(self.email_label, 2, 0)
    lay.addWidget(self.email_input, 2, 1)
    lay.addWidget(save_button, 3, 1)

    self.setWindowFlags(QtCore.Qt.Window)
    return lay

class WidgetAgregarFotografoRefreshTable(WidgetAgregarFotografo ):

  def __init__(self, parent, widget_extend = None):
    super(WidgetAgregarFotografoRefreshTable, self).__init__(parent, widget_extend)

  def guardar(self):
    if (super(WidgetAgregarFotografoRefreshTable, self).guardar()):
      self.parent.refresh()

class WidgetIndividuoConCapturas(CalleableWindow):
  """
  Widget que contiene una imagen del individuo con sus respectivas capturas
  las capturas se encuentran dentro de una tabla
  Hereda de CalleableWindow la cual es creada desde una tabla
  """
  def __init__(self, parent, id_individuo, ident):
    super(WidgetIndividuoConCapturas, self).__init__(parent, ident)
    self.id_individuo = id_individuo
    individuo = ManagerBase().get_individuo(id_individuo)
    self.setLayout(self.iniciar_ui(individuo))
    self.show()

  def guardar(self):
    sexo = self.sexo_input.itemText(self.sexo_input.currentIndex())
    observaciones = self.observaciones_input.toPlainText() if self.observaciones_input.toPlainText() != '' else None
    ManagerBase().modificar_individuo(self.id_input.text(), sexo, observaciones)
    self.close()
    self.parent.refresh()

  def refresh(self):
    individuo = ManagerBase().get_individuo(self.id_individuo)
    if individuo:
      self.table.set_data(individuo.capturas)
    else:
      self.parent.refresh()
      self.close()

  def borrar(self):
    reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Realmente desea borrar este individuo?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

    if reply == QtWidgets.QMessageBox.Yes:
      ManagerBase().borrar_individuo(self.id_individuo)
      self.close()
      self.parent.refresh()

  def iniciar_ui(self, individuo):
    self.setWindowTitle("Individuo")
    self.id = QtWidgets.QLabel("id")
    self.id_input = QtWidgets.QLabel(str(individuo.id))
    self.sexo = QtWidgets.QLabel("sexo")
    self.sexo_input = ComboBoxSexo()
    #self.sexo_input.setDisabled(True)
    self.sexo_input.setCurrentIndex(sexo.index(individuo.sexo))
    self.observaciones = QtWidgets.QLabel("Observaciones")
    self.observaciones_input = QtWidgets.QTextEdit(individuo.observaciones)
    #self.observaciones_input.setDisabled(True)

    self.boton_borrar = QtWidgets.QPushButton("Borrar")
    self.boton_borrar.clicked.connect(self.borrar)

    self.boton_guardar = QtWidgets.QPushButton("Guardar")
    self.boton_guardar.clicked.connect(self.guardar)

    self.table = WidgetTableCapturasDeIndividuo(self, individuo.capturas)
    self.vbox = QtWidgets.QVBoxLayout()

    #layout
    lay = QtWidgets.QGridLayout()
    lay.addWidget(self.id, 0, 0)
    lay.addWidget(self.id_input, 0, 1)
    lay.addWidget(self.sexo, 1, 0)
    lay.addWidget(self.sexo_input, 1, 1)
    lay.addWidget(self.observaciones, 2, 0)
    lay.addWidget(self.observaciones_input, 2, 1)
    #lay.addWidget(save_button, 3, # 1)

    self.vbox.addLayout(lay)
    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(self.boton_borrar)
    hbox.addWidget(self.boton_guardar)
    self.vbox.addLayout(hbox)
    self.vbox.addWidget(self.table)
    return self.vbox


class WidgetIndividuo(QtWidgets.QWidget):
  """
  Widget compuesto de un WidgetDatos y un WidgetGaleria.
  Sirve para mostrar los datos de un individuo, y las capturas de este individuo.
  lista_imagenes: lista de imagenes para la galeria. Esta lista se muestra en
  WidgetGaleria.
  datos: diccionario con los datos del individuo, que se van a mostrar en el
  WidgetDatos.
  """

  def __init__(self, lista_imagenes, datos_individuo, parent=None):
    super(WidgetIndividuo, self).__init__(parent)
    self.iniciar_ui(lista_imagenes, datos_individuo)

  def iniciar_ui(self, lista_imagenes, datos_individuo):
    self.setWindowFlags(QtCore.Qt.Window)
    #self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Galeria de imagenes para un individuo")
    self.crear_layout(lista_imagenes, datos_individuo)
    self.show()

  def crear_layout(self, lista_imagenes, datos_individuo):
    vertical_lay = QtWidgets.QVBoxLayout()
    vertical_lay.addWidget(WidgetDatos(datos_individuo))

    horizontal_lay = QtWidgets.QHBoxLayout()
    horizontal_lay.addWidget(WidgetGaleria(lista_imagenes))
    horizontal_lay.addLayout(vertical_lay)

    self.setLayout(horizontal_lay)

class WidgetBotonesAtrasAdelante(QtWidgets.QWidget):
  """
  Este widget muestra un par de botones tipo adelante/atras
  """
  def __init__(self, parent=None):
    super(WidgetBotonesAtrasAdelante, self).__init__(parent)
    self.iniciar_ui()

  def iniciar_ui(self):
    #Botones
    self.boton_atras = QtWidgets.QPushButton('Atras', self)
    self.boton_adelante = QtWidgets.QPushButton('Adelante', self)
    self.boton_adelante.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
    self.boton_atras.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

    #Layout
    horizontal_lay = QtWidgets.QHBoxLayout()
    horizontal_lay.addWidget(self.boton_atras)
    horizontal_lay.addWidget(self.boton_adelante)

    self.setLayout(horizontal_lay)

class WidgetImagen(QtWidgets.QWidget):
  """
  Este widget muestra una galeria de imagenes para un invididuo dado.
  La idea es usar un QLabel para mostrar las imagenes. Los botones van en una subclase.
  """
  def __init__(self, lista_imagenes, parent=None):
    super(WidgetImagen, self).__init__(parent)
    self.iniciar_ui()
    if lista_imagenes:
      self.set_imagen(lista_imagenes[0])
    self.indice_imagenes = 0
    self.lista_imagenes = lista_imagenes

  def iniciar_ui(self):
    #Label
    self.image_label = QtWidgets.QLabel()
    self.image_label.setBackgroundRole(QtGui.QPalette.Base)
    self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Ignored)
    self.image_label.setScaledContents(True)

    #Scroll area
    self.scroll_area = QtWidgets.QScrollArea()
    self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark);
    self.scroll_area.setWidget(self.image_label)
    self.scroll_area.setWidgetResizable(True)

    #Layout
    self.vertical_lay = QtWidgets.QVBoxLayout()
    self.vertical_lay.addWidget(self.scroll_area)

    #Seteamos el layout para el widget
    self.setLayout(self.vertical_lay)

  def set_imagen(self, image):
    """
    Antes de agregar la imagen al pixmap, la escalamos a 150x150
    """
    self.image_label.setPixmap(QtGui.QPixmap.fromImage(image.scaled(150,150)))

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
  Para obtener los botones, se compone usa el WidgetBotonesAtrasAdelante.
  lista_imagenes: lista con las imagenes que se van a mostrar en la galeria.
  """
  def __init__(self, lista_imagenes, parent=None):
    super(WidgetGaleria, self).__init__(lista_imagenes, parent)
    self._iniciar_ui()

  def _iniciar_ui(self):
    #Botones para pasar de imagen
    botones = WidgetBotonesAtrasAdelante()
    botones.boton_atras.clicked.connect(self.adelante)
    botones.boton_adelante.clicked.connect(self.atras)

    self.vertical_lay.addWidget(botones)

class WidgetDatos(QtWidgets.QWidget):
  """
  La idea de este widget es mostrar un grid con los datos de un individuo,
  con los datos de dicc_datos.
  """
  def __init__(self, dicc_datos, parent=None):
    super(WidgetDatos, self).__init__(parent)
    self.labels = dicc_datos
    self.iniciar_ui()

  def iniciar_ui(self):
    """
    La ui es un gridlayout con labels tipo key value
    """
    grid_lay = QtWidgets.QGridLayout()
    idx = 0
    policy = QtWidgets.QSizePolicy.Minimum
    for k,v in self.labels.items():
      l1 = QtWidgets.QLabel(k)
      l1.setSizePolicy(policy, policy)
      grid_lay.addWidget(l1, idx, 0)

      l2 = QtWidgets.QLabel(v)
      l2.setSizePolicy(policy, policy)
      grid_lay.addWidget(l2, idx, 1)

      idx += 1

    #Hack horrible para que la ultima fila ocupe el mayor espacio posible
    l1 = QtWidgets.QLabel("")
    l1.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    grid_lay.addWidget(l1, idx, 0)

    self.setLayout(grid_lay)

class ComboBoxSexo(QtWidgets.QComboBox):

  def __init__(self):
    super(ComboBoxSexo, self).__init__()
    for s in sexo:
      self.addItem(s)


class MyRadioButtonSexo(QtWidgets.QRadioButton):

  def __init__(self, text, parent):
    self.parent = parent
    super(MyRadioButtonSexo, self).__init__(text)
    self.clicked.connect(self.click)

  def click(self):
    self.parent.sexo = self.text()

class MyRadioButton(QtWidgets.QRadioButton):

  def __init__(self, parent):
    self.parent = parent
    super(MyRadioButton, self).__init__()
    self.clicked.connect(self.click)

  def click(self):
    #if (self.parent.iRadioChecked == -1):
    self.parent.widget_botones.botonAgrCaptura.setEnabled(True)
    self.parent.iRadioChecked = self.index

class WidgetScroleable(QtWidgets.QWidget):
  """
  Agrega una barra de scroll, al widget que se le pasa como parametro.
  """
  def __init__(self, widget, parent=None):
    super(WidgetScroleable, self).__init__(parent)
    self.scroll_area = QtWidgets.QScrollArea()
    self.scroll_area.setWidget(widget)

    self.lay = QtWidgets.QVBoxLayout()
    self.lay.addWidget(self.scroll_area)

    self.setLayout(self.lay)

def WidgetListaIndividuosScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuos(similares, parent))

class WidgetListaIndividuos(QtWidgets.QWidget):
  """
  Widget que muestra una lista vertical de 1 captura por individuo, con un radiobutton y un boton para mostrar el individuo.
  similares: diccionario de la forma
    {id_individuo: {imagen: <imagen captura>, dicc_datos: <diccionario con los datos del individuo>, capturas: <lista de imagenes de las capturas>}}
  Todas las imagenes son QImage.
  """
  def __init__(self, similares=None, parent=None):
    self.parent = parent
    super(WidgetListaIndividuos, self).__init__(parent)
    if similares is None: similares = {}
    #Creamos el layout y lo seteamos. Las subclases, pueden overridear este metodo para modificar el layout.
    lay = self.crear_layout(similares)
    self.setLayout(lay)

  def crear_layout(self, similares):
    vertical_lay = QtWidgets.QVBoxLayout()
    for sapo_id, dicc_sapo in similares.items():
      horizontal_lay = QtWidgets.QHBoxLayout()
      #En vez de pasar la imagen sola, pasamos una lista de 1 elemento con la imagen.
      horizontal_lay.addWidget(WidgetImagen([dicc_sapo["imagen"]]))
      boton_mostrar = QtWidgets.QPushButton("Mostrar individuo")
      boton_mostrar.clicked.connect(self.launch)
      boton_mostrar.id_individuo = sapo_id
      boton_mostrar.datos_individuo = dicc_sapo["dicc_datos"]
      boton_mostrar.lista_imagenes = dicc_sapo["lista_imagenes"]
      porcentaje_similitud = QtWidgets.QLabel(dicc_sapo["porcentaje_similitud"])
      horizontal_lay.addWidget(boton_mostrar)
      horizontal_lay.addWidget(porcentaje_similitud)
      vertical_lay.addLayout(horizontal_lay)
    return vertical_lay

  def launch(self):
    WidgetIndividuo(self.sender().lista_imagenes, self.sender().datos_individuo, self)

def WidgetListaIndividuosStandaloneScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuosStandalone(similares, parent))

class WidgetListaIndividuosStandalone(WidgetListaIndividuos):
  """
  Esta lista de individuos, muestra el thumbnail de cada individuo, los datos del mismo
  y el boton "mostrar individuo" que lanza la galeria.
  """

  def crear_layout(self, similares):
    """
    Metemos un WidgetDatos entre la imagen y el boton mostrar.
    """
    lay = super(WidgetListaIndividuosStandalone, self).crear_layout(similares)
    for idx, key in enumerate(similares):
      lay.itemAt(idx).insertWidget(1,WidgetDatos(similares[key]["dicc_datos"]))
    return lay

def WidgetListaIndividuosRadiosScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuosRadios(similares, parent))

class WidgetListaIndividuosRadios(WidgetListaIndividuos):
  """
  Sublcase de WidgetListaIndividuos que agrega radiobuttons a cada individuo.
  """

  def crear_layout(self, similares):
    vertical_lay = QtWidgets.QVBoxLayout()
    self.parent.radios = []
    i = 0
    for dicc_sapo in similares:
      sapo_id = dicc_sapo["id"]
      horizontal_lay = QtWidgets.QHBoxLayout()
      radio = MyRadioButton(self.parent)
      radio.id_individuo = sapo_id
      radio.index = i
      horizontal_lay.addWidget(radio)
      self.parent.radios.append(radio)
      i = i + 1
      #En vez de pasar la imagen sola, pasamos una lista de 1 elemento con la imagen.
      horizontal_lay.addWidget(WidgetImagen([dicc_sapo["imagen"]]))
      boton_mostrar = QtWidgets.QPushButton("Mostrar individuo")
      boton_mostrar.clicked.connect(self.launch)
      boton_mostrar.id_individuo = sapo_id
      boton_mostrar.datos_individuo = dicc_sapo["dicc_datos"]
      boton_mostrar.lista_imagenes = dicc_sapo["lista_imagenes"]
      porcentaje_similitud = QtWidgets.QLabel(str(dicc_sapo["porcentaje_similitud"]))
      horizontal_lay.addWidget(boton_mostrar)
      horizontal_lay.addWidget(porcentaje_similitud)
      vertical_lay.addLayout(horizontal_lay)
    return vertical_lay

class WidgetBotonesAgregarCaptura(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetBotonesAgregarCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def iniciar_ui(self):
    horizontal_layout = QtWidgets.QHBoxLayout()
    self.botonNuevo = QtWidgets.QPushButton("Nuevo")
    self.botonAgrCaptura = QtWidgets.QPushButton("Agregar Captura")
    self.botonAgrCaptura.setEnabled(False)
    horizontal_layout.addWidget(self.botonNuevo)
    horizontal_layout.addWidget(self.botonAgrCaptura)

    self.botonNuevo.clicked.connect(self.launchNuevo)
    self.botonAgrCaptura.clicked.connect(self.launchAgrCaptura)

    self.setLayout(horizontal_layout)

  def launchNuevo(self):
    WidgetNuevoIndividuo(self.parent)

  def launchAgrCaptura(self):
    WidgetNuevaCaptura(self.parent, self.parent.iRadioChecked)
#    print self.parent.iRadioChecked
#    if (self.parent.iRadioChecked != -1):
#      self.parent.agregarCaptura(self.parent.radios[self.parent.iRadioChecked].id_individuo, {})


class WidgetAgregarCaptura(QtWidgets.QWidget):

  def __init__(self, parent, posicion_algoritmo=-1):
    super(WidgetAgregarCaptura, self).__init__(parent)
    self.parent = parent
    self.posicion_algoritmo = posicion_algoritmo
    self.iniciar_ui()


  def guardar(self, individuo_id = None):
    db_man = ManagerBase()
    if (individuo_id == None):
      individuo_id = self.parent.radios[self.parent.iRadioChecked].id_individuo
    img_original = self.parent.q_img
    img_transformada = self.parent.qimage_transformada
    img_segmentada = self.parent.qimage_segmentada
    vector_regiones = self.parent.vector_regiones
    fecha = self.fecha.dateTime().toPython() if self.fecha.dateTime() != '01/01/2000 00:00:00' else None
    lat = self.latitud.text() if self.latitud.text() != '' else None
    lon = self.longitud.text() if self.longitud.text() != '' else None
    acompaniantes = self.cantidadSapitos.text() if self.cantidadSapitos.text() != '' else None
    observaciones = self.observaciones.toPlainText() if self.observaciones.toPlainText() != '' else None
    nombre_imagen = self.parent.filename_nopath
    puntos = self.parent.getPoints()
    angulos = self.parent.getAngles()
    largos = self.parent.getLarges()
    fotografo_id = self.fotografos.items.itemData(self.fotografos.items.currentIndex())
    zona_id = self.zona.items.itemData(self.zona.items.currentIndex())
    superficie_ocupada = self.parent.superficie_ocupada
    posicion_algoritmo = self.posicion_algoritmo
    if (individuo_id and img_original and img_segmentada and img_transformada):
      ManagerBase().crear_captura(individuo_id, img_original, img_transformada, img_segmentada, vector_regiones, fecha, lat, lon,\
                           acompaniantes, observaciones, nombre_imagen, puntos, angulos, largos, fotografo_id, zona_id, superficie_ocupada, posicion_algoritmo)

      self.close()


  def iniciar_ui(self):
    self.fecha = QtWidgets.QDateTimeEdit()
    self.zona = WidgetComboBoxExtensible(Zona, self.parent)
    self.latitud = QtWidgets.QLineEdit()
    self.longitud = QtWidgets.QLineEdit()
    self.fotografos = WidgetComboBoxExtensible(Fotografo, self.parent)
    self.cantidadSapitos = QtWidgets.QLineEdit()
    self.observaciones = QtWidgets.QTextEdit()

    qgridLayout = QtWidgets.QGridLayout()

    qgridLayout.addWidget(QtWidgets.QLabel("CAPTURA"), 0, 0)
    qgridLayout.addWidget(QtWidgets.QLabel("fecha: "), 1, 0)
    qgridLayout.addWidget(self.fecha, 1, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Zona: "), 2, 0)
    qgridLayout.addWidget(self.zona, 2, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Latitud: "), 3, 0)
    qgridLayout.addWidget(self.latitud, 3, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Longitud: "), 4, 0)
    qgridLayout.addWidget(self.longitud, 4, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Fotografo: "), 5, 0)
    qgridLayout.addWidget(self.fotografos, 5, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Sapitos acomp: "), 6, 0)
    qgridLayout.addWidget(self.cantidadSapitos, 6, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Observaciones: "), 7, 0)
    qgridLayout.addWidget(self.observaciones, 7, 1)

    self.setLayout(qgridLayout)

class WidgetEditarCaptura(CalleableWindow):

  def __init__(self, parent, id_captura, ident):
    super(WidgetEditarCaptura, self).__init__(parent, ident)
    self.id_captura = id_captura
    self.iniciar_ui()
    self.show()
    self.llenar()

  def guardar(self):
    db_man = ManagerBase()

    fecha = self.fecha.dateTime().toPython() if self.fecha.dateTime() != '01/01/2000 00:00:00' else None
    lat = self.latitud.text() if self.latitud.text() != '' else None
    lon = self.longitud.text() if self.longitud.text() != '' else None
    acompaniantes = self.cantidadSapitos.text() if self.cantidadSapitos.text() != '' else None
    observaciones = self.observaciones.toPlainText() if self.observaciones.toPlainText() != '' else None
    fotografo_id = self.fotografos.items.itemData(self.fotografos.items.currentIndex())
    zona_id = self.zona.items.itemData(self.zona.items.currentIndex())
    db_man.modificar_captura(self.id_captura,fecha, lat, lon, acompaniantes, observaciones, fotografo_id, zona_id)

    self.close()
    self.refresh_table()


  def refresh_table(self):
    self.parent.refresh()

  def borrar(self):
    reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Realmente desea borrar esta captura?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

    if reply == QtWidgets.QMessageBox.Yes:
      ManagerBase().borrar_captura(self.id_captura)
      self.close()
      self.refresh_table()

  def iniciar_ui(self):
    self.setWindowTitle("Captura")
    self.fecha = QtWidgets.QDateTimeEdit()
    self.zona = WidgetComboBoxExtensible(Zona, self.parent)
    self.latitud = QtWidgets.QLineEdit()
    self.longitud = QtWidgets.QLineEdit()
    self.fotografos = WidgetComboBoxExtensible(Fotografo, self.parent)
    self.cantidadSapitos = QtWidgets.QLineEdit()
    self.observaciones = QtWidgets.QTextEdit()
    self.imagen_label = QtWidgets.QLabel()

    qgridLayout = QtWidgets.QGridLayout()

    qgridLayout.addWidget(QtWidgets.QLabel("CAPTURA"), 0, 0)
    qgridLayout.addWidget(QtWidgets.QLabel("fecha: "), 1, 0)
    qgridLayout.addWidget(self.fecha, 1, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Zona: "), 2, 0)
    qgridLayout.addWidget(self.zona, 2, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Latitud: "), 3, 0)
    qgridLayout.addWidget(self.latitud, 3, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Longitud: "), 4, 0)
    qgridLayout.addWidget(self.longitud, 4, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Fotografo: "), 5, 0)
    qgridLayout.addWidget(self.fotografos, 5, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Sapitos acomp: "), 6, 0)
    qgridLayout.addWidget(self.cantidadSapitos, 6, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Observaciones: "), 7, 0)
    qgridLayout.addWidget(self.observaciones, 7, 1)

    self.boton_borrar = QtWidgets.QPushButton("Borrar")
    self.boton_borrar.clicked.connect(self.borrar)

    self.boton_guardar = QtWidgets.QPushButton("Guardar")
    self.boton_guardar.clicked.connect(self.guardar)

    self.vbox = QtWidgets.QVBoxLayout()

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(self.boton_borrar)
    hbox.addWidget(self.boton_guardar)
    self.vbox.addLayout(qgridLayout)
    self.vbox.addLayout(hbox)

    hbox_principal = QtWidgets.QHBoxLayout()
    hbox_principal.addLayout(self.vbox)
    hbox_principal.addWidget(self.imagen_label)

    self.setLayout(hbox_principal)

  def llenar(self):
    if self.id_captura:
      captura = ManagerBase().get_captura(self.id_captura)
      date_time = QtCore.QDateTime(QtCore.QDateTime.fromString(str(captura.fecha), "yyyy-MM-dd hh:mm:ss"))
      self.fecha.setDateTime(date_time)

      index = self.fotografos.items.findData(captura.fotografo_id)
      self.fotografos.items.setCurrentIndex(index)

      index = self.zona.items.findData(captura.zona_id)
      self.zona.items.setCurrentIndex(index)

      self.latitud.setText(str(captura.lat if captura.lat != None else ""))
      self.longitud.setText(str(captura.lon if captura.lon != None else ""))
      self.cantidadSapitos.setText(str(captura.cantidad_acompaniantes if captura.cantidad_acompaniantes != None else ""))
      self.observaciones.setText(captura.observaciones)

      db_man = ManagerBase()
      otra_captura = db_man.get_captura(captura.id)
      qimage = ManagerBase().bytes_a_imagen(otra_captura.imagen_original_thumbnail_mediana)

      self.imagen_label.setPixmap(QtGui.QPixmap.fromImage(qimage))


class WidgetEditarFotografo(CalleableWindow):

  def __init__(self, parent, id_fotografo, ident):
    super(WidgetEditarFotografo, self).__init__(parent, ident)
    self.id_fotografo = id_fotografo
    self.iniciar_ui()
    self.show()
    self.llenar()


  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text() if self.name_input.text() != '' else None
    ln = self.lastname_input.text() if self.lastname_input.text() != '' else None
    em = self.email_input.text() if self.email_input.text() != '' else None
    if (n and ln and em):
      db_man.modificar_fotografo(self.id_fotografo, n, ln, em)
      self.close()
      self.refresh_table()

  def refresh_table(self):
    self.parent.refresh()

  def borrar(self):
    reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Realmente desea borrar este fotografo?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

    if reply == QtWidgets.QMessageBox.Yes:
      ManagerBase().borrar_fotografo(self.id_fotografo)
      self.close()
      self.refresh_table()

  def iniciar_ui(self):
    #labels, inputs y boton guardar
    self.setWindowTitle("Editar Fotografo")
    self.name_label = QtWidgets.QLabel("Nombre")
    self.name_input = QtWidgets.QLineEdit()
    self.lastname_label = QtWidgets.QLabel("Apellido")
    self.lastname_input = QtWidgets.QLineEdit()
    self.email_label = QtWidgets.QLabel("e-mail")
    self.email_input = QtWidgets.QLineEdit()
    delete_button = QtWidgets.QPushButton("Borrar")
    delete_button.clicked.connect(self.borrar)
    save_button = QtWidgets.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtWidgets.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lastname_label, 1, 0)
    lay.addWidget(self.lastname_input, 1, 1)
    lay.addWidget(self.email_label, 2, 0)
    lay.addWidget(self.email_input, 2, 1)
    lay.addWidget(save_button, 3, 1)

    self.setWindowFlags(QtCore.Qt.Window)

    self.vbox = QtWidgets.QVBoxLayout()
    self.vbox.addLayout(lay)
    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(delete_button)
    hbox.addWidget(save_button)
    self.vbox.addLayout(hbox)
    self.setLayout(self.vbox)

  def llenar(self):
    if self.id_fotografo:
      fotografo = ManagerBase().get_fotografo(self.id_fotografo)
      self.name_input.setText(str(fotografo.nombre if fotografo.nombre != None else ""))
      self.lastname_input.setText(str(fotografo.apellido if fotografo.apellido != None else ""))
      self.email_input.setText(str(fotografo.email if fotografo.email != None else ""))

class WidgetEditarZona(CalleableWindow):

  def __init__(self, parent, id_zona, ident):
    super(WidgetEditarZona, self).__init__(parent, ident)
    self.id_zona = id_zona
    self.iniciar_ui()
    self.show()
    self.llenar()


  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text()
    la = self.lat_input.text() if self.lat_input.text() != '' else None
    lo = self.lon_input.text() if self.lon_input.text() != '' else None
    if (n):
      db_man.modificar_zona(self.id_zona, n, la, lo)
      self.close()
      self.refresh_table()

  def refresh_table(self):
    self.parent.refresh()

  def borrar(self):
    reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Realmente desea borrar esta zona?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

    if reply == QtWidgets.QMessageBox.Yes:
      ManagerBase().borrar_zona(self.id_zona)
      self.close()
      self.refresh_table()

  def iniciar_ui(self):
        #labels, inputs y boton guardar
    self.setWindowTitle("Editar Zona")
    self.name_label = QtWidgets.QLabel("Nombre")
    self.name_input = QtWidgets.QLineEdit()
    self.lat_label = QtWidgets.QLabel("Latitud")
    self.lat_input = QtWidgets.QLineEdit()
    self.lon_label = QtWidgets.QLabel("Longitud")
    self.lon_input = QtWidgets.QLineEdit()
    delete_button = QtWidgets.QPushButton("Borrar")
    delete_button.clicked.connect(self.borrar)
    save_button = QtWidgets.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtWidgets.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lat_label, 1, 0)
    lay.addWidget(self.lat_input, 1, 1)
    lay.addWidget(self.lon_label, 2, 0)
    lay.addWidget(self.lon_input, 2, 1)
    lay.addWidget(save_button, 3, 1)
    self.setWindowFlags(QtCore.Qt.Window)


    self.vbox = QtWidgets.QVBoxLayout()
    self.vbox.addLayout(lay)
    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(delete_button)
    hbox.addWidget(save_button)
    self.vbox.addLayout(hbox)
    self.setLayout(self.vbox)

  def llenar(self):
    if self.id_zona:
      zona = ManagerBase().get_zona(self.id_zona)
      self.name_input.setText(str(zona.nombre if zona.nombre != None else ""))
      self.lat_input.setText(str(zona.lat if zona.lat != None else ""))
      self.lon_input.setText(str(zona.lon if zona.lon != None else ""))

class WidgetBuscarCaptura(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetBuscarCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()
    self.showMaximized()
    self.default_date_time = QtWidgets.QDateTimeEdit().dateTime()

  def refresh(self):
    self.buscar()

  def buscar(self):
    individuo_id = self.id_individuo.text() if self.id_individuo.text() != '' else None
    captura_id = self.id_captura.text() if self.id_captura.text() != '' else None
    sexo = self.sexo.items.itemText(self.sexo.items.currentIndex())
    sexo = sexo if sexo != "..." else None
    date_time_inic = self.date_time_inic.dateTime().toPython() if self.date_time_inic.dateTime() != self.default_date_time else None
    date_time_fin = self.date_time_fin.dateTime().toPython() if self.date_time_fin.dateTime() != self.default_date_time else None
    zona_id = self.zona.items.itemData(self.zona.items.currentIndex())
    zona_id = zona_id if zona_id != -1 else None
    fotografo_id = self.fotografo.items.itemData(self.fotografo.items.currentIndex())
    fotografo_id = fotografo_id if fotografo_id != -1 else None
    cant_sapitos_min = self.cant_sapitos_min.text() if self.cant_sapitos_min.text() != '' else None
    cant_sapitos_max = self.cant_sapitos_max.text() if self.cant_sapitos_max.text() != '' else None
    observaciones = self.observaciones.text() if self.observaciones.text() != '' else None
    observaciones_individuo = self.observaciones_individuo.text() if self.observaciones_individuo.text() != '' else None
    archivo = self.archivo.text() if self.archivo.text() != '' else None

    db_man = ManagerBase()
    capturas_individuos = db_man.buscar_capturas_join_individuos(individuo_id, captura_id, sexo, date_time_inic, date_time_fin, zona_id, fotografo_id,\
                         cant_sapitos_min, cant_sapitos_max, observaciones, observaciones_individuo, archivo)

    self.table.set_data(capturas_individuos)

  def iniciar_ui(self):
    vbox = QtWidgets.QVBoxLayout()
    qgridLayout = QtWidgets.QGridLayout()
    vbox.addLayout(qgridLayout)

    boton_buscar = QtWidgets.QPushButton("Buscar")
    boton_buscar.clicked.connect(self.buscar)
    vbox.addWidget(boton_buscar)

    self.table = WidgetTableCapturasIndividuosJoin(self)

    vbox.addWidget(self.table)

    db_man = ManagerBase()

    self.id_individuo = QtWidgets.QLineEdit()
    self.id_individuo.setValidator(QtGui.QIntValidator())
    self.id_captura = QtWidgets.QLineEdit()
    self.id_captura.setValidator(QtGui.QIntValidator())
    self.sexo = WidgetComboBoxList(sexo, self.parent)
    self.zona = WidgetComboBoxType(Zona, self.parent)
    self.fotografo = WidgetComboBoxType(Fotografo, self.parent)
    self.cant_sapitos_min = QtWidgets.QLineEdit()
    self.cant_sapitos_min.setValidator(QtGui.QIntValidator())
    self.cant_sapitos_max = QtWidgets.QLineEdit()
    self.cant_sapitos_max.setValidator(QtGui.QIntValidator())
    self.observaciones = QtWidgets.QLineEdit()
    self.observaciones_individuo = QtWidgets.QLineEdit()
    self.archivo = QtWidgets.QLineEdit()

    self.date_time_inic = QtWidgets.QDateTimeEdit()
    self.date_time_inic.setCalendarPopup(True)
    self.date_time_inic.setCalendarWidget(QtWidgets.QCalendarWidget())

    self.date_time_fin = QtWidgets.QDateTimeEdit()
    self.date_time_fin.setCalendarPopup(True)
    self.date_time_fin.setCalendarWidget(QtWidgets.QCalendarWidget())


    qgridLayout.addWidget(QtWidgets.QLabel("id individuo: "), 0, 0)
    qgridLayout.addWidget(self.id_individuo, 0, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("id captura: "), 0, 2)
    qgridLayout.addWidget(self.id_captura, 0, 3)
    qgridLayout.addWidget(QtWidgets.QLabel("fecha inicio: "), 0, 4)
    qgridLayout.addWidget(self.date_time_inic, 0, 5)
    qgridLayout.addWidget(QtWidgets.QLabel("fecha fin: "), 0, 6)
    qgridLayout.addWidget(self.date_time_fin, 0, 7)
    qgridLayout.addWidget(QtWidgets.QLabel("Zona: "), 1, 0)
    qgridLayout.addWidget(self.zona, 1, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Fotografo: "), 1, 2)
    qgridLayout.addWidget(self.fotografo, 1, 3)
    qgridLayout.addWidget(QtWidgets.QLabel("Sapitos acomp min: "), 1, 4)
    qgridLayout.addWidget(self.cant_sapitos_min, 1, 5)
    qgridLayout.addWidget(QtWidgets.QLabel("Sapitos acomp max: "), 1, 6)
    qgridLayout.addWidget(self.cant_sapitos_max, 1, 7)
    qgridLayout.addWidget(QtWidgets.QLabel("Observaciones: "), 2, 0)
    qgridLayout.addWidget(self.observaciones, 2, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Observaciones Individuo: "), 2, 2)
    qgridLayout.addWidget(self.observaciones_individuo, 2, 3)
    qgridLayout.addWidget(QtWidgets.QLabel("Archivo: "), 2, 4)
    qgridLayout.addWidget(self.archivo, 2, 5)
    qgridLayout.addWidget(QtWidgets.QLabel("Sexo: "), 2, 6)
    qgridLayout.addWidget(self.sexo, 2, 7)


    self.setLayout(vbox)

    self.show()

class WidgetBuscarIndividuo(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetBuscarIndividuo, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def refresh(self):
    self.buscar()

  def buscar(self):
    individuo_id = self.id_individuo.text() if self.id_individuo.text() != '' else None
    sexo = self.sexo.items.currentText()
    sexo = sexo if sexo != "..." else None
    observaciones = self.observaciones.text() if self.observaciones.text() != '' else None

    db_man = ManagerBase()
    individuos = db_man.buscar_individuos(individuo_id, sexo, observaciones)

    self.table.set_data(individuos)

  def iniciar_ui(self):
    vbox = QtWidgets.QVBoxLayout()
    qgridLayout = QtWidgets.QGridLayout()
    vbox.addLayout(qgridLayout)

    boton_buscar = QtWidgets.QPushButton("Buscar")
    boton_buscar.clicked.connect(self.buscar)
    vbox.addWidget(boton_buscar)

    self.table = WidgetTableIndividuos(self)

    vbox.addWidget(self.table)

    db_man = ManagerBase()

    self.id_individuo = QtWidgets.QLineEdit()
    self.id_individuo.setValidator(QtGui.QIntValidator())
    self.sexo = WidgetComboBoxList(sexo, self.parent)
    self.observaciones = QtWidgets.QLineEdit()

    qgridLayout.addWidget(QtWidgets.QLabel("id individuo: "), 0, 0)
    qgridLayout.addWidget(self.id_individuo, 0, 1)
    qgridLayout.addWidget(QtWidgets.QLabel("Sexo: "), 0, 2)
    qgridLayout.addWidget(self.sexo, 0, 3)
    qgridLayout.addWidget(QtWidgets.QLabel("Observaciones: "), 0, 4)
    qgridLayout.addWidget(self.observaciones, 0, 5)

    self.setLayout(vbox)

    self.show()



class WidgetFotografos(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetFotografos, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def refresh(self):
    self.table.set_data(ManagerBase().all_fotografos())

  def iniciar_ui(self):
    self.setWindowTitle("Fotografos")
    self.table = WidgetTableFotografos(self)
    self.table.set_data(ManagerBase().all_fotografos())
    self.button_nuevo = QtWidgets.QPushButton("Nuevo")
    self.button_nuevo.clicked.connect(self.launch_nuevo_fotografo)

    vbox = QtWidgets.QVBoxLayout()
    vbox.addWidget(self.table)
    vbox.addWidget(self.button_nuevo)
    self.setLayout(vbox)

  def launch_nuevo_fotografo(self):
    self.widget = WidgetAgregarFotografoRefreshTable(self)
    self.widget.show()


class WidgetZonas(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetZonas, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def refresh(self):
    self.table.set_data(ManagerBase().all_zonas())

  def iniciar_ui(self):
    self.setWindowTitle("Zonas")
    self.table = WidgetTableZonas(self)
    self.table.set_data(ManagerBase().all_zonas())
    self.button_nuevo = QtWidgets.QPushButton("Nuevo")
    self.button_nuevo.clicked.connect(self.launch_nueva_zona)

    vbox = QtWidgets.QVBoxLayout()
    vbox.addWidget(self.table)
    vbox.addWidget(self.button_nuevo)
    self.setLayout(vbox)

  def launch_nueva_zona(self):
    self.widget = WidgetAgregarZonaRefreshTable(self)
    self.widget.show()

class WidgetTableCapturasIndividuosJoin(WidgetTableTemplateQueryJoin):

  column_constructs = [ColumnConstruct(HeaderLabelIndex("id individuo", 0), ConstructorItemString("individuo_id"), open_window=True, widget=WidgetIndividuoConCapturas),
                      ColumnConstruct(HeaderLabelIndex("id captura", 0), ConstructorItemString("id"), open_window=True, widget=WidgetEditarCaptura),
                      ColumnConstruct(HeaderLabelIndex("sexo", 1), ConstructorItemString("sexo")),
                      ColumnConstruct(HeaderLabelIndex("fecha", 0), ConstructorItemString("fecha")),
                      ColumnConstruct(HeaderLabelIndex("zona", 0), ConstructorItemString("zona_description", replace_empty=True)),
                      ColumnConstruct(HeaderLabelIndex("lat", 0), ConstructorItemString("lat", replace_empty=True)),
                      ColumnConstruct(HeaderLabelIndex("lon", 0), ConstructorItemString("lon", replace_empty=True)),
                      ColumnConstruct(HeaderLabelIndex("fotografo", 0), ConstructorItemString("fotografo_description", replace_empty=True)),
                      ColumnConstruct(HeaderLabelIndex("archivo", 0), ConstructorItemString("nombre_imagen")),
                      ColumnConstruct(HeaderLabelIndex("orig", 0), ConstructorItemImage("imagen_original_thumbnail", width=100, height=100)),
                      ColumnConstruct(HeaderLabelIndex("seg", 0), ConstructorItemImage("imagen_segmentada", width=100, height=100)),
                      ColumnConstruct(HeaderLabelIndex("trans", 0), ConstructorItemImage("imagen_transformada", width=100, height=100)),
                      ColumnConstruct(HeaderLabelIndex("observaciones", 0, 300), ConstructorItemString("observaciones", replace_empty=True)),
                      ColumnConstruct(HeaderLabelIndex("observacones individuo", 1, 300), ConstructorItemString("observaciones", replace_empty=True))]

  size_rows = 100

class WidgetTableCapturasDeIndividuo(WidgetTableTemplate):

  column_constructs = [ColumnConstruct(HeaderLabel("id captura"), ConstructorItemString("id"), open_window=True, widget=WidgetEditarCaptura),
                      ColumnConstruct(HeaderLabel("fecha"), ConstructorItemString("fecha")),
                      ColumnConstruct(HeaderLabel("zona"), ConstructorItemString("zona_description")),
                      ColumnConstruct(HeaderLabel("lat"), ConstructorItemString("lat", replace_empty=True)),
                      ColumnConstruct(HeaderLabel("lon"), ConstructorItemString("lon", replace_empty=True)),
                      ColumnConstruct(HeaderLabel("fotografo"), ConstructorItemString("fotografo_description")),
                      ColumnConstruct(HeaderLabel("archivo"), ConstructorItemString("nombre_imagen")),
                      ColumnConstruct(HeaderLabel("observaciones", 300), ConstructorItemString("observaciones", replace_empty=True))]


class WidgetTableIndividuos(WidgetTableTemplate):

  column_constructs = [ColumnConstruct(HeaderLabel("id"), ConstructorItemString("id"), open_window=True, widget=WidgetIndividuoConCapturas),
                      ColumnConstruct(HeaderLabel("sexo"), ConstructorItemString("sexo")),
                      ColumnConstruct(HeaderLabel("observaciones", 300), ConstructorItemString("observaciones", replace_empty=True))]

class WidgetTableFotografos(WidgetTableTemplate):

  column_constructs = [ColumnConstruct(HeaderLabel("id"), ConstructorItemString("id"), open_window=True, widget=WidgetEditarFotografo),
                      ColumnConstruct(HeaderLabel("nombre"), ConstructorItemString("nombre")),
                      ColumnConstruct(HeaderLabel("apellido"), ConstructorItemString("apellido")),
                      ColumnConstruct(HeaderLabel("email"), ConstructorItemString("email"))]


class WidgetTableZonas(WidgetTableTemplate):

  column_constructs = [ColumnConstruct(HeaderLabel("id"), ConstructorItemString("id"), open_window=True, widget=WidgetEditarZona),
                      ColumnConstruct(HeaderLabel("nombre"), ConstructorItemString("nombre")),
                      ColumnConstruct(HeaderLabel("latitud"), ConstructorItemString("lat", replace_empty=True)),
                      ColumnConstruct(HeaderLabel("longitud"), ConstructorItemString("lon", replace_empty=True  ))]

class WidgetTableImagenCapturas(WidgetTableTemplate):

  column_constructs = [ColumnConstruct(HeaderLabel("id individuo"), ConstructorItemString("individuo_id"), open_window=True, widget=WidgetIndividuoConCapturas),
                      ColumnConstruct(HeaderLabel("id captura"), ConstructorItemString("id"), open_window=True, widget=WidgetEditarCaptura),
                      ColumnConstruct(HeaderLabel("imagen", 650), ConstructorItemImage("imagen_original_thumbnail_mediana", set_size_row=True))]

class WidgetComboBoxList(QtWidgets.QWidget):

  def __init__(self, list, parent = None):
    super(WidgetComboBoxList, self).__init__(parent)
    self.parent = parent
    self.list = list
    self.iniciar_ui()

  def iniciar_ui(self):
    self.items = QtWidgets.QComboBox()
    self.items.addItem("...")
    for item in self.list:
        self.items.addItem(item)
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.items)
    self.setLayout(layout)

class WidgetComboBoxType(QtWidgets.QWidget):

  def __init__(self, type, parent = None):
    super(WidgetComboBoxType, self).__init__(parent)
    self.parent = parent
    self.type = type
    self.iniciar_ui()

  def iniciar_ui(self):
    self.items = QtWidgets.QComboBox()
    self.items.addItem("...", -1)
    for item in ManagerBase().all(self.type):
        self.items.addItem(item.description(), item.id)
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.items)
    self.setLayout(layout)


class WidgetComboBoxExtensible(QtWidgets.QWidget):

  add_item_widgets = {Fotografo: WidgetAgregarFotografo,
                      Zona: WidgetAgregarZona
  }

  def __init__(self, type, parent = None):
    super(WidgetComboBoxExtensible, self).__init__(parent)
    self.parent = parent
    self.type = type
    self.iniciar_ui()

  def iniciar_ui(self):
    self.hBox = QtWidgets.QHBoxLayout()
    self.load_items()
    self.add_item_button = QtWidgets.QPushButton("+")
    self.add_item_button.clicked.connect(self.add_item)
    self.add_item_button.setMaximumWidth(30)
    self.hBox.addWidget(self.add_item_button)
    self.setLayout(self.hBox)

  def load_items(self):
    items = self.hBox.takeAt(0)
    if items != None:
      items.widget().deleteLater()
    self.items = QtWidgets.QComboBox()
    for item in ManagerBase().all(self.type):
        self.items.addItem(item.description(), item.id)
    self.hBox.insertWidget(0, self.items)

  def extend(self, element):
    self.load_items()
    self.items.setCurrentIndex(self.items.findText(element.description()))

  def add_item(self):
    self.add_item_widget = self.add_item_widgets[self.type](self.parent, widget_extend = self)
    self.add_item_widget.show()


class WidgetAgregarCapturaConBotonGuardar(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetAgregarCapturaConBotonGuardar, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()


  def iniciar_ui(self):
    qHLayout = QtWidgets.QHBoxLayout()

    self.setLayout(qHLayout)

    self.setWindowTitle("Formulario para agregar nueva captura")

    botonGuardar = QtWidgets.QPushButton("Guardar")

    self.widgetCaptura = WidgetAgregarCaptura(self.parent)

    botonGuardar.clicked.connect(self.widgetCaptura.guardar)

    qHLayout.addWidget(self.widgetCaptura)
    qHLayout.addWidget(botonGuardar)

    self.show()

class WidgetNuevaCaptura(QtWidgets.QWidget):

  def __init__(self, parent = None, position=-1):
    """
    @param parent:
    @param position: acierto del algoritmo.
                -1 implica que el algoritmo no encontro parecido
                0 implica que el algoritmo encontro el parecido en la primer posicion
                1 en la segunda posicion
                etc
    """
    super(WidgetNuevaCaptura, self).__init__(parent)
    self.parent = parent
    self.position = position
    self.iniciar_ui()

  def guardar(self):
    self.widgetAgregarCaptura.guardar()
    self.close()
    self.parent.hideUIResult()

  def iniciar_ui(self):

    qHLayout = QtWidgets.QHBoxLayout()
    self.setLayout(qHLayout)
    self.setWindowFlags(QtCore.Qt.Window)
    self.setWindowTitle("Formulario para agregar nueva captura")

    botonGuardar = QtWidgets.QPushButton("Guardar")

    self.widgetAgregarCaptura = WidgetAgregarCaptura(self.parent, self.position)
    botonGuardar.clicked.connect(self.guardar)
    qHLayout.addWidget(self.widgetAgregarCaptura)
    qHLayout.addWidget(botonGuardar)


    self.show()



class WidgetNuevoIndividuo(QtWidgets.QWidget):

  def __init__(self, parent = None):
    super(WidgetNuevoIndividuo, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def guardar(self):
    db_man = ManagerBase()
    sexo = self.sexo
    observaciones_individuo = self.texto.toPlainText()
    try:
      individuo_id = db_man.crear_individuo_ret_id(sexo, observaciones_individuo)
      self.widgetAgregarCaptura.guardar(individuo_id)
      self.close()
      self.parent.hideUIResult()
    except:
      print("error!")
      traceback.print_exc()


  def iniciar_ui(self):

    self.sexo = sexo[2]
    self.labeln = QtWidgets.QLabel("Sexo: ")
    self.labelz = QtWidgets.QLabel("Observaciones: ")
    self.radioMasculino = MyRadioButtonSexo(sexo[0], self)
    self.radioFemenino = MyRadioButtonSexo(sexo[1], self)
    self.radioNoDeterminado = MyRadioButtonSexo(sexo[2], self)
    self.radioNoDeterminado.setChecked(True)
    self.texto = QtWidgets.QTextEdit()

    qHLayout = QtWidgets.QHBoxLayout()
    qgridLayout = QtWidgets.QGridLayout()

    qHLayout.addLayout(qgridLayout)

    qgridLayout.addWidget(QtWidgets.QLabel("INDIVIDUO"), 0, 0)
    qgridLayout.addWidget(self.labeln, 1, 0)
    qgridLayout.addWidget(self.radioMasculino, 1, 1)
    qgridLayout.addWidget(self.radioFemenino, 2, 1)
    qgridLayout.addWidget(self.radioNoDeterminado, 3, 1)
    qgridLayout.addWidget(self.labelz, 4, 0)
    qgridLayout.addWidget(self.texto, 4, 1)

    self.setLayout(qHLayout)
    self.setWindowFlags(QtCore.Qt.Window)
    #self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Formulario para agregar nuevo individuo")

    botonGuardar = QtWidgets.QPushButton("Guardar")

    botonGuardar.clicked.connect(self.guardar)

    self.widgetAgregarCaptura = WidgetAgregarCaptura(self.parent)
    qHLayout.addWidget(self.widgetAgregarCaptura)
    qHLayout.addWidget(botonGuardar)


    self.show()


class WidgetArchivoConMismoNombre(QtWidgets.QWidget):

  def __init__(self, parent, nombre_imagen, capturas):
    super(WidgetArchivoConMismoNombre, self).__init__(parent, QtCore.Qt.Window)
    self.iniciar_ui(nombre_imagen, capturas)
    self.setFixedSize(800, 600)

  def iniciar_ui(self, nombre_imagen, capturas):
    message = "Ya existe una imagen con el nombre de archivo %s en la base de datos." if capturas.count() == 1 else\
              "Ya existen imagenes con el nombre de archivo %s en la base de datos."
    message_label = QtWidgets.QLabel(message % nombre_imagen)
    image_widget = WidgetTableImagenCapturas(self, capturas)

    vbox = QtWidgets.QVBoxLayout()
    vbox.addWidget(message_label)
    vbox.addWidget(image_widget)

    self.setLayout(vbox)

def main():
  app = QtWidgets.QApplication(sys.argv)
  #ex = WidgetIndividuo()
  from db import ManagerBase
  ex = WidgetListaIndividuosStandaloneScroleable(ManagerBase().all_individuos())
  ex.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
    main()
