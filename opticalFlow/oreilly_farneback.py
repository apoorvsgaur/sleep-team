#gunnar farneback optical flow

import cv2
from numpy import *
import datetime

#special imports for matplot with virtual environment
import matplotlib as mpl  
mpl.use('TkAgg')
import matplotlib.pyplot as plt

#plotting function script
import plotting


def draw_flow(im, flow, step=16):
    h,w = im.shape[:2]
    y,x = mgrid[step/2:h:step,step/2:w:step].reshape(2,-1)
    fx,fy = flow[y,x].T
    
    # create line endpoints
    lines = vstack([x,y,x+fx,y+fy]).T.reshape(-1,2,2)
    lines = int32(lines)

    # create image and draw
    vis = cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
    for (x1,y1),(x2,y2) in lines:
        cv2.line(vis,(x1,y1),(x2,y2),(0,255,0),1)
        cv2.circle(vis,(x1,y1),1,(0,255,0), -1)
    return vis

def optical_flow(video):    
    #get video
    cap = cv2.VideoCapture(video)

    #get initial frame
    ret,im = cap.read()
    prev_gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

    pcv = 0 #plotting control variable
    flowSum = 0 #adds up flow of 16 frames
    timer = 1 #timer

    while True:
        # get next frame
        ret,im = cap.read()
        next_gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

        # compute flow and move to next frame
        flow = cv2.calcOpticalFlowFarneback(prev_gray,next_gray,float(0),float(0),3,15,3,5,float(1),0)
        flowSum += flow
        prev_gray = next_gray

        # plot the flow vectors
        #cv2.imshow('original', next_gray)
        #cv2.imshow('Optical flow',draw_flow(next_gray, flow))
        #if cv2.waitKey(30) == 27:
        #    break

        pcv += 1
        
        #16 comparisons
        if pcv == 15:
            #testing: calculating and plotting displacement
            print "Distance = " + str(plotting.findDistance(next_gray, flowSum)) + " time = " + str(timer)

            #reset variables
            pcv = 0
            flowSum = 0
            timer += 1

            

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        optical_flow(sys.argv[1])
