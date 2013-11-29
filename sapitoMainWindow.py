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

        hlayout = QtGui.QHBoxLayout()
        vlayout1 = QtGui.QVBoxLayout()
        vlayout2 = QtGui.QVBoxLayout()

        hlayout.addLayout(vlayout1)
        hlayout.addLayout(vlayout2)

        self.selectorWidget = SelectorWidget()

        vlayout1.addWidget(self.selectorWidget)
        vlayout2.addWidget(QtGui.QLabel("hola"))

        centralWidget = QtGui.QWidget()
        centralWidget.setGeometry(QtCore.QRect(0, 0, 800, 800))

        centralWidget.setLayout(hlayout)

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

        coords = self.selectorWidget.boundingRect().getCoords()
        pixmap = QtGui.QPixmap.grabWidget(self.selectorWidget, coords[0],
            coords[1], coords[2], coords[3])
        pixmap.save("pixmap.png")

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

        imagenDiferencia.save(self.filename+"transofrmada.jpg")
        imagenDiferencia.show()

        if hasattr(self, 'transWidget'):
            self.transObjet.setImage(qimage, self.img_filename)
            self.transWidget.show()
        else:
            self.transWidget = QtGui.QWidget()
            self.transObjet = Ui_Form()
            self.transObjet.setupUi(self.transWidget, width, height)
            self.transObjet.setImage(qimage, self.img_filename)
            self.transWidget.show()

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut="Ctrl+O", enabled=True, triggered=self.open)

        #self.exitAct = QtGui.QAction("E&xit", self.centralwidget, shortcut="Ctrl+Q",
         #       triggered=self.close)

        self.zoomOutAct = QtGui.QAction("Zoom &Out", self,
                shortcut="Ctrl+-", enabled=True, triggered=self.selectorWidget.zoomOut)

        self.zoomInAct = QtGui.QAction("Zoom &In", self,
                shortcut="Ctrl++", enabled=True, triggered=self.selectorWidget.zoomIn)

        self.resetSizeAct = QtGui.QAction("&Reset Size", self,
                shortcut="Ctrl+R", enabled=True, triggered=self.selectorWidget.resetSizeImage)

        """
        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)
        """
        self.transformAct = QtGui.QAction("&Transform", self,
                shortcut="Ctrl+T", enabled=True, triggered=self.transform)

    """
    def dictToList(self, mydict):
        mylist = []
        for i in range(0,4):
            mylist.append(mydict[i])
        return mylist
    """

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        """
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        """
        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.resetSizeAct)
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
    """
    def scaleImage(self, factor):
        self.scaleFactor *= factor
        print self.scaleFactor
        print self.scaleFactor * self.imageLabel.pixmap().size()
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.1)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

    def clickLabel(self, x, y):
        if self.i == 4:
            self.points = {}
            self.i = 0
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.img))

        self.points[self.i] = (int(x/self.scaleFactor),int(y/self.scaleFactor))
        print self.points
        if self.i != 0:
            self.update()

        self.i += 1

        self.transformAct.setEnabled(self.i == 4)


    def paintEvent(self, event):
        if self.i != 0:
            painter = QtGui.QPainter()
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            painter.begin(self.imageLabel.pixmap())
            painter.setPen(pen)
            painter.drawLine(self.points[self.i-2][0], self.points[self.i-2][1], self.points[self.i-1][0], self.points[self.i-1][1])
            if self.i == 4:
                painter.drawLine(self.points[self.i-1][0], self.points[self.i-1][1], self.points[0][0], self.points[0][1])
            painter.end()
            self.imageLabel.refresh()

    """

def main():

    app = QtGui.QApplication(sys.argv)
    ex = WindowSapito()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()