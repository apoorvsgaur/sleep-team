#optical flow with Farneback method
#shows movement in very dense view


import cv2
import numpy as np
cap = cv2.VideoCapture("203959_1.AVI") #capture video
     
ret, frame1 = cap.read()  #get frame
prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY) #change to grayscale
hsv = np.zeros_like(frame1)
hsv[...,1] = 255
     
while(1):
  ret, frame2 = cap.read()
  cv2.imshow('frame1', frame2)
  next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
   
  flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    
  mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
  hsv[...,0] = ang*180/np.pi/2
  hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
  bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    
  cv2.imshow('frame2', bgr)
  
  #Waits 30 milliseconds if esc is pressed it quits, if s is pressed it saves the frame
  key  = cv2.waitKey(30) & 0xff
  if key == 27:
    break
  elif k == ord('s'):
    cv2.imwrite('opticalfb.png',frame2)
    cv2.imwrite('opticalhsv.png',bgr)
    prvs = next
    
cap.release()
cv2.destroyAllWindows()