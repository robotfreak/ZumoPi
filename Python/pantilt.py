import piconzero as pz, time

pan = 0
tilt = 1

def servoPan(a):
    pz.setOutput (pan, a)

def servoTilt(a):
    pz.setOutput (tilt, a)

pz.init()

# Set output mode to Servo
pz.setOutputConfig(pan, 2)
pz.setOutputConfig(tilt, 2)

# Centre all servos
panVal = 90
tiltVal = 90
pz.setOutput (pan, panVal)
pz.setOutput (tilt, tiltVal)


