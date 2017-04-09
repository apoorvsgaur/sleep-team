# importing the packages
import argparse
import datetime
import imutils
import time
import cv2
from matplotlib import pyplot
import numpy as np
import glob


#given folder path, compile all paths of videos
folder_path = "/Users/apoorvsgaur/Desktop/Apoorv/Classes/Spring 2016/EPICS/epics-sleep-video/23001_24M/*"
#def contouring_processing(folder_path):
list_of_videos =  glob.glob(folder_path)

#Variables used in the program
no_of_videos = 0 #To keep count of videos processed through
plot_dict = {} #Dictionary to keep count of number of contours per second
sleep_dict = {} #Dictionary to keep count of sleep status at each second
status = 0 #Status of sleep at any second
frame_count = 0 #keeping count of frames processed
contours_in_the_last_60_seconds = 0 #Activity Count
no_of_videos_in_folder_path = len(list_of_videos)
start_time_of_processing_video = time.time()

#video = cv2.VideoWriter('.avi',-1,1,(width,height))

for video in list_of_videos:
				#print video
				no_of_videos += 1
				print (no_of_videos)
				#if (no_of_videos == 2):
				#	break
				camera = cv2.VideoCapture(video)

				previousFrame = None
				start = time.time()

				# loop over the frames of the video
				while True:
					# grab the current frame
					(grabbed, frame) = camera.read()

					# if the frame could not be grabbed, then we have reached the end
					# of the video
					if not grabbed:
						break

					#convert it to grayscale
					gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
					gray = cv2.GaussianBlur(gray, (21, 21), 0)

					# if the previousFrame is None, initialize it
					if previousFrame is None:
						previousFrame = gray #
						continue

					# compute the absolute difference between the current frame and previous frame
					frameDelta = cv2.absdiff(previousFrame, gray)

					#Absolute Difference has been calculated, hence currentFrame is now previousFrame
					previousFrame = gray

					#Updating frame count
					frame_count = frame_count + 1

					#Thresholding Frame Difference
					thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

					#Finding number of contours in thresholded frame difference
					(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
					 	cv2.CHAIN_APPROX_SIMPLE)

					no_contours = 0
					for c in cnts:
						no_contours += len(c)

					#no_white_pixels = np.count_nonzero(thresh)
					second = round(frame_count/16.02) #Camera frames at 16 frames per second (16.02 was tested to be more accurate)


					#Keeping track of no_of_white pixels per second and Sleep status at a given second
					if  second not in plot_dict.keys():
						plot_dict[second] =	no_contours
						sleep_dict[second] = status
						print (str(frame_count) + ": " + str(round(frame_count/16.02)) + " No. of contours:" + str(no_contours))

					else:
						plot_dict[second] += no_contours
						sleep_dict[second] = status
						print (str(frame_count) + ": " + str(round(frame_count/16.02)) + " No. of contours:" + str(no_contours))



					#Calculating average number of white pixels over the past 2 minutes (120 seconds)
					list_of_contour_values = plot_dict.values()
					if (len(list_of_contour_values) < 120):
						average = round(sum(list_of_contour_values) / float(len(list_of_contour_values)))
					else:
						average = round(sum(list_of_contour_values[-120:]) / float(120))


					#print "Average number of contours in the past 2 minutes: " + str(average)
					if average > 75:
						text = "Awake"
						status = 1
					else:
						text = "Asleep"
						status = 0

					# draw the text and timestamp on the frame
					#cv2.putText(frame, "Sleep Status: {}".format(text), (10, 20),
					#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
					#cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
					#	(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

					#show the frame and record if the user presses a key
					#cv2.imshow("Video", frame)
					#cv2.imshow("Thresh", thresh)
					#cv2.imshow("Grayscale Equivalent", gray)
					#cv2.imshow("Frame Delta", frameDelta)

					#Exaggerated frameDelta for presentation
					#cv2.imshow("Frame Delta", 5*frameDelta)
					key = cv2.waitKey(1) & 0xFF

					# if the `q` key is pressed, break from the lop
					if key == ord("q"):
						break

				x_values= []
				y_values = []

				for key, values in plot_dict.items():
					x_values.append(key) #For testing, values for x axis of histogram (time in seconds)
					y_values.append(values) #For testing, values for y axis of histogram (No. of contours that second)

print ("Total Processing time of video: " + str(time.time() - start_time_of_processing_video) + "seconds")

f = open("23003_15M_Fall_2016.txt", "w")
f.write("Time    Activity  	Sleep Status\n")

#Calculating Activity Count and storing the results in a file
for seconds, no_of_contours in plot_dict.items():
	contours_in_the_last_60_seconds += no_of_contours
	if (seconds % 60 == 0):
		f.write(str(round(seconds/60)) + "m     "	+ str(round(contours_in_the_last_60_seconds/60)) + "    " + str(sleep_dict[seconds]) + "\n")
		contours_in_the_last_60_seconds = 0

f.close()


#Plotting histogram
pyplot.plot(x_values, y_values)
pyplot.ylabel('No. of Contours')
pyplot.xlabel('Time (seconds)')
#pyploy.axis('tight')
pyplot.show()

#pyplot.plot(x_values, status_list)
#pyplot.ylabel('Status')
#pyplot.xlabel('Time (seconds)')
#pyplot.show()


# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
