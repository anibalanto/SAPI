#!/usr/bin/env python

import sys
import weakref
import math
from PySide import QtCore, QtGui

A01 = -10
A10 = 10

A12 = -30
A21 = 60

A23 = 60
A32 = -60

A30 = -60
A03 = 30

ANGLES = [[0,A01,0,A03],
        [A10,0,A12,0],
        [0,A21,0,A23],
        [A30,0,A32,0]]

class Shape(QtGui.QGraphicsItem):

    Pi = math.pi
    Type = QtGui.QGraphicsItem.UserType + 3
    def __init__(self, nodes, angles):
        QtGui.QGraphicsItem.__init__(self)

        self.angles = angles
        self.nodes = nodes
        self.scale = 1.0
        self.path =  QtGui.QPainterPath()
        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        self.nodesWeakRef = []
        for i in range(0,4):
            self.nodesWeakRef.append(weakref.ref(self.nodes[i]))
            self.nodesWeakRef[i]().addShape(self)

        self.adjust() 

    def setScale(self, scale):
        self.scale = scale

    def type(self):
        return Shape.Type

    def adjust(self):
        self.prepareGeometryChange()

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        factor = 1.0/3
        
        self.path =  QtGui.QPainterPath()
        self.path.moveTo(self.nodes[0].pos())
        for nsource in range(0,4):
            ndest = (nsource + 1) % 4
            pBezierSource = self.pointBezierVector(self.nodes[nsource].pos(), self.nodes[ndest].pos(), self.angles[nsource][ndest], factor)
            pBezierDest =  self.pointBezierVector(self.nodes[ndest].pos(), self.nodes[nsource].pos(), self.angles[ndest][nsource], factor)
            self.path.cubicTo(pBezierSource, pBezierDest, self.nodes[ndest].pos())

        #print self.scale
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(self.path)

    def pointBezierVector(self, pointSource, pointDest, angle, factor):
        vBezier =  QtGui.QVector3D(pointDest - pointSource) * factor
        vBezierRotate = self.rotation(vBezier,angle)
        return vBezierRotate.toPointF() + pointSource

    def rotation(self, vector, angle):
        rad = angle * self.Pi/180
        x = vector.x() * math.cos(rad) - vector.y() * math.sin(rad)
        y = vector.x() * math.sin(rad) + vector.y() * math.cos(rad)
        return QtGui.QVector3D(QtCore.QPoint(x,y))

class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 4
    
    def __init__(self, graphWidget):
        QtGui.QGraphicsItem.__init__(self)

        self.scale = 1.0
        self.graph = weakref.ref(graphWidget)
        self.edgeList = []
        self.shapeList = []
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

    def setScale(self, scale):
        self.scale = scale

    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(weakref.ref(edge))
        edge.adjust()

    def addShape(self, shape):
        self.shapeList.append(weakref.ref(shape))
        shape.adjust()

    def shapes(self):
        return self.shapeList

    def edges(self):
        return self.edgeList

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(self.scale * (-10 - adjust), self.scale * (-10 - adjust),
                             self.scale * (23 + adjust), self.scale * (23 + adjust))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10 * self.scale, -10 * self.scale, 20 * self.scale, 20 * self.scale)
        return path

    def paint(self, painter, option, widget):
        #print "Node.paint"
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawEllipse(-10 * self.scale, -10 * self.scale, 20 * self.scale, 20 * self.scale)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edgeList:
                edge().adjust()
            for shape in self.shapeList:
                shape().adjust()
            #self.graph().itemMoved()

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

	def __repr__(self):
		return "<%f, %f>" % (self.pos().x()), (self.pos().y()) 

class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(0, 0, 600,600)

        scene.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage("IMG_0235.JPG")))

        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        """
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)
        """
        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))


        self.createItems()
        """
        self.createActions()
        self.createMenus()

        self.updateActions()
        """

    def keyPressEvent(self, event):
        key = event.key()

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))
        
    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.0001 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)
        for item in self.items():
            print "setScale: ", 1.0/factor, factor
            item.setScale(1.0/factor)

    """
    def loadImage(self, filename):
        img_cv = cv.imread(filename)
        if not(img_cv.size):
            QtGui.QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return
        self.cv_img = img_cv
        self.img_filename = filename
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(self.openCVtoQImage(self.cv_img)))
        self.scaleImage(self.size().width()/self.img.size().width())
        print "en loadImage:", self.imageLabel.size()

    def open(self):
        filename,_ = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                QtCore.QDir.currentPath())
        self.loadImage(filename)
        self.updateActions()
        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.scaleFactor = 1.0
        self.scaleImage(self.size().width()/self.img.size().width())
    """

    def createItems(self):

        node1 = Node(self)
        node2 = Node(self)
        node3 = Node(self)
        node4 = Node(self)

        node1.setZValue(10)
        node2.setZValue(10)
        node3.setZValue(10)
        node4.setZValue(10)
        #scene.addItem(Edge(node1, node2, -10, 10))
        #scene.addItem(Edge(node2, node3,  -30, 60))
        #scene.addItem(Edge(node3, node4, 60, -60))
        #scene.addItem(Edge(node4, node1, -60, 30))

        node1.setPos(300, 100)
        node2.setPos(400, 400)
        node3.setPos(100, 500)
        node4.setPos(50, 200)

        nodes = [node1, node2, node3, node4]
        shape = Shape(nodes, ANGLES)

        self.scene().addItem(shape)

        self.scene().addItem(node1)
        self.scene().addItem(node2)
        self.scene().addItem(node3)
        self.scene().addItem(node4)

    """
    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.transformAct = QtGui.QAction("&Transform", self,
                shortcut="Ctrl+T", enabled=False, triggered=self.transform)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()

        self.transformMenu = QtGui.QMenu("&Transform", self)
        self.transformMenu.addAction(self.transformAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.transformMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
    """

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))

    widget = GraphWidget()
    widget.show()

    sys.exit(app.exec_())
