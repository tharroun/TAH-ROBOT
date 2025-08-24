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
sys.path.append('/home/tah/GitHub/TAH-ROBOT/motors')
from motors import Motors

class Gamepad:
    '''
    8BitDo SN30Pro 
    Appears as X-box controller on the Rpi5.
    '''
    def __init__(
        self, 
        control_servos  : bool = True,
        servos_instance : Servos | None = None,
        control_motors  : bool = True,
        motors_instance : Motors | None = None,
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
            if servos_instance != None : 
                self.servos = servos_instance
            else : 
                raise RuntimeError(f"Must supply a valid servo instance, or set control_servos to False.")
            self.servos.servo0.angle = 90
            self.servos.servo1.angle = 90
            # RIGHT STICK
            # LINEAR MAPING OF STICK (MIN,MAX) -> (0,180) DEGREES
            absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RX)
            self.servos_mx = 180.0/math.fabs(absinfo.max-absinfo.min)
            self.servos_bx = -self.servos_mx*absinfo.min
            absinfo = self.gamepad.absinfo(evdev.ecodes.ABS_RY)
            self.servos_my = 180.0/math.fabs(absinfo.max-absinfo.min)
            self.servos_by = -self.servos_my*absinfo.min
# -----------------------------------

# -----------------------------------
    def run(self):
        x=0
        y=0
        running = True
        while running:
            event = self.gamepad.read_one()
            if event :
                # Use the mode button *and* the button-up action to quit the program
                # If we don't use the button-up action, it remains in the queue, and the next
                # time the program runs, it quits!
                if event.code == evdev.ecodes.BTN_MODE and event.value == 0:
                    running = False
                # Right joytick controls the servos.
                if event.type ==  evdev.ecodes.EV_ABS and self.control_servos:
                    if event.code == evdev.ecodes.ABS_RY : y=event.value
                    if event.code == evdev.ecodes.ABS_RX : x=event.value
                    deg_x = math.trunc(self.servos_mx*x+self.servos_bx)
                    deg_y = math.trunc(self.servos_mx*y+self.servos_by)
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

