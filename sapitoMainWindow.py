#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
from transformedWidget import *
from widget_individuo import WidgetListaIndividuosRadios, WidgetBotonesAgregarCaptura
from db import ManagerBase

import aplicar_algoritmos as algorit
import adaptationImage as adaptrImg
import sys
import cv2 as cv
import warp_image as wi
from pointsbezier import *

class WindowSapito(QtGui.QMainWindow):

    def __init__(self):
        super(WindowSapito, self).__init__()
        self.db_man = ManagerBase()
        self.initUI()

    def initUI(self):

        self.iRadioChecked = -1

        self.filename = None
        self.showFullScreen()

        self.mainLayout = QtGui.QHBoxLayout()
        selectorLayout = QtGui.QVBoxLayout()

        self.mainLayout.addLayout(selectorLayout)

        self.selectorWidget = SelectorWidget()

        selectorLayout.addWidget(self.selectorWidget)


        centralWidget = QtGui.QWidget()
        centralWidget.setGeometry(QtCore.QRect(0, 0, 800, 800))

        centralWidget.setLayout(self.mainLayout)

        self.setCentralWidget(centralWidget)

        self.createActions()
        self.createMenus()

        self.imageResult = QtGui.QLabel()
        self.imageResult.resize(300, 300)

        self.imageTransform = QtGui.QLabel()
        self.imageTransform.resize(300,300)


    def initUIResult(self):
        self.resultLayout = QtGui.QVBoxLayout()

        imageResultLayout = QtGui.QHBoxLayout()
        image2ResultLayout = QtGui.QHBoxLayout()

        self.resultLayout.addLayout(imageResultLayout)
        self.resultLayout.addLayout(image2ResultLayout)
        self.widget_listado = WidgetListaIndividuosRadios({}, self)
        self.widget_listado.resize(300, 400)

        self.widget_botones = WidgetBotonesAgregarCaptura(self)
        self.resultLayout.addWidget(self.widget_listado)
        self.resultLayout.addWidget(self.widget_botones)

        self.mainLayout.addLayout(self.resultLayout)

        imageResultLayout.addWidget(self.imageTransform)
        imageResultLayout.addWidget(self.imageResult)


    def loadImage(self, filename):

        img_cv = cv.imread(filename)
        if not(img_cv.size):
            QtGui.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return
        self.cv_img = img_cv
        self.img = QtGui.QImage(filename)
        self.img_filename = filename
        qim = adaptrImg.OpenCVImageToQImage(self.cv_img)
        if(self.filename != None):
            self.selectorWidget.reset()
        self.selectorWidget.addImage(qim)
        self.filename = filename

    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

        self.loadImage(filename)

    def transform(self):
        points = self.selectorWidget.getPoints()
        pointsDest = self.selectorWidget.getPointsDest()
        width = int(self.selectorWidget.getWidthDest())
        height = int(self.selectorWidget.getHeightDest())
        cv_dest = wi.warpImage(self.cv_img, points, pointsDest, width, height)

        qimage = adaptrImg.OpenCVImageToQImage(cv_dest)
        qimageDest = self.selectorWidget.shapeDest.getImage()

        imagen = adaptrImg.QImageToImagePIL(qimage)
        imagenResta = adaptrImg.QImageToImagePIL(qimageDest)


        imagenDiferencia = algorit.borrar(imagen, imagenResta)

        imageSeg, regiones = algorit.calcular_regiones(imagenDiferencia)
        qimageSeg = imageSeg.get_img()

        self.transformada = imagenDiferencia.get_img()
        self.segmentada = qimageSeg
        self.vector_regiones = regiones


        qimageResult = qimageSeg
        qimageResult.scaled(50, 50)

        #self.imageResult.setGeometry(QtCore.QRect(0, 0, width/2, height/2))
        self.imageResult.setPixmap(QtGui.QPixmap.fromImage(qimageSeg.scaled(150, 150)))

        qimageTransform = self.transformada
        qimageTransform.scaled(50, 50)

        #self.imageTransform.setGeometry(QtCore.QRect(0, 0, width/2, height/2))
        self.imageTransform.setPixmap(QtGui.QPixmap.fromImage(self.transformada.scaled(150, 150)))



        self.initUIResult()

        self.completar_similares(regiones)
        #self.mainLayout.addLayout(self.resultLayout)


    def completar_similares(self,regiones):
        #buscar en la bd a partir del vector generado para la imagen
        #actualizar el WidgetListaIndividuos con lo que traemos de la bd
        similares = self.db_man.similares(regiones)
        self.widget_listado = WidgetListaIndividuosRadios(similares, self)
        self.resultLayout.addWidget(self.widget_listado)


    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut="Ctrl+O", enabled=True, triggered=self.open)

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

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)

        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.resetSizeAct)
        self.viewMenu.addAction(self.rotateAct)
        """
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        """

        self.transformMenu = QtGui.QMenu("&Transform", self)
        self.transformMenu.addAction(self.transformAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.transformMenu)

    """
    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
    """
    def saveIndividuo(self, attr):
        """
        self.img.save("enbase_image.png")
        self.transformada.save("enbase_transformada.png")
        self.segmentada.save("enbase_segmentada.png")
        """
        self.db_man.crear_individuo(self.img, self.transformada, self.segmentada, self.vector_regiones, attr)

    def agregarCaptura(self, id_individuo, attr):
        self.db_man.crear_captura(id_individuo, self.img, self.transformada, self.segmentada, self.vector_regiones, attr)

def main():

    app = QtGui.QApplication(sys.argv)
    ex = WindowSapito()
    #ex = WidgetListaIndividuos({})
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
