import cv2
import numpy as np
import sys
from PySide import QtGui

def warpImage(image, corners, target, width, height):
    mat_trans = getMat(np.asarray(corners, dtype=np.float32), np.asarray(target, dtype=np.float32))
    size = (width, height)
    return cv2.warpPerspective(image, M=mat_trans, dsize=size, flags=cv2.INTER_CUBIC)

def getMat(corners, target):
    return cv2.getPerspectiveTransform(np.asarray(corners, dtype=np.float32), np.asarray(target, dtype=np.float32))


def proyectCoord(coord, mat):
    x = proyectX(coord.x(), coord.y(), mat)
    y = proyectY(coord.x(), coord.y(), mat)
    print "proyectPos: %s ----> (%f, %f)"% (coord.toTuple(), x, y)
    coord.setX(x)
    coord.setY(y)
    return coord

def proyectPolygon(polygon, mat):
    newPolygon = QtGui.QPolygonF()
    for coord in polygon.toList():
        newCoord = proyectCoord(coord, mat)
        newPolygon.append(newCoord)
    #print "newPolygon: ", newPolygon.toList()
    return newPolygon
   
def proyectX(x, y, mat):
    return (mat[0,0] * x + mat[0,1] * y + mat[0,2])/(mat[2,0] * x + mat[2,1] * y + mat[2,2])

def proyectY(x, y, mat):
    return (mat[1,0] * x + mat[1,1] * y + mat[1,2])/(mat[2,0] * x + mat[2,1] * y + mat[2,2])

if __name__ == '__main__':
    """
    Los puntos de corners, se mapean a los de target. corners[0] va a ir a target[0] y asi.
    """
    width, height = 600, 600
    corners = [(268,330),(609,0),(697,511),(382,607)]
    target = [(0,0),(width,0),(width,height),(0,height)]
    image = cv2.imread(sys.argv[1])
    out = warpImage(image, corners, target, width, height)
    cv2.imshow("image", out)
    cv2.waitKey()
