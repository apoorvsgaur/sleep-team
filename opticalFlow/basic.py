#basic inputting of video with opencv

import cv2

# setup video capture
cap = cv2.VideoCapture(0)

while True:
  ret,im = cap.read()
  cv2.imshow('video test',im)
  
  #press esc to quit and space to store a frame
  key = cv2.waitKey(10)
  if key == 27:
    break
  if key == ord(' '):
    cv2.imwrite('vid_result.jpg',im)

cap.release()
cv2.destroyAllWindows()

