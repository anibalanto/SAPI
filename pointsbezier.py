#!/usr/bin/env python

import weakref
import math
import warp_image as wi
import numpy as np
from PySide import QtCore, QtGui

A01 = -10
A10 = 10

A12 = -30
A21 = 30

A23 = 30
A32 = -30

A30 = -30
A03 = 30

ANGLES = [[0, A01, 0, A03],
        [A10, 0, A12, 0],
        [0, A21, 0, A23],
        [A30, 0, A32, 0]]

C1 = QtCore.Qt.red
C2 = QtCore.Qt.green

WIDHT_DEST = 600
HEIGHT_DEST = 600

FACTOR_BEZIER = 1.0 / 3

POINTS_DEST = [(0, 0), (WIDHT_DEST, 0), (WIDHT_DEST, HEIGHT_DEST), (0, HEIGHT_DEST)]

class Points(object):

    def __init__(self):
        super(Points, self).__init__()
        self.numberPoints = 0
        self.points = []

    def addPoint(self, scene, point):
        if (self.numberPoints < 4):
            self.points.append(point)
            self.numberPoints = self.numberPoints + 1
            scene.addItem(point)
        else:
            del point

    def removeAllPoints(self, scene):
        while (self.numberPoints > 0):
            point = self.points[self.numberPoints - 1]
            scene.removeItem(point)
            self.points.remove(point)
            del point
            self.numberPoints = self.numberPoints - 1

    def getNumberPoints(self):
        return self.numberPoints

    def getPoints(self):
        return self.points
    """
    def paint(self, painter, option, widget):
        self.definePathShape()
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        for i in range(0, self.numberPoints):
            painter.draw

    """

class Shape(QtGui.QGraphicsItem):

    Pi = math.pi
    Type = QtGui.QGraphicsItem.UserType + 3
    def __init__(self, graphWidget, nodes, name = None, shapeDest = None):
        self.name = name
        self.nodes = nodes
        self.graphWidget = graphWidget
        if shapeDest:
            self.shapeDest = shapeDest
            self.points_dest = shapeDest.getListPointsNodes()
            self.points_bound_dest = self.transformToListPoints(shapeDest.boundingRect())
        QtGui.QGraphicsItem.__init__(self)

        self.scale = 1.0
        self.definePathShape()
        self.arrowSize = 10.0
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        self.nodesWeakRef = []
        for i in range(0,4):
            self.nodesWeakRef.append(weakref.ref(self.nodes[i]))
            self.nodesWeakRef[i]().addShape(self)

        self.adjust()
        """
        for node in self.nodes:
            node.setShape(self)
        """
    def heightDest(self):
        return self.shapeDest.boundingRect().height()

    def widthDest(self):
        return self.shapeDest.boundingRect().width()

    def getPointsDest(self):
        rect = self.shapeDest.boundingRect()
        coords = rect.getCoords()
        return self.transformToListPoints(rect, -1 * coords[0], -1 * coords[1])

    def boundingRectDest(self):
        return self.shapeDest.boundingRect()

    def getShapeDest(self):
        return self.shapeDest

    def getPoints(self):
        points = []
        for node in self.nodes:
            points.append(node.pos().toTuple())
        return points

    def getNodes(self):
        return self.nodes

    def transformToListPoints(self, rect, dx = None, dy = None):
        if not dx or not dy:
            dx = 0
            dy = 0
        coords = rect.getCoords()
        points = []
        for i in [1,3]:
            points.append((coords[i-1] + dx, coords[i] + dy))
            points.append((coords[(i+1) % 4] + dx, coords[i] +dy))
        return points

    def contains(self, point):
        return self.path.contains(point)

    def intersects(self, point):
        return self.path.intersects(point)

    def setScale(self, scale):
        self.scale = scale

    def type(self):
        return Shape.Type

    def adjust(self):
        self.prepareGeometryChange()

    def boundingRect(self):
        return self.path.boundingRect()

    def updateBezierTransform(self, nodes, mat):
        i = 0
        for node in nodes:
            for vincule in node.getVincules():
                bezierUpdate = self.nodes[i].getBezierByVinculeName(vincule.name)
                bezierUpdate.setPos(wi.proyectCoord(node.getBezier(vincule).pos(), mat))
            i += 1
        self.definePathShape()

    def boundingPolygon(self):
        mat = wi.getMat(self.getListPointsNodes(),self.points_dest)
        self.shapeDest.updateBezierTransform(self.nodes, mat)
        self.points_bound_dest = self.transformToListPoints(self.shapeDest.boundingRect())
        boundingPolygon = BoundPolygon(self.points_bound_dest)
        boundingPolygon.close()
        return wi.proyectPolygon(boundingPolygon, np.linalg.inv(mat))

    def proyect(self, mat):
        for node in self.nodes:
            node.proyect(mat)

    def paint(self, painter, option, widget):

        self.definePathShape()
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 3 * self.graphWidget.getScale(), QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(self.path)

    def definePathShape(self):

        self.path =  QtGui.QPainterPath()
        self.path.moveTo(self.nodes[0].pos())
        for i in range(0,4):
            nodeSource = self.nodes[i]
            nodeDest = self.nodes[(i + 1) % 4]
            self.path.cubicTo(nodeSource.getBezier(nodeDest).pos(), nodeDest.getBezier(nodeSource).pos(), nodeDest.pos())

    def getListPointsNodes(self):
        mylist = []
        for node in self.nodes:
            mylist.append(node.pos().toTuple())
        return mylist

    def __repr__(self):
	return "Shape.nodes: <%f>" % (self.getListPointsNodes())

    def toImage(self):
        rect = self.boundingRect()
        qimage = QtGui.QImage(rect.width(),rect.height())
        return qimage


class ShapeDest(Shape):

    def __init__(self, graphWidget, nodes, name = None):
        super(ShapeDest, self).__init__(graphWidget, nodes, name)

    def paint(self, painter, option, widget):

        self.definePathShape()

        painter.setBrush(QtGui.QColor(0, 0, 0))
        painter.drawRect(self.boundingRect())

        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawPath(self.path)



    def getImage(self):
        brect = self.boundingRect()
        qimage = QtGui.QImage(brect.width(), brect.height(), QtGui.QImage.Format_RGB888)
        qpainter = QtGui.QPainter(qimage)
        qpainter.setBackground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        qpainter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.scene().setSceneRect(brect)
        self.scene().render(qpainter)
        qpainter.end()
        return qimage

class BoundPolygon(QtGui.QPolygonF):

    def __init__(self, points):
        QtGui.QPolygonF.__init__(self)

        for point in points:
            self.append(QtCore.QPointF(point[0], point[1]))

    def close(self):
        self.append(self.toList()[0])

class PointSimple(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 8

    def __init__(self, myScene, graphWidget, pos, scale):
        QtGui.QGraphicsItem.__init__(self)
        self.scale = 1.0

        self.color = C1
        self.graph = weakref.ref(graphWidget)
        self.graphWidget = graphWidget

        self.myScene = myScene

        self.scale = scale
        self.newPos = pos
        self.setPos(pos)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.setZValue(10)

    def type(self):
        return Node.Type

    def setScale(self, scale):
        self.scale = scale

    def advance(self):
        if self.newPos == self.pos():
            return False

        self.setPos(self.newPos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(self.scale * (-10 - adjust), self.scale * (-10 - adjust),
                             self.scale * (23 + adjust), self.scale * (23 + adjust))

    #def mouseReleaseEvent(self, event):
        #print ("PointSimple.mousePressEvent")

    def mousePressEvent(self, event):
        self.myScene.notDoAddPoint()
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(self.color, 2 * self.graphWidget.getScale(), QtCore.Qt.SolidLine))
        inic = -5 * self.graphWidget.getScale()
        end = 10 * self.graphWidget.getScale()
        painter.drawEllipse(inic, inic, end, end)


class Point(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 4

    def __init__(self, graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.shapeList = []

        self.color = C1
        self.graph = weakref.ref(graphWidget)
        self.graphWidget = graphWidget

        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        self.setZValue(10)

    def proyect(self, mat):
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
        return QtCore.QRectF(self.graphWidget.getScale() * (-10 - adjust), self.graphWidget.getScale() * (-10 - adjust),
                             self.graphWidget.getScale() * (23 + adjust), self.graphWidget.getScale() * (23 + adjust))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10 * self.graphWidget.getScale(), -10 * self.graphWidget.getScale(), 20 * self.graphWidget.getScale(), 20 * self.graphWidget.getScale())
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
        painter.setPen(QtGui.QPen(self.color, 2 * self.graphWidget.getScale(), QtCore.Qt.SolidLine))
        painter.drawEllipse(-5 * self.graphWidget.getScale(), -5 * self.graphWidget.getScale(), 10 * self.graphWidget.getScale(), 10 * self.graphWidget.getScale())

class Bezier(Point):
    Type = QtGui.QGraphicsItem.UserType + 5

    Pi = math.pi
    TwoPi = 2 * math.pi
    def __init__(self, graphWidget, node, nodeDest, definator = None):
        self.node = node
        self.name = "v" + node.name + nodeDest.name
        self.nodeDest = nodeDest
        #self.shape = None
        Point.__init__(self, graphWidget)
        self.vectorToDest = self.getVectorToDest()
        self.define(definator)
        self.vectorToDest2 = self.vectorToDest

    """
    def setShape(self, shape):
        self.shape = shape
    """

    def adjust(self):
        self.updateVector()
        self.nodeDest.getBezier(self.node).updateVector()
        self.updateVectorToDest()
        self.nodeDest.getBezier(self.node).updateVectorToDest()
        super(Bezier, self).adjust()

    def itemChange(self, change, value):
        self.node.adjust()
        return super(Bezier, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        self.updateVector(QtGui.QVector2D(self.pos() - self.node.pos()))
        self.rad = self.getRadians()

    def setPos(self, pos):
        super(Bezier, self).setPos(pos)

    def posDefault(self):
        self.updateVector(self.getVectorToDest() * FACTOR_BEZIER)
        return self.vector.toPointF()

    def getFactor(self):
        if not self.factor:
            if not self.vector:
                self.factor = 1.0
            else:
                self.factor = self.vector.length()
        return self.factor

    def getVectorToDest(self):
        return QtGui.QVector2D(self.nodeDest.pos() - self.node.pos())

    def updateVector(self, vector = None):
        if vector != None:
            self.vector = vector
        else:
            vectorToDest = self.getVectorToDest()
            self.vector = vectorToDest * (self.vector.length() / vectorToDest.length())
            self.setPos(self.vector.toPointF() + self.node.pos())
            self.rotate()

    def updateVectorToDest(self):
        self.vectorToDest = self.getVectorToDest()
        self.vectorToDest2 = self.vectorToDest
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

    def getNormal(self):
        v1 = self.vectorToDest.toVector3D()
        v2 = self.vector.toVector3D()
        return QtGui.QVector3D.normal(v1, v2)

    def getRadians(self):
        if self.vector.length() == 0 or self.vectorToDest.length() == 0:
            return
        result = QtGui.QVector2D.dotProduct(self.vector, self.vectorToDest) / (self.vector.length() * self.vectorToDest.length())
        rad = math.acos(result)
        if self.getNormal().z() == -1:
            rad = self.TwoPi - rad
        self.updateVectorToDest()
        return rad

    def rotate(self, rad = None):
        if rad:
            self.rad = rad
        if self.pos().toTuple() == (0.0,0.0):
            self.setPos(self.posDefault())

        x_rot = self.vector.x() * math.cos(self.rad) - self.vector.y() * math.sin(self.rad)
        y_rot = self.vector.x() * math.sin(self.rad) + self.vector.y() * math.cos(self.rad)
        #print "Bezier%s.rotate: angle: %f, x: %f, y: %f, x_rot: %f, y_rot: %f"% (self.name, self.rad, self.x(), self.y(), x_rot, y_rot)
        vector = QtGui.QVector2D(QtCore.QPointF(x_rot,y_rot))
        #print "Bezier%s.rotate: vectorResult: %s, posRes: %s"% (self.name, vector.toTuple(), (x_rot, y_rot))
        self.updateVector(vector)
        self.setPos(self.vector.toPointF() + self.node.pos())

    def paint(self, painter, option, widget):
        super(Bezier, self).paint(painter, option, widget)
        painter.drawLine(QtCore.QLineF(0, 0, self.node.pos().x() - self.pos().x(), self.node.pos().y() - self.pos().y()))
        #painter.drawLine(QtCore.QLineF(self.pos().x(), self.pos().y(), self.node.pos().x(), self.node.pos().y()))
        #print "Bezier%s.paint: Line: %s"% (self.name, (self.pos().toTuple(), self.node.pos().toTuple()))
        #painter.drawRect(self.boundingRect())
        #print self.boundingRect()


    def boundingRect(self):
        return QtCore.QRectF(-200 * self.graphWidget.getScale(), -200 * self.graphWidget.getScale(), 800 * self.graphWidget.getScale(), 800 * self.graphWidget.getScale())
                #QtCore.QRectF(self.node.pos().x(), self.nodeDest.pos().y(), self.nodeDest.pos().x(), self.node.pos().y())
        #self.scale = 1.0
        #adjust = 2000.0
        #return QtCore.QRectF(self.scale * (-10 - adjust), self.scale * (-10 - adjust), self.scale * (23 + adjust), self.scale * (23 + adjust))

"""
class Definator(object):

    def define(self, element)
"""

class AngleDefinator(object):

    Pi = math.pi
    def __init__(self, angle):
        super(AngleDefinator, self).__init__()
        self.angle = angle

    def define(self, element):
        element.rotate(self.angle * self.Pi/180)

class PosDefinator(object):

    def __init__(self, pos):
        super(PosDefinator, self).__init__()
        self.pos = pos

    def define(self, element):
        element.setPos(self.pos)
        self.vector = QtGui.QVector2D(self.pos - self.node.pos())

class Node(Point):
    Type = QtGui.QGraphicsItem.UserType + 6

    def __init__(self, graphWidget, name = None):
        Point.__init__(self, graphWidget)
        self.name = name
        self.Type += 1
        self.edgeList = []
        self.contained = False

        self.vincules = {}
        self.vinculesName = {}

    """
    def setShape(self, shape):
        for bezier in self.vincules.values():
            bezier.setShape(shape)
    """

    def vincule(self, node, angle, yourAngle, graphWidget):
        if not (node in self.vincules):
            bezier = Bezier(graphWidget, self, node, AngleDefinator(angle))
            self.vincules[node] = bezier
            self.vinculesName[node.name] = node
            #print "Node.vincule.%s <-----> %s"% (self.name, node.name)
            tup = (bezier,) + node.vincule(self, yourAngle, angle, graphWidget)
            return tup
        return ()

    def getVincules(self):
        return self.vincules.keys()

    def getBeziers(self):
        return self.vincules.values()

    def getBezierByVinculeName(self, vinculeName):
        #print "Node.getBezierByNameVincule.%s: vinculeName: %s in %s"% (self.name, vinculeName, self.vinculesName.keys())
        return self.getBezier(self.vinculesName[vinculeName])

    def getBezier(self, node):
        return self.vincules[node]

    def proyect(self, mat):
        #print "Node.proyect.%s"% (self.name)
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
            for node, bezier in self.vincules.items():
                bezier.adjust()

        return super(Node, self).itemChange(change, value)

    """
    def mouseReleaseEvent(self, event):
        return super(Node, self).itemChange(change, value)
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
    """

    def paint(self, painter, option, widget):
        super(Node, self).paint(painter, option, widget)
        #painter.setPen(QtGui.QPen(self.color, 3 * self.scale, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawEllipse(-10 * self.graphWidget.getScale(), -10 * self.graphWidget.getScale(), 20 * self.graphWidget.getScale(), 20 * self.graphWidget.getScale())

"""
class WidgetDest(QtGui.QGraphicsView):

    def __init__(self, shape):
        QtGui.QGraphicsView.__init__(self)

        self.shape = shape

        scene = QtGui.QGraphicsScene(self)
        scene.setSceneRect(0, 0, 0, 0)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        scene.addItem(shape)

        #shape.getImage().save("pruebaqimage.png")


    def shape(self):
        return self.shape

"""

class MyScene(QtGui.QGraphicsScene):

    clicked = QtCore.Signal(int,int)

    def __init__(self, qGraphicsView):
        super(MyScene, self).__init__(qGraphicsView)

        self.grap = qGraphicsView

        self.doAddPoint = True

        self.clicked.connect(self.clickSelector)

    def mousePressEvent(self, event):
        super(MyScene, self).mousePressEvent(event)
        #self.clickSelector(event.scenePos().x(),event.scenePos().y())
        self.clicked.emit(event.scenePos().x(),event.scenePos().y())

    def notDoAddPoint(self):
        self.doAddPoint = False

    def getDoAddPoint(self):
        doAddPoint = self.doAddPoint
        self.doAddPoint = True
        return doAddPoint

    def clickSelector(self, x, y):
        if (self.grap.isSetImage() and self.getDoAddPoint()):
            point = PointSimple(self, self.grap, QtCore.QPointF(x, y), self.grap.getScale())
            self.grap.points.addPoint(self,point)
            if (self.grap.points.getNumberPoints() == 4):
                self.grap.createItems()
                self.clicked.disconnect(self.clickSelector)
                self.grap.clicked.connect(self.grap.clickSelector)
                self.grap.points.removeAllPoints(self)


class SelectorWidget(QtGui.QGraphicsView):

    clicked = QtCore.Signal(int,int)
    scaleFactor = 1.0

    def __init__(self):
        self.scroll = QtGui.QWidget()
        self.scroll.setGeometry(QtCore.QRect(0, 0, 1022, 798))
        QtGui.QGraphicsView.__init__(self, self.scroll)

        scene = MyScene(self)
        #scene.setSceneRect(0, 0, 800, 800)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        #self.setSceneRect(0, 0, 0, 0)

        #self.addImage(filename)

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
        self.scale(self.scaleFactor, self.scaleFactor)
        self.setMinimumSize(400, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))


        self.points = Points()

        self.shape = None
        self.factor = None

        #self.createItems()
        """
        self.createActions()
        self.createMenus()

        self.updateActions()
        """

    def clickSelector(self, x, y):
        #node = self.shape.addNode(QtCore.QPointF(x, y))
        #self.scene().addItem(node)
        print (x, y)



    def addImage(self, image):
        #self.scene().clear()
        imageItem = self.scene().addPixmap(QtGui.QPixmap.fromImage(image))
        self.scene().setSceneRect(imageItem.boundingRect())
        imageItem.setZValue(-1)
        self.image = image
        self.resetSizeImage()

    def setFactor(self, factor):
        self.factor = factor
        self.invfactor = 1.0/factor

    def resetFactor(self):
        self.setFactor(700.0/float(max(self.image.width(),self.image.height())))

    def isSetImage(self):
        return self.factor != None

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.0001 or factor > 100:
            return
        print (factor)
        self.scale(scaleFactor, scaleFactor)
        for item in self.items():
            #print "setScale: ", 1.0/factor, factor
            item.setScale(1.0/factor)

    def getPoints(self):
        points = []
        i = 0
        for coord in self.shape.boundingPolygon().toList():
            if i != 4:
                points.append(coord.toTuple())
            i += 1
        return points

    def getPointsDest(self):
        return self.shape.getPointsDest()

    def getWidthDest(self):
        return self.shape.widthDest()

    def getHeightDest(self):
        return self.shape.heightDest()

    def boundingRect(self):
        return self.shape.boundingRectDest()

    def wheelEvent(self, event):
        if (event.delta() < 0):
            self.zoomOut()
        else:
            self.zoomIn()

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
    """

    def zoomIn(self):
        self.setFactor(self.factor * 1.25)
        self.scale(1.25, 1.25)

    def zoomOut(self):
        self.setFactor(self.factor * 0.75)
        self.scale(0.75, 0.75)

    def resetSizeImage(self):
        self.resetFactor()
        self.resetTransform()
        self.scale(self.factor,self.factor)

    def getScale(self):
        return self.invfactor

    def createNodesBase(self, points = None):

        node1 = Node(self, "n1")
        node2 = Node(self, "n2")
        node3 = Node(self, "n3")
        node4 = Node(self, "n4")
        #nodeC = Node(self, "nc")

        if (points != None):
            node1.setPos(points[0].pos().x(), points[0].pos().y())
            node2.setPos(points[1].pos().x(), points[1].pos().y())
            node3.setPos(points[2].pos().x(), points[2].pos().y())
            node4.setPos(points[3].pos().x(), points[3].pos().y())
        else:
            node1.setPos(200, 200)
            node2.setPos(400, 200)
            node3.setPos(400, 400)
            node4.setPos(200, 400)


        bezier12, bezier21 = node1.vincule(node2,ANGLES[0][1],ANGLES[1][0],self)
        bezier23, bezier32 = node2.vincule(node3,ANGLES[1][2],ANGLES[2][1],self)
        bezier34, bezier43 = node3.vincule(node4,ANGLES[2][3],ANGLES[3][2],self)
        bezier41, bezier14 = node4.vincule(node1,ANGLES[3][0],ANGLES[0][3],self)
        """
        node1.setZValue(10)
        node2.setZValue(10)
        node3.setZValue(10)
        node4.setZValue(10)
        """
        return [node1, node2, node3, node4]
        #return Shape(nodes, name, shapeDest)


    def createItems(self):

        points = self.points.getPoints()

        self.shapeDest = ShapeDest(self, self.createNodesBase(), "shBase")
        #self.widgetDest = WidgetDest(self.shapeDest)

        self.sceneDest = QtGui.QGraphicsScene()
        self.sceneDest.setSceneRect(0, 0, 0, 0)
        self.sceneDest.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.sceneDest.addItem(self.shapeDest)

        self.shape = Shape(self, self.createNodesBase(points), "shEdit", self.shapeDest)

        #self.widgetDest.show()

        self.scene().addItem(self.shape)
        for node in self.shape.getNodes():
            self.scene().addItem(node)
            for bezier in node.getBeziers():
                self.scene().addItem(bezier)

    def imageShapeDest(self):
        return self.shape.getShapeDest().getImage()

    def reset(self):
        print("reset")
        if(self.shape != None):
            self.scene().removeItem(self.shape)
            for node in self.shape.getNodes():
                self.scene().removeItem(node)
                for bezier in node.getBeziers():
                    self.scene().removeItem(bezier)
            self.shape = None

        self.points.removeAllPoints(self.scene())

        #self.scene().clicked.connect(self.scene().clickSelector)
        self.clicked.connect(self.clickSelector)
        self.clicked.disconnect(self.clickSelector)
        #print(self.transform())
        self.resetTransform()
        #print(self.transform())
        if (len(list(self.scene().items())) > 0):
            item = (list(self.scene().items()))[0]
            self.scene().removeItem(item)
            del item