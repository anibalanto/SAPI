#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets
from transformedWidget import *
from widget_individuo import WidgetListaIndividuosRadiosScroleable, \
  WidgetBotonesAgregarCaptura, \
  WidgetArchivoConMismoNombre, \
  WidgetAgregarFotografo, \
  WidgetZonas, \
  WidgetBuscarCaptura, \
  WidgetFotografos, \
  WidgetBuscarIndividuo
from db import ManagerBase, Fotografo, Zona
from imagen import ImagenQImage
import aplicar_algoritmos as algoritmos
import adaptationImage as adaptrImg
import sys
import cv2 as cv
import warp_image as wi
from pointsbezier import *


class WindowSapito(QtWidgets.QMainWindow):

  def __init__(self, imagen_inicial=None):
    super(WindowSapito, self).__init__()
    self.db_man = ManagerBase()
    self.initUI()
    #Para debugear, recibimos una imagen inicial, en vez de tener que abrirla desde la gui.
    if imagen_inicial is not None:
      self.loadImage(imagen_inicial)

  def initUI(self):

    #self.buttonShape = QtWidgets.QPushButton()
    #self.buttonShape.setIcon(QtWidgets.QIcon("sapito.png"))


    self.iniciadaUIResult = False
    self.iRadioChecked = -1

    self.filename = None
    self.filename_path = None

    self.mainLayout = QtWidgets.QHBoxLayout()
    selectorLayout = QtWidgets.QVBoxLayout()

    self.mainLayout.addLayout(selectorLayout)

    self.selectorWidget = SelectorWidget()

    selectorLayout.addWidget(self.selectorWidget)

    centralWidget = QtWidgets.QWidget()

    centralWidget.setLayout(self.mainLayout)

    self.setCentralWidget(centralWidget)

    self.createActions()
    self.createMenus()

    #Este widget muestra la imagen proyectada y segmentada.
    self.imageResult = QtWidgets.QLabel()
    #self.imageResult.resize(300, 300)
    self.imageResult.resize(100, 100)

    #Este widget muestra la imagen proyectada.
    self.imageTransform = QtWidgets.QLabel()
    #self.imageTransform.resize(300, 300)
    self.imageTransform.resize(100, 100)

    self.showMaximized()

  def initUIResult(self, qimage_transformada, qimage_segmentada):
    if (self.iniciadaUIResult):
      self.hideUIResult()

    self.imageTransform.setPixmap(QtGui.QPixmap.fromImage(qimage_transformada.scaled(150, 150)))
    self.imageResult.setPixmap(QtGui.QPixmap.fromImage(qimage_segmentada.scaled(150, 150)))

    self.resultLayout = QtWidgets.QVBoxLayout()
    self.imageResultLayout = QtWidgets.QHBoxLayout()

    self.resultLayout.addLayout(self.imageResultLayout)

    self.widget_botones = WidgetBotonesAgregarCaptura(self)
    self.resultLayout.addWidget(self.widget_botones)

    self.mainLayout.addLayout(self.resultLayout)

    self.imageResultLayout.addWidget(self.imageTransform)
    self.imageResultLayout.addWidget(self.imageResult)

    self.imageTransform.setVisible(True)
    self.imageResult.setVisible(True)

    self.iniciadaUIResult = True


  def hideUIResult(self):
    resultLayout = self.mainLayout.takeAt(1)
    if resultLayout:
      resultLayout.deleteLater()

      image1 = self.imageResultLayout.takeAt(1)
      image2 = self.imageResultLayout.takeAt(0)
      image1.widget().setVisible(False)
      image2.widget().setVisible(False)

      self.widget_listado.deleteLater()
      self.widget_botones.deleteLater()

      self.iniciadaUIResult = False

      self.selectorWidget.resetShape()

  def loadImage(self, filename):
    self.filename = filename

    self.cv_img = cv.imread(self.filename, cv.IMREAD_IGNORE_ORIENTATION | cv.IMREAD_COLOR) # Abrimos la imagen con opencv
    self.q_img = QtGui.QImage(self.filename) # Abrimos la imagen con qt

    if not (self.cv_img.any() and self.cv_img.size):
        QtWidgets.QMessageBox.information(self, "Image Viewer", "Error al cargar la imagen %s." % filename)
    else:
      if (self.filename != None):
        self.selectorWidget.reset()
        if (self.iniciadaUIResult):
          self.hideUIResult()
      self.selectorWidget.addImage(self.q_img)
      self.setWindowTitle(self.filename)
    self.filename_nopath = self.filename.split("/")[-1]
    self.filename_path = self.filename[:-len(self.filename_nopath) - 1]
    self.verificar_nombre_imagen(self.filename_nopath)

  def verificar_nombre_imagen(self, nombre_imagen):
    db_man = ManagerBase()
    capturas = db_man.get_captura_por_nombre_imagen(nombre_imagen)
    if capturas.count() > 0:
      self.widget = WidgetArchivoConMismoNombre(self, nombre_imagen, capturas)
      #self.hide()
      self.widget.show()
      #self.widget.activateWindow()


  def open(self):
    path = QtCore.QDir.currentPath() if self.filename_path == None else QtCore.QDir.absolutePath(
      QtCore.QDir(self.filename_path))
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", path)
    if filename:
      self.loadImage(filename)

  def transform(self):
    """
        Aplicamos la transformacion a la region seleccionada y llenamos la lista de similares.
        """
    points = self.selectorWidget.getPoints() # Los puntos que marco el usuario.
    pointsDest = self.selectorWidget.getPointsDest() # Los puntos a los que va la proyeccion.
    width = int(self.selectorWidget.getWidthDest()) # Ancho bounding box destino.
    height = int(self.selectorWidget.getHeightDest()) # Alto bounding box destino.

    #Imagen proyectada en cv y en qt.
    cv_dest = wi.warpImage(self.cv_img, points, pointsDest, width, height)
    qimage_proyectada = adaptrImg.OpenCVImageToQImage(cv_dest)

    #Crea imagen de la forma destino con blanco adentro y negro afuera.
    #Esta imagen la vamos a usar para borrar lo que no queremos de la proyectada.
    #Es como un crop.
    qimage_resta = self.selectorWidget.shapeDest.getImage()

    #A la proyectada le sacamos lo que no queremos.
    #Por ahora pasamos las imagenes en el wrapper
    proy = ImagenQImage()
    proy.from_instance(qimage_proyectada)
    segm = ImagenQImage()
    segm.from_instance(qimage_resta)
    self.qimage_transformada = algoritmos.borrar(proy, segm).get_img()

    #Obtenemos la segmentada y el vector de regiones a partir de la resta que hicimos antes.
    #Por ahora pasamos las imagenes en el wrapper
    trans = ImagenQImage()
    trans.from_instance(self.qimage_transformada)
    imagen_wrapper, self.vector_regiones, self.superficie_ocupada = algoritmos.calcular_regiones(trans)

    self.qimage_segmentada  = imagen_wrapper.get_img() # Sacamos la imagen del wrapper.

    #Cargamos los widgets de la barra de costado con las imagenes obtenidas.
    self.initUIResult(self.qimage_transformada, self.qimage_segmentada)

    self.completar_similares(self.vector_regiones)


  def resetShape(self):
    self.selectorWidget.resetShape()
    self.hideUIResult()


  def completar_similares(self, regiones):
    #buscar en la bd a partir del vector generado para la imagen
    #actualizar el WidgetListaIndividuos con lo que traemos de la bd
    similares = self.db_man.similares(regiones)
    self.widget_listado = WidgetListaIndividuosRadiosScroleable(similares, self)
    self.resultLayout.addWidget(self.widget_listado)

  def individuos(self):
    """
    Llamamos al widget que muestra todos los individuos.
    Este metodo se llama desde la barra de menu.
    """
    self.widget_individuos = WidgetBuscarIndividuo()
    self.widget_individuos.show()
    #self.lista_individuos = WidgetListaIndividuosStandaloneScroleable(ManagerBase().all_individuos())
    #self.lista_individuos.show()

  def add_photographer(self):
    """
      Muestra el widget a usar para agregar un Fotografo
      """
    self.add_photographer_widget = WidgetAgregarFotografo()
    #self.add_photographer_widget.show()

  def capturas(self):
    """
      Llamamos al widget que muesstra el formulario de busqueda,
      este meotodo se llama desde la barra de menu.
      """
    self.search_widget = WidgetBuscarCaptura()
    self.search_widget.show()

  def fotografos(self):
    """
      Llamamos al widget que muesstra el formulario de busqueda,
      este meotodo se llama desde la barra de menu.
      """
    self.search_widget = WidgetFotografos()
    self.search_widget.show()

  def zonas(self):
    """
      Llamamos al widget que muesstra el formulario de busqueda,
      este meotodo se llama desde la barra de menu.
      """
    self.search_widget = WidgetZonas()
    self.search_widget.show()

  def createActions(self):
    self.openAct = QtWidgets.QAction("Abrir Imagen", self,
                                 shortcut="Ctrl+A", enabled=True, triggered=self.open)
    self.exitAct = QtWidgets.QAction("Salir", self, shortcut="Ctrl+Q",
                                 triggered=self.close)
    self.zoomOutAct = QtWidgets.QAction("Zoom -", self,
                                    shortcut="Ctrl+-", enabled=True, triggered=self.selectorWidget.zoomOut)
    self.zoomInAct = QtWidgets.QAction("Zoom +", self,
                                   shortcut="Ctrl++", enabled=True, triggered=self.selectorWidget.zoomIn)
    self.resetSizeAct = QtWidgets.QAction("Original", self,
                                      shortcut="Ctrl+O", enabled=True, triggered=self.selectorWidget.resetSizeImage)
    self.rotateAct = QtWidgets.QAction("&Rotar Imagen", self,
                                   shortcut="Ctrl+R", enabled=True, triggered=self.selectorWidget.rotateImage)
    self.transformAct = QtWidgets.QAction("&Transformar", self,
                                      shortcut="Ctrl+T", enabled=True, triggered=self.transform)
    self.resetShapeAct = QtWidgets.QAction("&Resetear", self,
                                    shortcut="Ctrl+E", enabled=True, triggered=self.resetShape)
    #self.add_photographer_act = QtWidgets.QAction("Agregar &fotografo", self, shortcut="Ctrl+F", enabled=True, triggered=self.add_photographer)
    self.individuos_act = QtWidgets.QAction("Individuos", self, triggered=self.individuos)
    self.capturas_act = QtWidgets.QAction("Capturas", self, enabled=True, triggered=self.capturas)
    self.fotografos_act = QtWidgets.QAction("Fotografos", self, enabled=True, triggered=self.fotografos)
    self.zonas_act = QtWidgets.QAction("Zonas", self, enabled=True, triggered=self.zonas)

  def createMenus(self):
    self.fileMenu = QtWidgets.QMenu("&Archivo", self)
    self.fileMenu.addAction(self.openAct)
    self.fileMenu.addSeparator()
    self.fileMenu.addAction(self.exitAct)

    self.datosMenu = QtWidgets.QMenu("&Datos", self)
    self.datosMenu.addAction(self.individuos_act)
    self.datosMenu.addAction(self.capturas_act)
    self.datosMenu.addAction(self.fotografos_act)
    self.datosMenu.addAction(self.zonas_act)

    self.viewMenu = QtWidgets.QMenu("&Vista", self)
    self.viewMenu.addAction(self.zoomInAct)
    self.viewMenu.addAction(self.zoomOutAct)
    self.viewMenu.addAction(self.resetSizeAct)
    self.viewMenu.addAction(self.rotateAct)

    self.transformMenu = QtWidgets.QMenu("&Forma", self)
    self.transformMenu.addAction(self.transformAct)
    self.transformMenu.addAction(self.resetShapeAct)

    self.menuBar().addMenu(self.fileMenu)
    self.menuBar().addMenu(self.datosMenu)
    self.menuBar().addMenu(self.viewMenu)
    self.menuBar().addMenu(self.transformMenu)

  #    def saveIndividuo(self, attr):
  #        self.db_man.crear_individuo(self.q_img, self.qimage_transformada, self.qimage_segmentada, self.vector_regiones, attr)

  #    def agregarCaptura(self, id_individuo, attr):
  #        self.db_man.crear_captura(id_individuo, self.q_img, self.qimage_transformada, self.qimage_segmentada, self.vector_regiones, attr)

  def getPoints(self):
    return self.selectorWidget.getPoints()

  def getAngles(self):
    return self.selectorWidget.getAngles()

  def getLarges(self):
    return self.selectorWidget.getLarges()


def main():
  app = QtWidgets.QApplication(sys.argv)
  try:
    ex = WindowSapito(sys.argv[1])
  except:
    ex = WindowSapito()
  ex.show()
  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
