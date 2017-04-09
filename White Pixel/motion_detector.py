# import packages
import argparse
import datetime
import imutils
import time
import cv2
from matplotlib import pyplot
import glob

# import videos
list_of_videos = glob.glob("/Users/David/Desktop/epics-sleep-video/23001_24M/23001_24M Sleep Videos/130903- Start of Night/*")

# initialize overall variables
no_of_videos = 0
plot_dict = {}
status = 0
status_list = []
num_frame = 0

# loop through all the videos
for video in list_of_videos:
		print video
		no_of_videos += 1

                # load video
		camera = cv2.VideoCapture(video)

                # initialize video variables
		valuable_pixels = 0
		previousFrame = None
		start = time.time()
		start_time_of_processing_video = time.time()
		
		# loop through all frames of video
		while True:
                    
			# grab the current frame and initialize the occupied/unoccupied
			(grabbed, frame) = camera.read()
			text = "Unoccupied"

			# if the frame could not be grabbed, then we have reached the end of video
			if not grabbed:
				break

			# resize the frame, convert it to grayscale, and blur it
			frame = imutils.resize(frame, width=500)
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			gray = cv2.GaussianBlur(gray, (21, 21), 0)

			# if the previous frame is None, initialize it
			if previousFrame is None:
				previousFrame = gray
				continue

			# compute the absolute difference between the current frame and previous frame
			frameDelta = cv2.absdiff(previousFrame, gray)

			# update previous
			previousFrame = gray

			# record time
			end = time.time()

			# update number of frames
			num_frame += 1

			# set threshhold, 25 is chosen at the moment, if difference is below 25, set to 0, if above, set to 255
			thresh = cv2.threshold(frameDelta, 40, 255, cv2.THRESH_BINARY)[1]
			# cv2.imshow("Thresh", thresh)
			
			# dilate the thresholded image to fill in holes, then find contours on thresholded image
			thresh = cv2.dilate(thresh, None, iterations=2)
			# cv2.imshow("Thresh after dilating", thresh)
			(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			 	cv2.CHAIN_APPROX_SIMPLE)
			
			# loop through contours
			no_contours = 0
			for c in cnts:
				no_contours += len(c)

                        # store number of contours based on time in seconds
			if round(num_frame/16.02) not in plot_dict.keys():
				plot_dict[round(num_frame/16.02)] = no_contours
				status_list.append(status)
				
			else:
				plot_dict[round(num_frame/16.02)] += no_contours

                        # plot number of contours
			list_of_contour_values = plot_dict.values()

			# calculate average number of contours in the last two minutes
			if (len(list_of_contour_values) < 120):
				average = sum(list_of_contour_values) / float(len(list_of_contour_values))
			else:
				average = sum(list_of_contour_values[-120:]) / float(120)

			print "Average number of contours in the past 2 minutes: " + str(average)

			# determine status, using 75 as threshold (chosen randomly at the moment)
			if average > 75:
				text = "Awake"
				status = 1
			else:
				text = "Asleep"
				status = 0

			# draw the text and timestamp on the frame
			cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

			#show the frame and record if the user presses a key
			cv2.imshow("Video", frame)
			cv2.imshow("Thresh", thresh)
			cv2.imshow("Frame Delta", frameDelta)
			key = cv2.waitKey(1) & 0xFF

			# if the `q` key is pressed, break from the loop
			if key == ord("q"):
				break

                # initialize two arrays
		x_values = []
		y_values = []

                # store the time in seconds as well as numbers of contours associated with that time
		for key, values in plot_dict.items():
			x_values.append(key)
			y_values.append(values)

# print time elapsed
print time.time() - start_time_of_processing_video

# plot data
pyplot.plot(x_values, y_values)
pyplot.ylabel('No. of Contours')
pyplot.xlabel('Time (seconds)')
pyplot.show()

pyplot.plot(x_values, status_list)
pyplot.ylabel('Status')
pyplot.xlabel('Time (seconds)')
pyplot.show()

# release the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
