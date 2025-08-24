#!/usr/bin/env python3
# coding=utf8
import evdev
import math
import sys
import time
import logging
import pprint
sys.path.append('/home/tah/GitHub/TAH-ROBOT')
sys.path.append('/home/tah/GitHub/TAH-ROBOT/servos')
from servos import Servos

class Gamepad:
    '''
    8BitDo SN30Pro 
    Appears as X-box controller on the Rpi5.
    '''
    def __init__(
        self, 
        control_servos: bool = True,
        servos_instance : Servos = None,
        logfile: str = "gamepad.log"
    ):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)

        found_gamepad = False
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if 'X-Box' in device.name:
                found_gamepad = True
                break
        if found_gamepad: 
            self.gamepad = evdev.InputDevice(device.path)
        else :
            raise RuntimeError(f"Failed to initialize gamepad.")
        gamepad_str = pprint.pformat(self.gamepad.capabilities(verbose=True))
        self.logger.info(gamepad_str)

        if control_servos:
            self.control_servos = control_servos
            self.servos         = servos_instance
            self.servos.servo0.angle = 90
            self.servos.servo1.angle = 90
            # RIGHT STICK
            # LINEAR MAPING OF STICK (MIN,MAX) -> (0,180) DEGREES
            absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RX)
            self.mx = 180.0/math.fabs(absinfo.max-absinfo.min)
            self.bx = -self.mx*absinfo.min
            absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RY)
            self.my = 180.0/math.fabs(absinfo.max-absinfo.min)
            self.by = -self.my*absinfo.min
# -----------------------------------

# -----------------------------------
    def run(self):
        x=0
        y=0
        running = True
        while running:
            event = self.gamepad.read_one()
            if event :
                if event.code == evdev.ecodes.BTN_MODE and event.value == 0:
                    running = False
                if event.type ==  evdev.ecodes.EV_ABS and self.control_servos:
                    if event.code == evdev.ecodes.ABS_RY : y=event.value
                    if event.code == evdev.ecodes.ABS_RX : x=event.value
                    deg_x = math.trunc(self.mx*x+self.bx)
                    deg_y = math.trunc(self.mx*y+self.by)
                    self.servos.servo0.angle = deg_x
                    self.servos.servo1.angle = deg_y
                    time.sleep(0.005)
                    #print(f"{deg_x} {deg_y}")
# -----------------------------------

if __name__ == "__main__":

    my_servos= Servos()
    my_gamepad = Gamepad(servos_instance=my_servos)
    my_gamepad.run()
    my_servos.deinit()

