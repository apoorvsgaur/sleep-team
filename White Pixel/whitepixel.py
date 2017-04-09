# this Python script uses the white pixels method to detect motion and estimate sleep status

# import libraries
import numpy as np
import cv2

# print OpenCV version
print cv2.__version__

# initialize variables (default values)
frame_count = 0
time = 0
previous_time = 0
pixel_min = 0
total_diff = 0
thresh_x = 25
minute = {}
status = {}
previousFrame = None

# load in video (change location and file name as appropriate)
cap = cv2.VideoCapture("C:/Users/David/Desktop/sleep/output.avi")

# get video properties
# get width and height aspects of video
width = cap.get(3)
height = cap.get(4)

# get frames per second
fps = cap.get(cv2.CAP_PROP_FPS)

# get total number of pixels in a frame
total_pixel = width * height

# check if video is loaded
print cap.isOpened()

# loop to process all frames
while(cap.isOpened()):
    
    # load in frame
    ret, frame = cap.read()

    # check for end of video
    if ret is False:
        minute[previous_time] = pixel_min
        break;

    # convert frame to grayscale from rgb
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # reducing noise effects with Gaussian blurring
    blur = cv2.GaussianBlur(gray, (21, 21), 0)

    # set up previous frame
    if previousFrame is None:
        previousFrame = blur
        continue

    # calculate differences between two consecutive frames
    frameDelta = cv2.absdiff(previousFrame, blur)

    # calculate total value of frame
    total_diff = np.sum(frameDelta)

    # update previous frame
    previousFrame = blur

    # calculate threshold for white pixels (to ignore lighting changes in video)
    thresh_x = total_diff / total_pixel + 25

    # convert difference frame to white pixels frame with calculated threshold
    thresh = cv2.threshold(frameDelta, thresh_x, 255, cv2.THRESH_BINARY)[1]

    # count number of white pixels
    white_pixels = np.count_nonzero(thresh)

    # update number of frames
    frame_count += 1

    # calculate time in minutes
    time = int(frame_count/fps/60)

    # calculate number of white pixels per minute
    # add white pixels in a minute
    if previous_time == time:
        pixel_min += white_pixels
    # update previous minute
    else:
        minute[previous_time] = pixel_min
        pixel_min = 0
        previous_time = time

    # show frames being processed
    # cv2.imshow('frame',frame)
    # cv2.imshow('gray',gray)
    # cv2.imshow('blur',gray)
    # cv2.imshow('thresh',thresh)

    # press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # press p to pause, enter to continue
    if cv2.waitKey(1) & 0xFF == ord('p'):
        raw_input("Press Enter to continue...")

# estimate status (difference between awake and asleep are very large regarding the number of white pixels, 100000 is a good value from experimenting)
for p in minute:
    if minute[p] > 100000:
        status[p] = 1
    else:
        status[p] = 0
        
# opening file to write
output = open('wp_output.txt','w')

# print table of outputs
print "Time(minutes)     Number of White Pixels      Status"

for p in minute:
    print '%-17s' % (p+1),
    print '%-27s' % minute[p],
    if status[p] == 1:
        print "Awake"
    else:
        print "Asleep"

# write table of outputs into file
output.write("Time(minutes)     Number of White Pixels      Status\n")

for p in minute:
    output.write('%-18s' % (p+1)),
    output.write('%-28s' % minute[p]),
    if status[p] == 1:
        output.write("Awake\n")
    else:
        output.write("Asleep\n")

# exit
output.close()
cap.release()
cv2.destroyAllWindows()
