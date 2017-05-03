# USAGE
# python track.py --video video/iphonecase.mov

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from pantilt import *
import numpy as np
import argparse
import time
import math
import cv2

def nothing(x):
    pass


def hsv2rgb(h, s, v):
    h = float(h * 2.0)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b

def h2rgb(h):
    h = h * 2
    if h < 61:
        r = 255
	b = 0
	g = 4.25 * h
    elif h < 121:
	g = 255
	b = 0
	r = 255 - (4.25 * (h-60))
    elif h < 181:
	r = 0
	g = 255
	b = 4.25 * (h-120)
    elif h < 241:
	r = 0
	b = 255
	g = 255 - (4.25 * (h-180))
    elif h < 301:
	g = 0
	b = 255
	r = 4.25 * (h-240)
    elif h< 360:
	r = 255;
	g = 0;
	b = 255 - (4.25 * (h-300));
    return r, g, b
		



# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

# define the upper and lower boundaries for a color
# to be considered "red"
#redLower = np.array([ 17, 15,100], dtype = "uint8")
#redUpper = np.array([ 50, 56,200], dtype = "uint8")
lower = np.array([0,0,0], dtype = "uint8")
upper = np.array([179,255,255], dtype = "uint8")

rgb = np.array([0,0,0], dtype = "uint8")
# Frame Size. Smaller is faster, but less accurate.
# Wide and short is better, since moving your head
# vertically is kinda hard!
FRAME_W = 320
FRAME_H = 240

# Default Pan/Tilt for the camera in degrees.
# Camera range is from 0 to 180
cam_pan = 90
cam_tilt = 90

# center servos
servoPan(cam_pan)
servoTilt(cam_tilt)


cv2.namedWindow('Tracking')

# create trackbars for color change
cv2.createTrackbar('V up','Tracking',upper[2],255,nothing)
cv2.createTrackbar('S up','Tracking',upper[1],255,nothing)
cv2.createTrackbar('H up','Tracking',upper[0],179,nothing)
cv2.createTrackbar('V low','Tracking',lower[2],255,nothing)
cv2.createTrackbar('S low','Tracking',lower[1],255,nothing)
cv2.createTrackbar('H low','Tracking',lower[0],179,nothing)

# initialize the camera and grab a reference to the raw camera
# capture
camera = PiCamera()
camera.resolution = (FRAME_W, FRAME_H)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(FRAME_W, FRAME_H))
framenum = 0

# load the video
#camera = cv2.VideoCapture(args["video"])

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array
	framenum = framenum + 1

	upper[2] = cv2.getTrackbarPos('V up','Tracking')
	upper[1] = cv2.getTrackbarPos('S up','Tracking')
	upper[0] = cv2.getTrackbarPos('H up','Tracking')
	lower[2] = cv2.getTrackbarPos('V low','Tracking')
	lower[1] = cv2.getTrackbarPos('S low','Tracking')
	lower[0] = cv2.getTrackbarPos('H low','Tracking')

	# determine which pixels fall within the red boundaries
	# and then blur the binary image
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS_FULL)
        color = cv2.inRange(hsv, lower, upper)
	# red = cv2.inRange(frame, redLower, redUpper)
	color = cv2.GaussianBlur(color, (3, 3), 0)

	# find contours in the image
	(_, cnts, _) = cv2.findContours(color.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# check to see if any contours were found
	for i,c in enumerate(cnts):
		# sort the contours and find the largest one -- we
		# will assume this contour correspondes to the area
		# of my phone
		cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

		# compute the (rotated) bounding box around then
		# contour and then draw it		
		#rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
		#cv2.drawContours(frame, [rect], -1, (0, 255, 0), 2)
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                print("Contour #{} -- area: {:.2f}, perimeter: {:.2f}".format((i + 1), area, perimeter))

                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                print(radius)
                #if framenum % 4 == 0:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
		
                print cX, cY
                # object is to the left
                if (cX > (FRAME_W/2) + 20):
                        if (cam_pan >= 60):
                                cam_pan -= 2
                # object is to the right
                else :
                        if (cX < (FRAME_W/2) - 20):
                                if (cam_pan <= 120):
                                        cam_pan += 2
                servoPan(cam_pan)
                rgb = h2rgb(lower[0])
                print rgb
                break

	# show the frame and the binary image
	cv2.imshow("Tracking", frame)
	cv2.imshow("Binary", color)
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
