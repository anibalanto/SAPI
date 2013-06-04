#!/usr/bin/env python

#############################################################################
##
## Copyright (C) 2005-2005 Trolltech AS. All rights reserved.
##
## This file is part of the example classes of the Qt Toolkit.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http://www.trolltech.com/products/qt/opensource.html
##
## If you are unsure which license is appropriate for your use, please
## review the following information:
## http://www.trolltech.com/products/qt/licensing.html or contact the
## sales department at sales@trolltech.com.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#############################################################################

from PySide import QtCore, QtGui
from collections import namedtuple
from transformedWidget import *

import sys
import cv2 as cv
import numpy
import warp_image as wi


class Communicate(QtCore.QObject):
    
    mouseClick = QtCore.Signal()

class ImageViewer(QtGui.QMainWindow):
    WIDHT_DEST = 600
    HEIGHT_DEST = 600
    points = {}
    points_dest = {0: (0,0), 1: (WIDHT_DEST,0), 2: (WIDHT_DEST,HEIGHT_DEST), 3: (0,HEIGHT_DEST)} 
    i = 0
    def __init__(self, filename):
        super(ImageViewer, self).__init__()

        self.printer = QtGui.QPrinter()
        self.scaleFactor = 1.0

        self.imageLabel = LabelImage()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.imageLabel.imageClicked.connect(self.clickLabel)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.setWindowTitle("Image Viewer")
        self.resize(800, 600)

        self.createActions()
        self.createMenus()

        if filename:
            self.loadImage(filename)
            
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self.updateActions()

    def loadImage(self, filename):
        if filename:
            img_cv = cv.imread(filename)
            if not(img_cv.size):
                QtGui.QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % filename)
                return

        self.cv_img = img_cv
        self.img = QtGui.QImage(filename)
        qim = self.openCVtoQImage(self.cv_img)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(qim))

    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())

        self.loadImage(filename)

        self.scaleFactor = 1.0

        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self.updateActions()

        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()

    def about(self):
        QtGui.QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def transform(self):
        cv_dest = wi.warpImage(self.cv_img, self.dictToList(self.points), self.dictToList(self.points_dest), self.WIDHT_DEST, self.HEIGHT_DEST) 

        if hasattr(self,'transWidget'):
            self.transObjet.setImage(self.openCVtoQImage(cv_dest))
            self.transWidget.show()
        else:
            self.transWidget = QtGui.QWidget()
            self.transObjet = Ui_Form()
            self.transObjet.setupUi(self.transWidget, self.WIDHT_DEST, self.HEIGHT_DEST)
            self.transObjet.setImage(self.openCVtoQImage(cv_dest))
            self.transWidget.show()

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.transformAct = QtGui.QAction("&Transform", self,
                shortcut="Ctrl+T", enabled=False, triggered=self.transform)

    def dictToList(self, mydict):
        mylist = []
        for i in range(0,4):
            mylist.append(mydict[i])
        return mylist

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.transformMenu = QtGui.QMenu("&Transform", self)
        self.transformMenu.addAction(self.transformAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)
        self.menuBar().addMenu(self.transformMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))

    def clickLabel(self, x, y):
        if self.i == 4:
            self.points = {}
            self.i = 0
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.img))

        self.points[self.i] = (x,y)

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
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.imageLabel.pixmap().toImage()))


    def openCVtoQImage(self, img_cv):

        dst = cv.cvtColor(img_cv, cv.COLOR_BGR2RGB)
        h = dst.shape[0]
        w = dst.shape[1]
        qim = QtGui.QImage(dst.data, w, h, dst.strides[0], QtGui.QImage.Format_RGB888)
        return qim.copy()


class LabelImage(QtGui.QLabel):

    imageClicked = QtCore.Signal(int,int)

    def __init__(self):
        super(LabelImage, self).__init__()

    def mousePressEvent(self, event):
	self.imageClicked.emit(event.x(),event.y())

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    if len(sys.argv) == 2:
        imageViewer = ImageViewer(sys.argv[1])
    else:
        imageViewer = ImageViewer(None)
    imageViewer.show()
    sys.exit(app.exec_())
