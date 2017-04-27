#! /usr/bin/env python
#
# Basic test of HC-SR04 ultrasonic sensor on Picon Zero

import piconzero as pz, hcsr04, time

def distance2Pixel(dist):
        pz.setAllPixels(0,0,0)
	if (dist > 80):
		dist = 80
	if (dist < 15):
		green = 0
		red = 255
		blue = 0
	elif (dist < 30):
		green = 165
		red = 255
		blue = 0
	else:
		green = 255
		red = 0
		blue = 0

        for i in range(8-dist/10):
		pz.setPixel(i,red,green,blue)

#	if (dist >= 80):
#		pz.setPixel(7,0,255,0)
#	if (dist >= 70):
#		pz.setPixel(6,0,255,0)
#	if (dist <= 60):
#		pz.setPixel(5,0,255,0)
#	if (dist <= 50):
#		pz.setPixel(4,0,255,0)
#	if (dist <= 40):
#		pz.setPixel(3,0,255,0)
#	if (dist <= 30):
#		pz.setPixel(2,0,255,0)
#	if (dist <= 20):
#		pz.setPixel(1,0,255,0);
#	else:
#		pz.setPixel(0,0,255,0);

pz.init()
pz.setOutputConfig(5, 3)    # set output 5 to WS2812
rev = pz.getRevision()
print(rev[0], rev[1])
hcsr04.init()

try:
    while True:
        distance = int(hcsr04.getDistance())
        print "Distance:", distance
        distance2Pixel(distance) 
        time.sleep(1)
except KeyboardInterrupt:
    print
finally:
    hcsr04.cleanup()

