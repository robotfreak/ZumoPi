from pyfirmata import Arduino, util

# connect to Arduino board
board = Arduino('/dev/ttyACM0')
board.digital[13].write(1)

def pan(a):
    panServo.write(a)

def tilt(a):
    tiltServo.write(a)

# set up pin D4, D12 as Servo Output
panServo = board.get_pin('d:4:s')
pan(90)
tiltServo = board.get_pin('d:12:s')
tilt(90)
 

def arduino_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
