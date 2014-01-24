#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
from transformedWidget import *
from widget_individuo import WidgetListaIndividuosRadiosScroleable, WidgetBotonesAgregarCaptura, WidgetListaIndividuosStandaloneScroleable
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
        self.resize(1024, 800)

        mainLayout = QtGui.QHBoxLayout()
        selectorLayout = QtGui.QVBoxLayout()
        self.resultLayout = QtGui.QVBoxLayout()

        imageResultLayout = QtGui.QHBoxLayout()

        self.resultLayout.addLayout(imageResultLayout)
        self.widget_listado = WidgetListaIndividuosRadiosScroleable({}, self)
        self.widget_listado.resize(300, 400)

        self.widget_botones = WidgetBotonesAgregarCaptura(self)
        self.resultLayout.addWidget(self.widget_listado)
        self.resultLayout.addWidget(self.widget_botones)

        mainLayout.addLayout(selectorLayout)
        mainLayout.addLayout(self.resultLayout)

        self.selectorWidget = SelectorWidget()
        self.imageResult = QtGui.QLabel()
        self.imageResult.resize(300, 300)

        selectorLayout.addWidget(self.selectorWidget)
        imageResultLayout.addWidget(self.imageResult)

        centralWidget = QtGui.QWidget()
        centralWidget.setGeometry(QtCore.QRect(0, 0, 800, 800))

        centralWidget.setLayout(mainLayout)

        self.setCentralWidget(centralWidget)

        self.createActions()
        self.createMenus()

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

        print type(imageSeg)

        self.imageResult.setGeometry(QtCore.QRect(0, 0, width, height))
        self.imageResult.setPixmap(QtGui.QPixmap.fromImage(qimageSeg))

        self.completar_similares(regiones)

        #print type(imagenDiferencia)

        self.transformada = imagenDiferencia.get_img()
        self.segmentada = qimageSeg
        self.vector_regiones = regiones


    def completar_similares(self,regiones):
        #buscar en la bd a partir del vector generado para la imagen
        #actualizar el WidgetListaIndividuos con lo que traemos de la bd
        similares = self.db_man.similares(regiones)
        self.widget_listado = WidgetListaIndividuosRadiosScroleable(similares, self)
        self.resultLayout.addWidget(self.widget_listado)


    def view_all(self):
        self.lista_individuos = WidgetListaIndividuosStandaloneScroleable(ManagerBase().all_individuos())
        self.lista_individuos.show()

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut="Ctrl+O", enabled=True, triggered=self.open)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.view_all_act = QtGui.QAction("&View All", self, triggered=self.view_all)

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
        self.fileMenu.addAction(self.view_all_act)

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
    def save(self, attr):
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
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
