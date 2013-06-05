# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import re

class Ui_Form(object):
    def setupUi(self, Form, width, height):
        Form.setObjectName("Form")
        Form.resize(width, height)
        self.imageLabel = QtGui.QLabel(Form)
        self.imageLabel.setGeometry(QtCore.QRect(0, 0, width, height))
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")

        self.save_button = QtGui.QPushButton("Guardar imagen", Form)
        self.save_button.clicked.connect(self.on_save_button_clicked)

        #El nombre de archivo que vamos a usar para guardar la imagen transformada.
        self.img_filename = None
        #La imagen transformada.
        self.img = None

        #Esta buena la idea de este metodo, pero parece no funcionar
        #https://deptinfo-ensip.univ-poitiers.fr/ENS/pyside-docs/PySide/QtCore/QMetaObject.html#PySide.QtCore.PySide.QtCore.QMetaObject.connectSlotsByName
        #QtCore.QMetaObject.connectSlotsByName(Form)

    def setImage(self, image, filename):
      self.img_filename = filename
      self.img = image
      self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    def on_save_button_clicked(self, *args, **kwargs):
      split = re.split(r'\.', self.img_filename)
      split[-1] = "transformada.bmp"# + split[-1]
      path = ".".join(split)
      print "Guardando en: %s" % path
      print "Se guardo bien?"
      print self.img.save(path, format="BMP", quality=100)


