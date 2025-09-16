from computervision_new import findBiggestSkincellFileName, onSkincellFile
import cv2

cv2.imread("images/currentPosition.JPG")

oncell = onSkincellFile("images/currentPosition.JPG")
print("Currently on skincell is: ", oncell)