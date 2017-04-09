# import packages
import numpy as np
import cv2
import time
import glob

# initialize values
previous = None

# load video
cap = cv2.VideoCapture('C:/Users/David/Desktop/sleep/test.avi')
# cap = cv2.VideoCapture(0)

# initiating background subtraction method
fgbg = cv2.createBackgroundSubtractorMOG()

# loop through all frames
while(cap.isOpened()):
    
    # read frame
    ret, frame = cap.read()

    # background subtraction using MOG
    fgmask = fgbg.apply(frame)

    cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff

    if k == 27:
        break

    # convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # show grayscale frames
    cv2.imshow('frame', gray)

    # initialize previous
    if (previous is None):
        previous = gray

    # calculate difference
    # diff = abs(gray - previous)
    diff = cv2.absdiff(previous, gray)
    cv2.imshow('frame difference', diff)

    # use threshold, greater than 25 becomes 255, less than 25 becomes 0
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow('frame difference with threshold', thresh)

    # count number of different pixels (this block of code slows everything down)
    diff_pix = 0
    for x in thresh:
        for y in x:
            if (y == 255):
                diff_pix += 1;

    print diff_pix

    # next I will determine a threshold for the number of different pixels to determine
    # movement, and calculate the numbers of movement in a minute to determine
    # awake or asleep
    
    # update previous
    previous = gray
    
    # press q to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release camera and close all windows
cap.release()
cv2.destroyAllWindows()
