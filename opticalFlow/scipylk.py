# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 11:23:57 2016
script for lucas kanade without using opencv(with exception of video and frame capturing)
As of current still incomplete
@author: Ian Lioe
"""

import cv2
import numpy as np
import scipy.signal as si

cap = cv2.VideoCapture(0) #capture webcam 
ret, frame1 = cap.read() #return frame 1 from webcam
ret, frame2 = cap.read() #return frame 2 from webcam

#Make gradient Images
def gauss_kern(): #function to create gaussian window to find corners
   h1 = 15
   h2 = 15
   x, y = np.mgrid[0:h2, 0:h1]
   x = x-h2/2
   y = y-h1/2
   sigma = 1.5
   g = np.exp( -( x**2 + y**2 ) / (2*sigma**2) );# gaussian window function
   return g / g.sum()
   
#Make gradient Images
Gx = np.matrix([[-1,1],[-1,1]]) #matrix for convolving with image to create gradient image in x
Gy = np.matrix([[-1,-1],[1,1]]) #matrix for convolving with image to create gradient image in y
Gt = np.matrix([[1,1],[1,1]])# matrix for convolving with image to find time gradient
Ix = si.convolve2d(frame1,Gx,mode='full', boundary='fill', fillvalue=0) #gradient matrix in x
Iy = si.convolve2d(frame1,Gy,mode='full', boundary='fill', fillvalue=0) #gradient matrix in y
It = si.convolve2d(frame1,Gt,mode='full', boundary='fill', fillvalue=0)+si.convolve2d(frame2,-Gt,mode='full', boundary='fill', fillvalue=0)#Partial derivative in time





