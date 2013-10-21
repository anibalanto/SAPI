#!/usr/bin/env python

from PySide import QtCore, QtGui
from transformedWidget import *

import aplicar_algoritmos as algorit
import adaptationImage as adaptrImg
import sys
import cv2 as cv
import warp_image as wi
from pointsbezier import *


class ImageViewer(object):
    def setupUi(self, MainWindow, filename):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 1024, 768))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1022, 766))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")


        self.selectorWidget = SelectorWidget(self.scrollAreaWidgetContents, filename)
        self.selectorWidget.setGeometry(QtCore.QRect(0, 0, 800, 600))
        self.selectorWidget.setObjectName("selectorWidget")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1024, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.selectorWidget.clicked.connect(self.selectorWidget.clickSelector)

        self.loadImage(filename)
        self.createActions(MainWindow)
        self.createMenus(MainWindow)
        """
        if filename:
            self.loadImage(filename)
            self.img_filename = filename

            self.fitToWindowAct.setEnabled(True)
            #self.fitToWindowAct.setChecked(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

        self.fitToWindowAct.setEnabled(True)
        """
        #self.updateActions()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

    def loadImage(self, filename):
        img_cv = cv.imread(filename)
        if not(img_cv.size):
            QtGui.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return
        self.cv_img = img_cv
        self.img = QtGui.QImage(filename)
        self.img_filename = filename
        qim = adaptrImg.OpenCVImageToQImage(self.cv_img)
        self.selectorWidget.addImage(qim)
        #self.scaleImage(self.size().width()/self.img.size().width())
        #print "en loadImage:", self.imageLabel.size()

    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

        self.loadImage(filename)


        self.fitToWindowAct.setEnabled(True)
        #self.updateActions()

        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()
    """
    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.scaleFactor = 1.0
        self.scaleImage(self.size().width()/self.img.size().width())
        #self.imageLabel.adjustSize()

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()
    """
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
        algorit.probar_dimension_fractal(adaptrImg.QImageToImagePIL(qimage))

        #qimageShapeDest = self.selectorWidget.imageShapeDest()
        #adaptrImg.QImageToImagePIL(qimageShapeDest).show()

        if hasattr(self, 'transWidget'):
            self.transObjet.setImage(qimage, self.img_filename)
            self.transWidget.show()
        else:
            self.transWidget = QtGui.QWidget()
            self.transObjet = Ui_Form()
            self.transObjet.setupUi(self.transWidget, width, height)
            self.transObjet.setImage(qimage, self.img_filename)
            self.transWidget.show()

    def createActions(self, mainWindow):
        self.openAct = QtGui.QAction("&Open...", mainWindow, shortcut="Ctrl+O",
                triggered=self.open)

        #self.exitAct = QtGui.QAction("E&xit", self.centralwidget, shortcut="Ctrl+Q",
         #       triggered=self.close)

        """
        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)
        """
        self.transformAct = QtGui.QAction("&Transform", mainWindow,
                shortcut="Ctrl+T", enabled=True, triggered=self.transform)

    def dictToList(self, mydict):
        mylist = []
        for i in range(0,4):
            mylist.append(mydict[i])
        return mylist

    def createMenus(self, mainWindow):
        self.fileMenu = QtGui.QMenu("&File", mainWindow)

        self.fileMenu.addAction(self.openAct)
        """
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        """
        """
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        """

        self.transformMenu = QtGui.QMenu("&Transform", self.centralwidget)
        self.transformMenu.addAction(self.transformAct)

        mainWindow.menuBar().addMenu(self.fileMenu)
        #self.menuBar().addMenu(self.viewMenu)
        mainWindow.menuBar().addMenu(self.transformMenu)

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

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QMainWindow()
    imageViewer = ImageViewer()
    imageViewer.setupUi(mainWindow, sys.argv[1])
    mainWindow.show()
    sys.exit(app.exec_())
