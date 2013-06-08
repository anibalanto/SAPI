#!/usr/bin/env python

import sys
import weakref
import math
import warp_image as wi
import numpy as np
import copy
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

C1 = QtCore.Qt.red
C2 = QtCore.Qt.green

WIDHT_DEST = 600
HEIGHT_DEST = 600

FACTOR_BEZIER = 1.0/3

POINTS_DEST = [(0,0), (WIDHT_DEST,0), (WIDHT_DEST,HEIGHT_DEST), (0,HEIGHT_DEST)]

class Shape(QtGui.QGraphicsItem):

    Pi = math.pi
    Type = QtGui.QGraphicsItem.UserType + 3
    def __init__(self, nodes = None, shapeDest = None):
        self.nodes = nodes
        self.shapeDest = shapeDest
        QtGui.QGraphicsItem.__init__(self)

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

    def calculatePoints(self, rect):
        coords = rect.getCoords()
        points = [QtCore.QPointF(coords[0],coords[1]), QtCore.QPointF(coords[1],coords[2]), QtCore.QPointF(coords[2],coords[3]), QtCore.QPointF(coords[3],coords[1])]
        return points

    def containsPath(self, point):
        return self.path.contains(point)

    def intersectsPath(self, point):
        return self.path.intersects(point)

    def setScale(self, scale):
        self.scale = scale

    def type(self):
        return Shape.Type

    def adjust(self):
        self.prepareGeometryChange()

    def boundingRect(self):
        return self.path.boundingRect()

    def boundingPolygon(self):
        mat = wi.getMat(self.getListPointsNodes(),POINTS_DEST)
        boundingPolygon = BoundPolygon(self.calculatePoints(self.shapeDest.boundingRect())) if self.shapeDest else self.boundingRect()
        wi.proyectPolygon(boundingPolygon, np.linalg.inv(mat))
        return boundingPolygon

    def proyect(self, mat):
        print "Shape.pryect", shape
        for node in self.nodes:
            print "Shape.proyect", node 
            node.proyect(mat)

    def paint(self, painter, option, widget):
        
        self.definePathShape()

        #self.path.addRect(self.boundingRect())
        #print self.scale
        """
        i = 0
        for boundPoint in self.boundPoints:
            x, y = self.pointBound(boundPoint[0], boundPoint[1])
            #x, y = self.pointBound(self.nodes[i].pos().x(), self.nodes[i].pos().y())
            #print "node...............:", i, (self.nodes[i].pos().x(), self.nodes[i].pos().y())
            print "bound..............:", i, (boundPoint[0], boundPoint[1]) 
            print "bound result.......:", i, (x, y)
            #print "node result........:",i , self.pointBound(self.nodes[i].pos().x(), self.nodes[i].pos().y())
            self.nodesBound[i].setPos(x, y)
            i +=1
        """
        self.path.addPolygon(self.boundingPolygon())

        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(self.path)

    def definePathShape(self):
        factor = 1.0/3
        
        self.path =  QtGui.QPainterPath()
        self.path.moveTo(self.nodes[0].pos())
        for i in range(0,4):
            nodeSource = self.nodes[i]
            nodeDest = self.nodes[(i + 1) % 4]
            self.path.cubicTo(nodeSource.getPosBezier(nodeDest), nodeDest.getPosBezier(nodeSource), nodeDest.pos())

    def getListPointsNodes(self):
        mylist = []
        for node in self.nodes:
            mylist.append(node.pos().toTuple())
            #print "node pos:", node.pos().toTuple()
        return mylist

	def __repr__(self):
		return "<%f>" % (self.getListPointsNodes()) 

class BoundPolygon(QtGui.QPolygonF):

    def __init__(self, points):
        QtGui.QPolygonF.__init__(self)
        
        for point in points:
            self.append(point)

class Point(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 4
    
    def __init__(self, graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.scale = 1.0
        self.shapeList = []

        self.color = C1
        self.graph = weakref.ref(graphWidget)

        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

    def proyect(self, mat):
        print self
        wi.proyect(self.pos(),mat)

    def type(self):
        return Node.Type

    def adjust(self):
        self.prepareGeometryChange()
        
    def setScale(self, scale):
        self.scale = scale

    def addShape(self, shape):
        self.shapeList.append(weakref.ref(shape))
        shape.adjust()

    def shapes(self):
        return self.shapeList

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

    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

	def __repr__(self):
		return "<%f, %f>" % (self.pos().x()), (self.pos().y()) 

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(self.color, 1 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawEllipse(-10 * self.scale, -10 * self.scale, 20 * self.scale, 20 * self.scale)



class Bezier(Point):
    Type = QtGui.QGraphicsItem.UserType + 5
    
    Pi = math.pi
    def __init__(self, graphWidget, node, nodeDest, angle):
        self.node = node
        self.name = "v" + node.name + nodeDest.name
        Point.__init__(self, graphWidget)
        self.nodeDest = nodeDest
        self.definePos(angle)

    def itemChange(self, change, value):
        self.node.adjust()
        return super(Bezier, self).itemChange(change, value)

    def definePos(self, angle):
        vectorToDest = QtGui.QVector3D(self.node.pos() - self.nodeDest.pos()) * FACTOR_BEZIER
        vBezier =  self.rotate(vectorToDest, angle)
        #print "pBezier, pNode", vBezier.toPointF().toTuple(), self.node.pos().toTuple()
        print "Bezier.definePos.result", (vBezier.toPointF() + self.node.pos()).toTuple()
        self.setPos(vBezier.toPointF() + self.node.pos())

    def rotate(self, vector, angle):
        rad = angle * self.Pi/180
        x = vector.x() * math.cos(rad) - vector.y() * math.sin(rad)
        y = vector.x() * math.sin(rad) + vector.y() * math.cos(rad)
        return QtGui.QVector3D(QtCore.QPoint(x,y))

class Node(Point):
    Type = QtGui.QGraphicsItem.UserType + 6

    def __init__(self, graphWidget, name = None):
        Point.__init__(self, graphWidget)
        self.name = name
        self.Type += 1
        self.edgeList = []
        self.contained = False

        self.vincules = {}

    def vincule(self, node, angle, yourAngle, graphWidget):
        if not (node in self.vincules):
            bezier = Bezier(graphWidget, self, node, angle)
            self.vincules[node] = bezier
            tup = (bezier,) + node.vincule(self, yourAngle, angle, graphWidget)
            return tup 
        return ()

    def getPosBezier(self, node):
        return self.vincules[node].pos()

    def proyect(self, mat):
        print "Node.proyect", self
        super(Node, self).proyect(mat)
        for bezier in self.vincules:
            bezier.poryect(mat)

    def addEdge(self, edge):
        self.edgeList.append(weakref.ref(edge))
        edge.adjust()

    def edges(self):
        return self.edgeList

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edgeList:
                edge().adjust()
            for shape in self.shapeList:
                shape().adjust()
            for bezier in self.vincules:
                bezier.adjust()

        return super(Node, self).itemChange(change, value)

    def paint(self, painter, option, widget):
        #print "Node.paint"
        painter.setPen(QtGui.QPen(self.color, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawEllipse(-10 * self.scale, -10 * self.scale, 20 * self.scale, 20 * self.scale)

class GraphWidget(QtGui.QGraphicsView):
    def __init__(self, filename):
        QtGui.QGraphicsView.__init__(self)

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(0, 0, 600,600)

        scene.addPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(filename)))

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

        node1 = Node(self, "n1")
        node2 = Node(self, "n2")
        node3 = Node(self, "n3")
        node4 = Node(self, "n4")

        node1.setPos(200, 200)
        node2.setPos(400, 200)
        node3.setPos(400, 400)
        node4.setPos(200, 400)

        bezier12, bezier21 = node1.vincule(node2,ANGLES[0][1],ANGLES[1][0],self)
        bezier23, bezier32 = node2.vincule(node3,ANGLES[1][2],ANGLES[2][1],self)
        bezier34, bezier43 = node3.vincule(node4,ANGLES[2][3],ANGLES[3][2],self)
        bezier41, bezier14 = node4.vincule(node1,ANGLES[3][0],ANGLES[0][3],self)
        
        """
        nodeBound1 = Node(self)
        nodeBound2 = Node(self)
        nodeBound3 = Node(self)
        nodeBound4 = Node(self)
        """

        nodes = [node1, node2, node3, node4]
        shapeDest = Shape(nodes)
        shape = Shape(nodes, shapeDest)

        #nodeTest = NodeTest(self, shape)

        node1.setZValue(10)
        node2.setZValue(10)
        node3.setZValue(10)
        node4.setZValue(10)
        #scene.addItem(Edge(node1, node2, -10, 10))
        #scene.addItem(Edge(node2, node3,  -30, 60))
        #scene.addItem(Edge(node3, node4, 60, -60))
        #scene.addItem(Edge(node4, node1, -60, 30))

        #nodeTest.setPos(10,10)

        self.scene().addItem(shape)

        self.scene().addItem(node1)
        self.scene().addItem(node2)
        self.scene().addItem(node3)
        self.scene().addItem(node4)

        self.scene().addItem(bezier12)
        self.scene().addItem(bezier21)
        self.scene().addItem(bezier23)
        self.scene().addItem(bezier32)
        self.scene().addItem(bezier34)
        self.scene().addItem(bezier43)
        self.scene().addItem(bezier41)
        self.scene().addItem(bezier14)

        """
        self.scene().addItem(nodeBound1)
        self.scene().addItem(nodeBound2)
        self.scene().addItem(nodeBound3)
        self.scene().addItem(nodeBound4)
        """
        #self.scene().addItem(nodeTest)

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

    widget = GraphWidget(sys.argv[1])
    widget.show()

    sys.exit(app.exec_())
