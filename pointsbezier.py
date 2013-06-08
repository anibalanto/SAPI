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
    def __init__(self, nodes = None, shapeDest = None, name = None):
        self.name = name
        self.nodes = nodes
        self.shapeDest = shapeDest
        QtGui.QGraphicsItem.__init__(self)

        self.scale = 1.0
        self.definePathShape()
        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        if shapeDest:
            self.points_dest = shapeDest.getListPointsNodes()
            self.points_bound_dest = self.calculatePoints(shapeDest.boundingRect())
            print "points_dest:", self.points_dest
            print "points_bound_dest:", self.points_bound_dest

        self.nodesWeakRef = []
        for i in range(0,4):
            self.nodesWeakRef.append(weakref.ref(self.nodes[i]))
            self.nodesWeakRef[i]().addShape(self)

        self.adjust() 

    def calculatePoints(self, rect):
        coords = rect.getCoords()
        points = [(coords[0],coords[1]), (coords[2],coords[1]), (coords[2],coords[3]), (coords[0],coords[3])]
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
        #print "Shape.boundingRect.%s rect: %s"% (self.name, self.path.boundingRect())
        return self.path.boundingRect()

    def boundingPolygon(self):
        print "  Shape.boundingPolygon.%s"% (self.name,)
        mat = wi.getMat(self.getListPointsNodes(),self.points_dest)
        boundingPolygon = BoundPolygon(self.points_bound_dest)# if self.shapeDest else self.boundingRect()
        #print "       boundingPolygon:", boundingPolygon.toList()
                #print "  Shape.boundingPolygon.%s"% (self.name,)
        #print "       polygon:", boundingPolygon.toList()
        boundingPolygon.close()
        return wi.proyectPolygon(boundingPolygon, np.linalg.inv(mat))

    def proyect(self, mat):
        print "Shape.pryect.shape.%s"% (self.name)
        for node in self.nodes:
            print "Shape.proyect.node.%s"% (node.name)
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
        bp = self.boundingPolygon()
        self.path.addPolygon(bp)
        #print "polygon: ", bp
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
            #print "S.dPS.%s, bD: %s, bS: %s, (po: %s pD: %s)"% (self.name, nodeSource.getPosBezier(nodeDest).toTuple(), nodeDest.getPosBezier(nodeSource).toTuple(), nodeSource.pos().toTuple(), nodeDest.pos().toTuple())

    def getListPointsNodes(self):
        mylist = []
        for node in self.nodes:
            mylist.append(node.pos().toTuple())
            #print "node pos:", node.pos().toTuple()
        return mylist

	def __repr__(self):
		return "Shape.nodes: <%f>" % (self.getListPointsNodes()) 

class BoundPolygon(QtGui.QPolygonF):

    def __init__(self, points):
        QtGui.QPolygonF.__init__(self)
        
        for point in points:
            print "BoundPolygon.point", point
            self.append(QtCore.QPointF(point[0],point[1]))
 
    def close(self):
        self.append(self.toList()[0])

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
        self.pen = QtGui.QPen(self.color, 2 * self.scale, QtCore.Qt.SolidLine)

    def proyect(self, mat):
        print "Point.proyect.%s"% (self.name)
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
        painter.setPen(self.pen)
        painter.drawEllipse(-5 * self.scale, -5 * self.scale, 10 * self.scale, 10 * self.scale)

class Bezier(Point):
    Type = QtGui.QGraphicsItem.UserType + 5
    
    Pi = math.pi
    def __init__(self, graphWidget, node, nodeDest, definator = None):
        self.node = node
        self.name = "v" + node.name + nodeDest.name
        self.nodeDest = nodeDest
        #self.vector = None
        Point.__init__(self, graphWidget)
        self.define(definator)

    def adjust(self):
        print "Bezier%s.adjust: vect: %s, node: %s"% (self.name, self.vector.toPointF().toTuple(), self.node.pos().toTuple())
        self.setPos(self.vector.toPointF() + self.node.pos())
        super(Bezier, self).adjust()

    def itemChange(self, change, value):
        self.node.adjust()
        #print "Bezier.itemChange", self.pos().toTuple()
        #if hasattr(self, 'vector'):
            #self.defineAngle()
        return super(Bezier, self).itemChange(change, value)

    def mousePressEvent(self, event):
        #print "Bezier.mousePressEvent"
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        #print "Bezier.mouseReleaseEvent"
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        #print "Bezier%s.mouseReleaseEvent: %s"% (self.name, self.pos().toTuple())
        self.setVector(self.pos() - self.node.pos())

    def setPos(self, pos):
        #print "Bezier%s.setPos: %s"% (self.name, pos.toTuple())
        super(Bezier, self).setPos(pos)

    def posDefault(self):
        #print "   Bezier%s.posDefault:"% (self.name,)
        #print "      node............:", self.node.pos().toTuple()
        #print "      nodeDest........:", self.nodeDest.pos().toTuple()
        self.setVector(self.node.pos(), self.nodeDest.pos(), FACTOR_BEZIER)
        return self.vector.toPointF() 

    def setVector(self, pos, dest = None, factor = None):
        if dest:
            if not factor:
                factor = 1.0
            self.vector = QtGui.QVector2D(dest - pos) * factor
        else:
            self.vector = QtGui.QVector2D(pos)
    """
    def definePos(self):
        self.setPos(self.vector.toPointF() + self.node.pos())
        print "Bezier%s.definePos: %s"% (self.name, self.pos().toTuple())
    """

    def define(self, definator = None):
        if definator:
            definator.define(self)
        else:
            self.setPos(self.posDefault())

    """
    def defineAngle(self):
        self.defineVector(self.pos())
        if self.vector.length() == 0 or self.vectorToDest.length() == 0:
            return
        print "Bezier.defineAngle", self.vector.toTuple(), self.vectorToDest.toTuple()
        dotProduct = QtGui.QVector2D.dotProduct(self.vector, self.vectorToDest)
        lengthVector = self.vector.length()
        lengthVectorToDest = self.vectorToDest.length()
        dividendo = lengthVector * lengthVectorToDest
        result = dotProduct / dividendo 
        print "arcos(%f / %f * %f)"% (dotProduct, lengthVector, lengthVectorToDest)
        print "arcos(%f / %f)"% (dotProduct, dividendo)
        print "arcos(%f)"% result
        self.angle = math.acos(result) * 180 / self.Pi
        print "Bezier%s.defineAngle: %f"% (self.name, self.angle)
    """


    def rotate(self, angle):
        rad = angle * self.Pi/180
        if self.pos() != (0,0):
            self.setPos(self.posDefault())

        x_rot = self.x() * math.cos(rad) - self.y() * math.sin(rad)
        y_rot = self.x() * math.sin(rad) + self.y() * math.cos(rad)
        #print "Bezier%s.rotate: angle: %f, x: %f, y: %f, x_rot: %f, y_rot: %f"% (self.name, angle, self.x(), self.y(), x_rot, y_rot)
        self.setVector(QtCore.QPointF(x_rot,y_rot))
        self.setPos(self.vector.toPointF() + self.node.pos())

    def getLineToNode(self):
        line = QtCore.QLineF(self.pos(), self.node.pos())
        #print line.toTuple()
        return line 

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawLine(self.getLineToNode())
        super(Bezier, self).paint(painter, option, widget)
"""
class Definator(object):

    def define(self, element)
"""

class AngleDefinator(object):

    def __init__(self, angle):
        super(AngleDefinator, self).__init__()
        self.angle = angle

    def define(self, element):
        element.rotate(self.angle)

class PosDefinator(object):

    def __init__(self, pos):
        super(PosDefinator, self).__init__()
        self.pos = pos

    def define(self, element):
        element.setPos(self.pos)
        self.vector = QtGui.QVector2D(pos - self.node.pos())

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
            bezier = Bezier(graphWidget, self, node, AngleDefinator(angle))
            self.vincules[node] = bezier
            tup = (bezier,) + node.vincule(self, yourAngle, angle, graphWidget)
            return tup 
        return ()

    def getPosBezier(self, node):
        return self.vincules[node].pos()

    def proyect(self, mat):
        print "Node.proyect.%s"% (self.name)
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
            for bezier in self.vincules.values():
                bezier.adjust()

        return super(Node, self).itemChange(change, value)

    def paint(self, painter, option, widget):
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
        shapeDest = Shape(nodes, name="shDest")
        shape = Shape(nodes, shapeDest, name="shEdit")

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
