#!/usr/bin/env python3
# coding=utf8
import evdev
import math
import sys
import time
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos

found_gamepad = False
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if 'X-Box' in device.name:
        found_gamepad = True
        break
if found_gamepad: gamepad = evdev.InputDevice(device.path)
else: quit()
#print(gamepad)
#print(gamepad.capabilities(verbose=True))

servos = Servos()

# LEFT STICK : LINEAR MAPING OF STICK (MIN,MAX) -> (0,180) DEGREES
absinfo = gamepad.absinfo(evdev.ecodes.ABS_X)
mx = 180.0/math.fabs(absinfo.max-absinfo.min)
bx = -mx*absinfo.min
absinfo = gamepad.absinfo(evdev.ecodes.ABS_Y)
my = 180.0/math.fabs(absinfo.max-absinfo.min)
by = -my*absinfo.min

# RIGHT STICK
absinfo = gamepad.absinfo(evdev.ecodes.ABS_RX)


x=0
y=0
while True:
    event = gamepad.read_one()
    if event :
        if event.type ==  evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_Y :
                y=event.value
            if event.code == evdev.ecodes.ABS_X:
                x=event.value
            deg_x = math.trunc(mx*x+bx)
            deg_y = math.trunc(mx*y+by)
            servos.servo0.angle = deg_x
            servos.servo1.angle = deg_y
            #time.sleep(0.005)
            #print(f"{deg_x} {deg_y}")
