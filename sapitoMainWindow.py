#!/usr/bin/python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
from transformedWidget import *

import aplicar_algoritmos as algorit
import adaptationImage as adaptrImg
import sys
import cv2 as cv
import warp_image as wi
from pointsbezier import *

class WindowSapito(QtGui.QMainWindow):

    def __init__(self):
        super(WindowSapito, self).__init__()

        self.initUI()

    def initUI(self):

        self.filename = None
        self.resize(1024, 800)

        mainLayout = QtGui.QHBoxLayout()
        selectorLayout = QtGui.QVBoxLayout()
        resultLayout = QtGui.QVBoxLayout()

        imageResultLayout = QtGui.QHBoxLayout()
        listResultLayout = QtGui.QHBoxLayout()

        resultLayout.addLayout(imageResultLayout)
        resultLayout.addLayout(listResultLayout)

        mainLayout.addLayout(selectorLayout)
        mainLayout.addLayout(resultLayout)

        self.selectorWidget = SelectorWidget()
        self.imageResult = QtGui.QLabel()

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

        #coords = self.selectorWidget.boundingRect().getCoords()
        #pixmap = QtGui.QPixmap.grabWidget(self.selectorWidget, coords[0],
            #coords[1], coords[2], coords[3])
        #pixmap.save("pixmap.png")

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

        imageSeg = algorit.probar_areas_regiones(imagenDiferencia)
        #imagenDiferencia.save(self.filename+"transofrmada.jpg")
        #imagenDiferencia.show()

        qimageSeg = adaptrImg.ImagePILToQImage(imageSeg)

        self.imageResult.setGeometry(QtCore.QRect(0, 0, width, height))
        self.imageResult.setPixmap(QtGui.QPixmap.fromImage(qimageSeg))

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

def main():

    app = QtGui.QApplication(sys.argv)
    ex = WindowSapito()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()