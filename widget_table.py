#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide2 import QtWidgets, QtCore, QtGui
from collections import namedtuple
from db import ManagerBase

def export_csv(table, filename = None):
  filename = "export.csv" if filename == None else None
  file = QtCore.QFile(filename)
  if file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Truncate):
    data = QtCore.QTextStream(file)
    str_list = []
    for i in range(table.columnCount()):
      str_list.append("\""+table.horizontalHeaderItem(i).data(QtCore.Qt.DisplayRole)+"\"")
    data << ";".join(str_list) << "\n"
    for r in range(table.rowCount()):
      str_list = []
      for c in range(table.columnCount()):
        #item = table.item(r, c)
        #if (not item or not item.text()):
          #self.setItem(r, c, QtWidgets.QTableWidgetItem("0"))
        str_list.append("\""+table.item(r, c).text()+"\"")
      data << ";".join(str_list) << "\n"
    file.close()

class CalleableWindow(QtWidgets.QWidget):

  def __init__(self, parent, ident):
    super(CalleableWindow, self).__init__(parent, QtCore.Qt.Window)
    self.parent = parent
    self.ident = ident

  def closeEvent(self, a):
    self.parent.close_window(self)

class WidgetTableTemplate(QtWidgets.QTableWidget):

  size_rows = None

  def __init__(self, parent, data = None):
    super(WidgetTableTemplate, self).__init__(0, len(self.column_constructs), parent)
    self.opened_windows = {}
    self.parent = parent
    self.data = data
    self.setSortingEnabled(True)
    self.set_horizontal_header_labels()
    self.resizeSections()
    self.cellClicked.connect(self.open_window)
    if self.data:
      self.load()

  def resizeSections(self):
    for j in range(len(self.column_constructs)):
      size = self.column_constructs[j].header_label.size
      if size:
        self.horizontalHeader().resizeSection(j, size)

  def set_data(self, data):
    self.data = data
    self.load()

  def load(self):

    self.clear()
    self.setSortingEnabled(False)

    while (self.rowCount() > 0):
      self.removeRow(0)

    i = 0
    for item_data in self.data:
      self.insertRow(i)
      for j in range(len(self.column_constructs)):
        item_table = self.extract_item_table(j, item_data)
        self.setItem(i, j, item_table)
        if hasattr(item_table, "size_row"):
          self.size_rows = item_table.size_row
      if self.size_rows:
        self.verticalHeader().resizeSection(i, self.size_rows)
      i += 1

    self.setSortingEnabled(True)
    self.set_horizontal_header_labels()
    #export_csv(self)

  def extract_item_table(self, j, item_data):
      return self.column_constructs[j].item_construct._get_item_table(item_data)

  def set_horizontal_header_labels(self):
    header_labels_string = []
    for table_construct in self.column_constructs:
      header_labels_string.append(str(table_construct.header_label))
    self.setHorizontalHeaderLabels(header_labels_string)

  def open_window(self, row, column):
    if self.column_constructs[column].open_window:
      data = self.item(row, column).text()
      ident = str(column)+":"+data
      if ident not in self.opened_windows:
        self.opened_windows[ident] = self.column_constructs[column].widget(self, data, ident)
      else:
        self.opened_windows[ident].activateWindow()

  def close_window(self, window):
    del self.opened_windows[window.ident]

  def refresh(self):
    self.parent.refresh()

class WidgetTableTemplateQueryJoin(WidgetTableTemplate):

  #def __init__(self, parent, data = None):
    #super(WidgetTableTemplateQueryJoin, self).__init__(parent, data)

  def extract_item_table(self, j, item_data_tuple):
    """
    para los query join los datos vienen en tuplas
    primero se extrae el dato de la tupla a traves
    de la informacion contenida en el header label
    luego se lo trabaja normalmente como en la clase
    padre
    """
    item_data = item_data_tuple[self.column_constructs[j].header_label.index]
    return super(WidgetTableTemplateQueryJoin, self).extract_item_table(j, item_data)

class ConstructorItemTable(object):

  def __init__(self, data_index):
    super(ConstructorItemTable, self).__init__()
    self.data_index = data_index

  def _get_item_table(self, data):
      pass

  def extract_data(self, data_contain):
    return getattr(data_contain, self.data_index)

class ConstructorItemString(ConstructorItemTable):

  def __init__(self, data_index, replace_empty=False):
    super(ConstructorItemString, self).__init__(data_index)
    self.replace_empty = replace_empty

  def _get_item_table(self, data_contain):
    item_string = QtWidgets.QTableWidgetItem("%s" % (self.extract_data(data_contain)))
    item_string.setFlags(item_string.flags() & ~QtCore.Qt.ItemIsEditable)
    return item_string

  def extract_data(self, data_contain):
    """
    en caso que este seteado en True replace_empty se redefine el metodo
    extract_data para que se setee con cadena vacia los elementos nulos
    en la base de datos
    """
    data = super(ConstructorItemString, self).extract_data(data_contain)
    if self.replace_empty:
      data = data if data != None else ''
    return data


class ConstructorItemImage(ConstructorItemTable):

  def __init__(self, data_index, width=-1, height=-1, set_size_row=False):
    super(ConstructorItemImage, self).__init__(data_index)
    self.width = width
    self.height = height
    self.set_size_row = set_size_row

  def _get_item_table(self, data_contain):
    item_img = QtWidgets.QTableWidgetItem()
    data = self.extract_data(data_contain)
    qimage = ManagerBase().bytes_a_imagen(data)
    if self.width != -1 and self.height != -1:
      qimage = qimage.scaled(self.width, self.height)
    item_img.setData(QtCore.Qt.DecorationRole, QtGui.QPixmap.fromImage(qimage))
    if self.set_size_row:
      item_img.size_row = qimage.height()
    return item_img

class HeaderLabel(object):

  def __init__(self, string, size = None):
    super(HeaderLabel, self).__init__()
    self.string = string
    self.size = size

  def __str__(self):
    return self.string

class HeaderLabelIndex(HeaderLabel):

  def __init__(self, string, index, size = None):
    super(HeaderLabelIndex, self).__init__(string, size)
    self.index = index

  def __str__(self):
    return self.string

class ColumnConstruct(namedtuple('ColumnConstruct', "header_label item_construct open_window widget")):
    def __new__(cls, header_label, item_construct, open_window=False, widget=None):
        return super(ColumnConstruct, cls).__new__(cls, header_label, item_construct, open_window, widget)
