#Script to understand how to plot using matplotlib
import cv2
from numpy import *
import math

#special imports for matplot with virtual environment
import matplotlib as mpl  
mpl.use('TkAgg')
import matplotlib.pyplot as plt

def findDistance(im, flow, step=16):
	h,w = im.shape[:2]
	y,x = mgrid[step/2:h:step,step/2:w:step].reshape(2,-1)
	fx,fy = flow[y,x].T
	 
	#calculate distance
	distance = sqrt(fx**2 + fy**2)
	
	#find number of points
	number_of_points = len(distance)

	#calculate average distance moved per second
	total_distance = 0
	for points in distance:
		total_distance += points

	return total_distance/number_of_points