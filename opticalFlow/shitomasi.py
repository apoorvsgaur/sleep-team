#implementation of shitomasi corner points algorithm

import numpy as np
import cv2

#macosx matplotlib special import specs
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt


#get first frame from video and change to gray scale
cap = cv2.VideoCapture("203959_1.AVI")
while True:
	ret,im = cap.read()
	gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
	

	#get shitomasi corner detection
	corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
	corners = np.int0(corners) #convert to integers

	for i in corners:
		x, y = i.ravel()
		cv2.circle(gray, (x,y), 3, 255, -1) #draw circles to represent the points

	
	cv2.imshow('Shi-tomasi corner points', gray)
	if cv2.waitKey(30) == 27:
		break


cap.release()
cv2.destroyAllWindows()
	#plt.imshow(im),plt.show()	#plot with matlab