import serial

s = serial.Serial("/dev/ttyACM0", 115200)

while True:
    print "reading"
    print s.readline()
