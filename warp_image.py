import cv2
import numpy as np
import sys

def warpImage(image, corners, target, width, height):
    mat_trans = cv2.getPerspectiveTransform(np.asarray(corners, dtype=np.float32), np.asarray(target, dtype=np.float32))
    size = (width, height)
    return cv2.warpPerspective(image, M=mat_trans, dsize=size, flags=cv2.INTER_CUBIC)

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
