# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transformedWidget.ui'
#
# Created: Tue May 28 11:19:48 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form, width, height):
        Form.setObjectName("Form")
        Form.resize(width, height+200)
        self.imageLabel = QtGui.QLabel(Form)
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, width, height))
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))

    def setImage(self, image):
	 self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))


