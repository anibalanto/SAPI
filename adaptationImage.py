from PySide import QtCore, QtGui
import cv2 as cv
import cStringIO
import Image


def QImageToImagePIL(qimage):
    buff = QtCore.QBuffer()
    buff.open(QtCore.QIODevice.ReadWrite)
    qimage.save(buff, "PNG")

    strio = cStringIO.StringIO()
    strio.write(buff.data())
    buff.close()
    strio.seek(0)
    return Image.open(strio)


def OpenCVImageToQImage(openCVImage):
    dst = cv.cvtColor(openCVImage, cv.COLOR_BGR2RGB)
    h = dst.shape[0]
    w = dst.shape[1]
    qim = QtGui.QImage(dst.data, w, h, dst.strides[0], QtGui.QImage.Format_RGB888)
    return qim.copy()


def ImagePILToQImage(pilImage):
    data = pilImage.tostring('raw','RGBA')
    qimage = QtGui.QImage(data,pilImage.size[0],pilImage.size[1],QtGui.QImage.Format_ARGB32)
    return qimage