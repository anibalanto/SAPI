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
        MainWindow.resize(1024, 800)

        hlayout = QtGui.QHBoxLayout()
        vlayout1 = QtGui.QVBoxLayout()
        vlayout2 = QtGui.QVBoxLayout()

        hlayout.addLayout(vlayout1)
        hlayout.addLayout(vlayout2)

        MainWindow.setLayout(hlayout)
        MainWindow.addWidget(QtGui.QLabel("hola1"))

        scrollAreaWidgetContents = QtGui.QWidget()
        scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1022, 798))
        #scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        selectorWidget = SelectorWidget(scrollAreaWidgetContents)
        selectorWidget.setGeometry(QtCore.QRect(0, 0, 800, 800))

        vlayout1.addWidget(selectorWidget)
        vlayout1.addWidget(QtGui.QLabel("hola"))


        #MainWindow.setCentralWidget()
        """
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 1024, 800))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1022, 798))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")


        self.selectorWidget = SelectorWidget(self.scrollAreaWidgetContents)
        self.selectorWidget.setGeometry(QtCore.QRect(0, 0, 800, 800))
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

        self.selectorWidget.scene().clicked.connect(self.selectorWidget.scene().clickSelector)


        self.loadImage(filename)
        self.createActions(MainWindow)
        self.createMenus(MainWindow)
        """

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

    def loadImage(self, filename):
        self.filename = filename
        img_cv = cv.imread(filename)
        if not(img_cv.size):
            QtGui.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return
        self.cv_img = img_cv
        self.img = QtGui.QImage(filename)
        self.img_filename = filename
        qim = adaptrImg.OpenCVImageToQImage(self.cv_img)
        self.reset()
        self.selectorWidget.addImage(qim)

    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self.centralwidget, "Open File",
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

    def createActions(self, mainWindow):
        self.openAct = QtGui.QAction("&Open...", mainWindow,
                shortcut="Ctrl+O", enabled=True, triggered=self.open)

        #self.exitAct = QtGui.QAction("E&xit", self.centralwidget, shortcut="Ctrl+Q",
         #       triggered=self.close)

        """
        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", mainWindow,
                shortcut="Ctrl++", enabled=True, triggered=self.selectorWidget.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", mainWindow,
                shortcut="Ctrl+-", enabled=True, triggered=self.selectorWidget.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", mainWindow,
                shortcut="Ctrl+S", enabled=True, triggered=self.selectorWidget.normalSize)
        """
        """
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
        """
        """
        self.viewMenu = QtGui.QMenu("&View", mainWindow)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        #self.viewMenu.addAction(self.normalSizeAct)
        """
        """
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        """

        self.transformMenu = QtGui.QMenu("&Transform", self.centralwidget)
        self.transformMenu.addAction(self.transformAct)

        mainWindow.menuBar().addMenu(self.fileMenu)
        #mainWindow.menuBar().addMenu(self.viewMenu)
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
