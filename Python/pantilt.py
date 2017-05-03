import piconzero as pz, hcsr04, time 

pan = 0
tilt = 1
pixel = 5

def servoPan(a):
    pz.setOutput (pan, a)

def servoTilt(a):
    pz.setOutput (tilt, a)

def setNeoPixel(pixel, rgb):
    r, g, b = rgb
    pz.setPixel(pixel, int (r), int(g), int(b))

def getDistance():
    return hcsr04.getDistance()  
    
pz.init()

# Set output mode to Servo
pz.setOutputConfig(pan, 2)
pz.setOutputConfig(tilt, 2)
# set output 5 to WS2812
pz.setOutputConfig(pixel, 3)    
hcsr04.init()

# Centre all servos
panVal = 90
tiltVal = 90
pz.setOutput (pan, panVal)
pz.setOutput (tilt, tiltVal)


