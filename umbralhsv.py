#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PySide.QtCore import *
from PySide.QtGui import *
import operator
import colors

class MyQSpinBox(QSpinBox):
  def __init__(self, min_val, max_val, curr_value):
    super(MyQSpinBox, self).__init__()
    self.setMinimum(min_val)
    self.setMaximum(max_val)
    self.setValue(curr_value)

class Form(QDialog):

  def __init__(self, trans, origen, parent=None):
    super(Form, self).__init__(parent)

    #El transformador
    self.trans = trans
    self.img_origen = origen

    #Create widgets
    """self.widget_dict = dict()

    self.widget_dict["h_h"] = MyQSpinBox(0, 359, 30)
    self.widget_dict["h_l"] = MyQSpinBox(0, 359, 350)
    self.widget_dict["s_h"] = MyQSpinBox(0, 100, 100)
    self.widget_dict["s_l"] = MyQSpinBox(0, 100, 50)
    self.widget_dict["v_h"] = MyQSpinBox(0, 100, 100)
    self.widget_dict["v_l"] = MyQSpinBox(0, 100, 50)
    self.button = QPushButton("Mostrar")        

    # Create layout and add widgets
    layout = QVBoxLayout()
    #i: key j:value
    for i,j in sorted(self.widget_dict.iteritems(), key=operator.itemgetter(0)):
      layout.addWidget(QLabel(i))
      layout.addWidget(self.widget_dict[i])
    layout.addWidget(self.button)
    # Set dialog layout
    self.setLayout(layout)
    self.button.clicked.connect(self.action)"""

  def action(self):
    """values = {index:int(self.widget_dict[index].value()) for index in self.widget_dict}
    print values

    algoritmo = colors.AlgoritmoUmbralHSV(**values)
    algoritmo2 = colors.AlgoritmoCombinar(self.img_origen)

    umbralada = trans.aplicar(algoritmo, self.img_origen)
    combinada = trans.aplicar(algoritmo2, umbralada)

    filename = combinada.save_temp()
    print filename

    umbralada.show()
    combinada.show()"""

if __name__ == '__main__':
  # Create the Qt Application
  app = QApplication(sys.argv)

  origen = colors.cargar(sys.argv[1])
  origen.show()
  trans = colors.Transformador()

  # Create and show the form
  form = Form(trans, origen)
  form.show()
  # Run the main Qt loop
  sys.exit(app.exec_())
