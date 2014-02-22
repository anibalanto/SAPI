#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
from transformedWidget import *
from widget_individuo import WidgetListaIndividuosRadiosScroleable, \
    WidgetBotonesAgregarCaptura, \
    WidgetListaIndividuosStandaloneScroleable, \
    WidgetAgregarFotografo
from db import ManagerBase
from imagen import ImagenQImage
import aplicar_algoritmos as algoritmos
import adaptationImage as adaptrImg
import sys
import cv2 as cv
import warp_image as wi
from pointsbezier import *

class WindowSapito(QtGui.QMainWindow):

    def __init__(self, imagen_inicial=None):
        super(WindowSapito, self).__init__()
        self.db_man = ManagerBase()
        self.initUI()
        #Para debugear, recibimos una imagen inicial, en vez de tener que abrirla desde la gui.
        if imagen_inicial is not None:
          self.loadImage(imagen_inicial)

    def initUI(self):

        #self.buttonShape = QtGui.QPushButton()
        #self.buttonShape.setIcon(QtGui.QIcon("sapito.png"))


        self.iniciadaUIResult = False
        self.iRadioChecked = -1

        self.filename = None

        self.mainLayout = QtGui.QHBoxLayout()
        selectorLayout = QtGui.QVBoxLayout()

        self.mainLayout.addLayout(selectorLayout)

        self.selectorWidget = SelectorWidget()

        selectorLayout.addWidget(self.selectorWidget)

        centralWidget = QtGui.QWidget()

        centralWidget.setLayout(self.mainLayout)

        self.setCentralWidget(centralWidget)

        self.createActions()
        self.createMenus()

        #Este widget muestra la imagen proyectada y segmentada.
        self.imageResult = QtGui.QLabel()
        #self.imageResult.resize(300, 300)
        self.imageResult.resize(100, 100)

        #Este widget muestra la imagen proyectada.
        self.imageTransform = QtGui.QLabel()
        #self.imageTransform.resize(300, 300)
        self.imageTransform.resize(100, 100)

        self.showMaximized()

    def initUIResult(self, qimage_transformada, qimage_segmentada):
        if (self.iniciadaUIResult):
            self.hideUIResult()

        self.imageTransform.setPixmap(QtGui.QPixmap.fromImage(qimage_transformada.scaled(150, 150)))
        self.imageResult.setPixmap(QtGui.QPixmap.fromImage(qimage_segmentada.scaled(150, 150)))

        self.resultLayout = QtGui.QVBoxLayout()
        self.imageResultLayout = QtGui.QHBoxLayout()

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
        resultLayout.deleteLater()

        image1 = self.imageResultLayout.takeAt(1)
        image2 = self.imageResultLayout.takeAt(0)
        image1.widget().setVisible(False)
        image2.widget().setVisible(False)

        self.widget_listado.deleteLater()
        self.widget_botones.deleteLater()

        self.iniciadaUIResult = False

    def loadImage(self, filename):
        self.filename = filename

        self.cv_img  = cv.imread(self.filename) # Abrimos la imagen con opencv
        self.q_img = QtGui.QImage(self.filename) # Abrimos la imagen con qt

        if not(self.cv_img.any() and self.cv_img.size):
            QtGui.QMessageBox.information(self, "Image Viewer", "Error al cargar la imagen %s." % filename)
        else:
            if(self.filename != None):
                self.selectorWidget.reset()
                if (self.iniciadaUIResult):
                    self.hideUIResult()
            self.selectorWidget.addImage(self.q_img)
            self.setWindowTitle(self.filename)


    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

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

        #Obtenemos la segemntada y el vector de regiones a partir de la resta que hicimos antes.
        #Por ahora pasamos las imagenes en el wrapper
        trans = ImagenQImage()
        trans.from_instance(self.qimage_transformada)
        imagen_wrapper, self.vector_regiones = algoritmos.calcular_regiones(trans)
        self.qimage_segmentada  = imagen_wrapper.get_img() # Sacamos la imagen del wrapper.

        #Cargamos los widgets de la barra de costado con las imagenes obtenidas.
        self.initUIResult(self.qimage_transformada, self.qimage_segmentada)

        self.completar_similares(self.vector_regiones)

    def completar_similares(self, regiones):
        #buscar en la bd a partir del vector generado para la imagen
        #actualizar el WidgetListaIndividuos con lo que traemos de la bd
        similares = self.db_man.similares(regiones)
        self.widget_listado = WidgetListaIndividuosRadiosScroleable(similares, self)
        self.resultLayout.addWidget(self.widget_listado)

    def view_all(self):
        """
        Llamamos al widget que muestra todos los individuos.
        Este metodo se llama desde la barra de menu.
        """
        self.lista_individuos = WidgetListaIndividuosStandaloneScroleable(ManagerBase().all_individuos())
        self.lista_individuos.show()

    def add_photographer(self):
      """
      Muestra el widget a usar para agregar un Fotografo
      """
      self.add_photographer_widget = WidgetAgregarFotografo()
      self.add_photographer_widget.show()


    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut="Ctrl+O", enabled=True, triggered=self.open)
        self.view_all_act = QtGui.QAction("&View All", self, triggered=self.view_all)
        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
        self.zoomOutAct = QtGui.QAction("Zoom &Out", self,
                shortcut="Ctrl+-", enabled=True, triggered=self.selectorWidget.zoomOut)
        self.zoomInAct = QtGui.QAction("Zoom &In", self,
                shortcut="Ctrl++", enabled=True, triggered=self.selectorWidget.zoomIn)
        self.resetSizeAct = QtGui.QAction("Reset Size", self,
                shortcut="Ctrl+0", enabled=True, triggered=self.selectorWidget.resetSizeImage)
        self.rotateAct = QtGui.QAction("&Rotate", self,
                shortcut="Ctrl+R", enabled=True, triggered=self.selectorWidget.rotateImage)
        self.transformAct = QtGui.QAction("&Transform", self,
                shortcut="Ctrl+T", enabled=True, triggered=self.transform)
        self.add_photographer_act = QtGui.QAction("Add Photographer", self, enabled=True, triggered=self.add_photographer)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.view_all_act)
        self.fileMenu.addAction(self.add_photographer_act)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.resetSizeAct)
        self.viewMenu.addAction(self.rotateAct)

        self.transformMenu = QtGui.QMenu("&Transform", self)
        self.transformMenu.addAction(self.transformAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.transformMenu)

    def saveIndividuo(self, attr):
        self.db_man.crear_individuo(self.q_img, self.qimage_transformada, self.qimage_segmentada, self.vector_regiones, attr)

    def agregarCaptura(self, id_individuo, attr):
        self.db_man.crear_captura(id_individuo, self.q_img, self.qimage_transformada, self.qimage_segmentada, self.vector_regiones, attr)

def main():
    app = QtGui.QApplication(sys.argv)
    try:
      ex = WindowSapito(sys.argv[1])
    except:
      ex = WindowSapito()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
