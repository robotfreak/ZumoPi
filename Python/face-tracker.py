# USAGE
# python webcam.py --face cascades/haarcascade_frontalface_default.xml

# import the necessary packages
from pantilt import *
from facedetector import *
from imutils import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import time
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", required = True,
	help = "path to where the face cascade resides")
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

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
pan(cam_pan)
tilt(cam_tilt)

# initialize the camera and grab a reference to the raw camera
# capture
camera = PiCamera()
camera.resolution = (FRAME_W, FRAME_H)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(FRAME_W, FRAME_H))

# construct the face detector and allow the camera to warm
# up
fd = FaceDetector(args["face"])
time.sleep(0.1)
framenum = 0

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array
	framenum = framenum+1

	# resize the frame and convert it to grayscale
	frame = imutils.resize(frame, width = 300)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces in the image and then clone the frame
	# so that we can draw on it
	faceRects = fd.detect(gray, scaleFactor = 1.1, minNeighbors = 5,
		minSize = (30, 30))
	frameClone = frame.copy()

	# loop over the face bounding boxes and draw them
	for (x, y, w, h) in faceRects:
                cv2.rectangle(frameClone, (x, y), (x + w, y + h), (0, 255, 0), 2)
		#if framenum % 8 == 0:
                # Track first face
        
                # Get the center of the face
                mid_x = x + (w/2)
                mid_y = y + (h/2)

                # face is to the left
                if (mid_x > (FRAME_W/2) + 20):
                        if (cam_pan >= 20):
                                cam_pan -= 2
                # face is to the right
                else :
                        if (mid_x < (FRAME_W/2) - 20):
                                if (cam_pan <= 160):
                                        cam_pan += 2

                # face is upper
                if (mid_y < (FRAME_H/2) - 20):
                        if (cam_tilt >= 40):
                                cam_tilt -= 2
                # face is lower
                else :
                        if (mid_y > (FRAME_H/2) + 20):
                                if (cam_tilt <= 140):
                                        cam_tilt += 2

                # Clamp Pan/Tilt to 0 to 180 degrees
                cam_pan = max(0,min(180,cam_pan))
                cam_tilt = max(0,min(180,cam_tilt))
                print ("x: ", x, mid_x, cam_pan)
                print ("y: ", y, mid_y, cam_tilt)
                # Update the servos
                pan(cam_pan)
                tilt(cam_tilt)

                break

	# show our detected faces, then clear the frame in
	# preparation for the next frame
	cv2.imshow("Face", frameClone)
	rawCapture.truncate(0)

	# if the 'q' key is pressed, stop the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break
