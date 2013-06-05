# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form, width, height):
        Form.setObjectName("Form")
        Form.resize(width, height)
        self.imageLabel = QtGui.QLabel(Form)
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, width, height))
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")

        #self.saveButton = QtGui.Button()

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setImage(self, image):
     self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))


