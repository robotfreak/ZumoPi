# USAGE
# python track.py --video video/iphonecase.mov

# import the necessary packages
from pyfirmata import Arduino, util
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import argparse
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

# connect to Arduino board
board = Arduino('/dev/ttyACM0')
board.digital[13].write(1)

# set up pin D4, D12 as Servo Output
pan = board.get_pin('d:4:s')
tilt = board.get_pin('d:12:s')
 
def move_pan(a):
    pan.write(a)

def move_tilt(a):
    tilt.write(a)

def arduino_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min



# center servos
move_pan(90)
move_tilt(90)

# define the upper and lower boundaries for a color
# to be considered "blue"
blueLower = np.array([100, 67, 0], dtype = "uint8")
blueUpper = np.array([255, 128, 50], dtype = "uint8")

# initialize the camera and grab a reference to the raw camera
# capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# load the video
#camera = cv2.VideoCapture(args["video"])
framenum = 0
# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array
	framenum = framenum+1

	# determine which pixels fall within the blue boundaries
	# and then blur the binary image
	blue = cv2.inRange(frame, blueLower, blueUpper)
	blue = cv2.GaussianBlur(blue, (3, 3), 0)

	# find contours in the image
	(_, cnts, _) = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# check to see if any contours were found
	if len(cnts) > 0:
		# sort the contours and find the largest one -- we
		# will assume this contour correspondes to the area
		# of my phone
		cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

		# compute the (rotated) bounding box around then
		# contour and then draw it		
		rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
		cv2.drawContours(frame, [rect], -1, (0, 255, 0), 2)
		if framenum % 4 == 0:
                        print(rect);
			#move_pan(arduino_map(rect[0].x, 0, 640, 45, 135));
			#move_tilt(arduino_map(rect[0].y, 0, 480, 45, 135));
                

	# show the frame and the binary image
	cv2.imshow("Tracking", frame)
	cv2.imshow("Binary", blue)
	rawCapture.truncate(0)

	# if your machine is fast, it may display the frames in
	# what appears to be 'fast forward' since more than 32
	# frames per second are being displayed -- a simple hack
	# is just to sleep for a tiny bit in between frames;
	# however, if your computer is slow, you probably want to
	# comment out this line
	time.sleep(0.025)

	# if the 'q' key is pressed, stop the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
