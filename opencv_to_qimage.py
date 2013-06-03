import sys
import cv2
from PySide.QtGui import QImage


img_cv = cv2.imread(sys.argv[1])

print "Source image type: %s" % type(img_cv)
print "Source data type %s" % img_cv.dtype

dst = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

print "Destnation image type: %s" % type(dst)
print "Destination data type %s" % dst.dtype

h = dst.shape[0]
w = dst.shape[1]
qim = QImage(dst.data, w, h, dst.strides[0], QImage.Format_RGB888)

qim.save("out.jpg")
